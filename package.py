"""Build a portable source release; never include runtime data or environments."""
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXCLUDE = {'.venv', '__pycache__', '.pytest_cache', '.git', 'data', 'dist', 'build', 'node_modules'}


def build():
    target = ROOT / 'dist/halawacore-0.2.0.tar.gz'
    target.parent.mkdir(exist_ok=True)
    with tarfile.open(target, 'w:gz') as archive:
        for source in sorted(ROOT.rglob('*')):
            relative = source.relative_to(ROOT)
            if source.is_file() and not EXCLUDE.intersection(relative.parts) and source.suffix != '.pyc':
                archive.add(source, arcname=Path('halawacore-0.2.0') / relative, recursive=False)
    return target


if __name__ == '__main__':
    print(build())
