import json
import os
import uuid
from pathlib import Path

from .errors import HalawaCoreError


class ProfileManager:
    def __init__(self, data_dir):
        self.base = Path(data_dir) / 'profiles'
        self.base.mkdir(parents=True, exist_ok=True, mode=0o700)

    def listing(self):
        result = []
        for path in self.base.glob('*.json'):
            try:
                result.append(json.loads(path.read_text()))
            except (OSError, ValueError):
                continue
        return result

    def save(self, profile):
        ident = uuid.uuid4().hex
        row = {'id': ident, **profile}
        path = self.base / (ident + '.json')
        with path.open('x') as out:
            os.chmod(path, 0o600)
            json.dump(row, out)
        return row

    def delete(self, ident):
        try:
            if uuid.UUID(ident).hex != ident:
                raise ValueError
        except ValueError as exc:
            raise HalawaCoreError('Invalid profile identifier.') from exc
        try:
            (self.base / (ident + '.json')).unlink()
        except FileNotFoundError as exc:
            raise HalawaCoreError('Profile no longer exists.', 404) from exc
