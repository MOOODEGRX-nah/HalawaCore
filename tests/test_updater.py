import hashlib
import io
import json
import os
import stat
import tarfile
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from backend.errors import HalawaCoreError
from backend.updater import (Updater, RELEASE_API, REPOSITORY, select_release, unpack_portable,
                             replace_portable, sha256, probe, installation, trusted_url, version_tuple)


def metadata(version='0.7.0', name='HalawaCore-Linux-x64.tar.gz', data=b'archive'):
    return {'draft':False,'prerelease':False,'tag_name':'v'+version,'body':'Release notes',
            'assets':[{'name':name,'size':len(data),'digest':'sha256:'+hashlib.sha256(data).hexdigest(),
                       'state':'uploaded','browser_download_url':f'https://github.com/{REPOSITORY}/releases/download/v{version}/{name}'}]}


def archive_bytes(system='Linux', extras=None):
    files={'HalawaCore.exe' if system=='Windows' else 'HalawaCore':b'new binary', 'LICENSE.txt':b'license'}
    files.update(extras or {})
    stream=io.BytesIO()
    if system=='Windows':
        with zipfile.ZipFile(stream,'w') as bundle:
            for name,data in files.items():bundle.writestr(name,data)
    else:
        with tarfile.open(fileobj=stream,mode='w:gz') as bundle:
            for name,data in files.items():
                entry=tarfile.TarInfo(name);entry.size=len(data);bundle.addfile(entry,io.BytesIO(data))
    return stream.getvalue()


def runner(args,**kwargs):
    if '--version-file' in args:
        Path(args[-1]).write_text(json.dumps({'application':'HalawaCore','version':'0.7.0'}))
    return SimpleNamespace(returncode=0,stdout='halawacore-bin 0.7.0-1',stderr='')


class Client:
    def __init__(self,data,release=None):self.data=data;self.release=release or metadata(data=data);self.calls=[]
    def latest(self):self.calls.append(RELEASE_API);return self.release
    def download(self,url,destination,size,progress):
        self.calls.append(url);Path(destination).write_bytes(self.data);progress(len(self.data));return hashlib.sha256(self.data).hexdigest()


def updater(tmp_path,system='Linux',kind='portable',client=None,launch=runner):
    executable=tmp_path/('HalawaCore.exe' if system=='Windows' else 'HalawaCore')
    executable.write_bytes(b'old binary');executable.chmod(0o755)
    service=Updater(tmp_path/'data',executable,current_version='0.6.0',client=client or Client(archive_bytes()),
                    runner=launch,capability={'kind':kind,'supported':True,'reason':'test'})
    service.system=system
    return service


def test_no_network_at_startup_or_status_and_fixed_release_selection(tmp_path):
    service=updater(tmp_path)
    assert service.client.calls==[] and service.snapshot()['phase']=='idle'
    result=service.check()
    assert result['available'] and result['latest_version']=='0.7.0' and result['can_download']
    assert service.client.calls==[RELEASE_API]
    assert select_release(metadata('0.6.0'),'0.6.0','portable','Linux')['available'] is False
    assert select_release(metadata('0.5.0'),'0.6.0','portable','Linux')['available'] is False


@pytest.mark.parametrize('version',['../x','0.7','0.7.0-beta','01.7.0','v0.7.0','1.2.3/extra'])
def test_reject_invalid_versions(version):
    with pytest.raises(HalawaCoreError):version_tuple(version)


@pytest.mark.parametrize('damage',['draft','prerelease','bad_url','missing_digest','wrong_digest','oversize','duplicate'])
def test_unverified_or_unpublished_asset_cannot_download(damage):
    release=metadata()
    if damage in ('draft','prerelease'):release[damage]=True
    if damage=='bad_url':release['assets'][0]['browser_download_url']='https://evil.test/update'
    if damage=='missing_digest':del release['assets'][0]['digest']
    if damage=='wrong_digest':release['assets'][0]['digest']='sha256:bad'
    if damage=='oversize':release['assets'][0]['size']=1024**3
    if damage=='duplicate':release['assets'].append(release['assets'][0])
    if damage in ('draft','prerelease'):
        with pytest.raises(HalawaCoreError):select_release(release,'0.6.0','portable','Linux')
    else:assert select_release(release,'0.6.0','portable','Linux')['asset'] is None


@pytest.mark.parametrize('system',['Linux','Windows'])
def test_archive_checks_flat_files_and_modes(tmp_path,system):
    source=tmp_path/'archive';source.write_bytes(archive_bytes(system))
    hashes=unpack_portable(source,tmp_path/'stage',system)
    name='HalawaCore.exe' if system=='Windows' else 'HalawaCore'
    assert hashes[name]==hashlib.sha256(b'new binary').hexdigest()
    for bad in ['../outside','/absolute','folder/HalawaCore','unrelated.exe']:
        source.write_bytes(archive_bytes(system,{bad:b'bad'}))
        with pytest.raises(HalawaCoreError):unpack_portable(source,tmp_path/('stage-'+hashlib.md5(bad.encode()).hexdigest()),system)
    assert not (tmp_path/'outside').exists()


def test_archive_symlinks_and_missing_executable_are_rejected(tmp_path):
    source=tmp_path/'archive'
    with tarfile.open(source,'w:gz') as bundle:
        entry=tarfile.TarInfo('HalawaCore');entry.type=tarfile.SYMTYPE;entry.linkname='/tmp/wrong';bundle.addfile(entry)
    with pytest.raises(HalawaCoreError):unpack_portable(source,tmp_path/'a','Linux')
    with zipfile.ZipFile(source,'w') as bundle:
        entry=zipfile.ZipInfo('HalawaCore.exe');entry.external_attr=(stat.S_IFLNK|0o777)<<16;bundle.writestr(entry,'/wrong')
    with pytest.raises(HalawaCoreError):unpack_portable(source,tmp_path/'b','Windows')


def test_verified_portable_update_requires_job_and_confirmation_and_keeps_backup(tmp_path):
    service=updater(tmp_path)
    service.check();service.download();service.worker.join(10)
    assert service.phase=='ready'
    assert service.executable.read_bytes()==b'old binary'
    with pytest.raises(HalawaCoreError):service.install(service.job_id,False)
    with pytest.raises(HalawaCoreError):service.install('0'*32,True)
    service.install(service.job_id,True);service.worker.join(10)
    assert service.phase=='restart_required'
    assert service.executable.read_bytes()==b'new binary'
    assert Path(str(service.executable)+'.previous').read_bytes()==b'old binary'
    assert json.loads(service.result_path.read_text())['version']=='0.7.0'


@pytest.mark.parametrize('damage',['download','stage','installed'])
def test_tampered_payload_or_target_is_never_applied(tmp_path,damage):
    service=updater(tmp_path)
    if damage=='download':service.client.release['assets'][0]['digest']='sha256:'+'0'*64
    service.check();service.download();service.worker.join(10)
    if damage=='download':assert service.phase=='failed'
    elif damage=='stage':
        (service.prepared['job']/'staged/HalawaCore').write_bytes(b'tampered')
        service.install(service.job_id,True);service.worker.join(10)
        assert service.phase=='failed'
    else:
        service.executable.write_bytes(b'external update')
        with pytest.raises(HalawaCoreError):service.install(service.job_id,True)
    assert service.executable.read_bytes()==(b'external update' if damage=='installed' else b'old binary')


def test_portable_failure_restores_previously_replaced_docs(tmp_path,monkeypatch):
    target=tmp_path/'HalawaCore';target.write_bytes(b'old')
    license=tmp_path/'LICENSE.txt';license.write_bytes(b'old license')
    stage=tmp_path/'stage';stage.mkdir()
    (stage/'HalawaCore').write_bytes(b'new');(stage/'LICENSE.txt').write_bytes(b'new license')
    original_replace=os.replace
    def fail(source,destination):
        if Path(destination)==target:raise PermissionError('test failure')
        return original_replace(source,destination)
    monkeypatch.setattr(os,'replace',fail)
    with pytest.raises(PermissionError):replace_portable(target,stage,{name:sha256(stage/name) for name in ['HalawaCore','LICENSE.txt']},sha256(target))
    assert target.read_bytes()==b'old' and license.read_bytes()==b'old license'


def test_arch_update_uses_only_fixed_package_manager_command_and_handles_cancel(tmp_path):
    data=b'package';client=Client(data,metadata(name='HalawaCore-Arch-x64.pkg.tar.zst',data=data))
    launch=Mock(side_effect=runner)
    service=updater(tmp_path,kind='arch',client=client,launch=launch)
    service.check();service.download();service.worker.join(10);assert service.phase=='ready'
    launch.side_effect=lambda args,**kwargs:SimpleNamespace(returncode=126,stdout='',stderr='')
    service.install(service.job_id,True);service.worker.join(10)
    assert service.phase=='failed' and service.executable.read_bytes()==b'old binary'
    args=launch.call_args.args[0]
    assert args[:5]==['/usr/bin/pkexec','--disable-internal-agent','/usr/bin/pacman','-U','--noconfirm']
    assert len(args)==6 and not launch.call_args.kwargs.get('shell')


def test_version_probe_uses_private_report_for_windowed_executables(tmp_path):
    launch=Mock(side_effect=runner)
    probe(tmp_path/'app.exe','0.7.0',launch)
    assert '--version-file' in launch.call_args.args[0]
    assert launch.call_args.kwargs['env']['PYINSTALLER_RESET_ENVIRONMENT']=='1'
    with pytest.raises(HalawaCoreError):probe(tmp_path/'app.exe','0.8.0',launch)


def test_sources_and_unsupported_architectures_do_not_offer_installation():
    assert not installation(None)['supported']
    assert not installation(None,machine='aarch64')['supported']
    assert not trusted_url('http://github.com/file')
    assert not trusted_url('https://github.com.evil.test/file')
    assert not trusted_url('https://user:password@github.com/file')
    assert trusted_url('https://release-assets.githubusercontent.com/asset?token=test')


def test_frozen_linux_uses_target_os_ca_bundle_not_ubuntu_build_path(monkeypatch):
    import backend.updater as module
    monkeypatch.delenv('SSL_CERT_FILE',raising=False);monkeypatch.delenv('SSL_CERT_DIR',raising=False)
    monkeypatch.setattr(module.platform,'system',lambda:'Linux')
    monkeypatch.setattr(module.Path,'is_file',lambda path:path.as_posix()=='/etc/ssl/cert.pem')
    create=Mock();monkeypatch.setattr(module.ssl,'create_default_context',create)
    module.system_ssl_context()
    create.assert_called_once_with(cafile='/etc/ssl/cert.pem')


def test_explicit_ca_settings_are_honored_and_windows_keeps_system_store(monkeypatch):
    import backend.updater as module
    create=Mock();monkeypatch.setattr(module.ssl,'create_default_context',create)
    monkeypatch.setenv('SSL_CERT_FILE','/custom/ca.pem');monkeypatch.setenv('SSL_CERT_DIR','/custom/certs')
    module.system_ssl_context();create.assert_called_once_with(cafile='/custom/ca.pem',capath='/custom/certs')
    create.reset_mock();monkeypatch.delenv('SSL_CERT_FILE');monkeypatch.delenv('SSL_CERT_DIR')
    monkeypatch.setattr(module.platform,'system',lambda:'Windows')
    module.system_ssl_context();create.assert_called_once_with()


def test_update_tls_context_keeps_certificate_and_hostname_validation():
    import ssl
    from backend.updater import system_ssl_context
    context=system_ssl_context()
    assert context.check_hostname is True
    assert context.verify_mode==ssl.CERT_REQUIRED
