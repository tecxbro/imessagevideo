"""Restore the pinned director input from the direction branch, without merging."""
import hashlib
from pathlib import Path
import subprocess

BASE=Path(__file__).resolve().parents[1]
expected='9dc4a812480d778c4b453f1eeb8d87e19569683ea2f4d78e8015b9f2f9952d9e'
data=subprocess.check_output(['git','show','bddbbe6:projects/devin-direction-checkin-v1/renders/v3-final.mp4'])
if hashlib.sha256(data).hexdigest()!=expected:
    raise ValueError('Director branch input differs from pinned attachment')
path=BASE/'v3-final.mp4'
if path.exists():
    if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
        raise ValueError('Refusing to overwrite a different local director input')
else:
    path.write_bytes(data)
print(f'Verified/restored director input from bddbbe6: {expected}')
