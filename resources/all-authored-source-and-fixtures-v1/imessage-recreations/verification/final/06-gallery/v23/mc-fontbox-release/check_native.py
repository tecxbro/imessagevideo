from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image

R = Path('/workspace/imessage-recreations')
D = Path(__file__).resolve().parent
EXPECTED_SCENE = 'abc87b6e69314e5df3ef75a81efd216011fa1604872aec66c1eb2a39f69658b2'
EXPECTED_ENGINE = '383edd8f560d13f794d46cbca0daa4eddfc58774a41b9e2a295b95d757d33edb'
O = R / 'outputs/06-gallery'
old = O / 'iterations/before-mc-text-top-metrics'
preservation = json.loads((old / 'preservation.json').read_text())
metadata = json.loads((O / 'motion-canvas.mp4.render.json').read_text())
assert metadata.get('sceneSHA256', metadata.get('sceneSha256')) == EXPECTED_SCENE
assert metadata.get('engineSha256', metadata.get('engineSHA256')) == EXPECTED_ENGINE
assert metadata['frames'] == 1483
cache = Path(metadata['frameDirectory'])
scope = set(range(108, 240)) | set(range(1050, 1151))
memo = {}
def sha(path):
    stat = path.stat()
    key = (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns)
    if key not in memo:
        memo[key] = hashlib.sha256(path.read_bytes()).hexdigest()
    return memo[key]

changed = []
for row in preservation['frames']:
    frame = row['frame']
    assert sha(old / 'frames-mc' / f'{frame:06d}.png') == row['sha256']
    digest = sha(cache / f'{frame:06d}.png')
    if digest != row['sha256']:
        assert frame in scope, frame
        changed.append(frame)
for row in preservation['files']:
    assert sha(R / row['preserved']) == row['sha256'], row['preserved']

checks = []
for frame in [1067, 1106, 552]:
    native = np.asarray(Image.open(cache / f'{frame:06d}.png').convert('RGB'))
    prototype = np.asarray(Image.open(R / f'verification/final/06-gallery/v23/text-metric-diagnosis/actual/{frame}-native-dom-prototype.png').convert('RGB'))
    delta = np.abs(native.astype(float) - prototype.astype(float))
    assert not delta.any(), frame
    gsap = np.asarray(Image.open(O / f'frames-gsap/{frame:06d}.png').convert('RGB'))
    difference = np.abs(native.astype(float) - gsap.astype(float))
    checks.append({'frame': frame, 'nativeVsApprovedPrototype': {'mae': float(delta.mean()), 'changedPixels': int(np.any(delta, axis=2).sum())}, 'nativeVsGSAP': {'mae': float(difference.mean()), 'changedPixels': int(np.any(difference, axis=2).sum())}})

report = {
    'status': 'PASS', 'sceneSHA256': EXPECTED_SCENE,
    'actualEngineSHA256': EXPECTED_ENGINE,
    'requestedRanges': [[108, 239], [1050, 1150]], 'requestedFrames': 233,
    'changedFrames': changed, 'changedCount': len(changed),
    'outsideCandidateHashIdentical': 1250,
    'all1483PriorPicturesPreserved': True, 'priorMasterSidecarAudioPreserved': True,
    'preservationManifest': str((old / 'preservation.json').relative_to(R)),
    'prototypeChecks': checks,
    'qualification': 'Conservative active actor ranges include possible offscreen or occluded nodes. Source23 is unchanged. Native pixel parity with approved prototype is separate from source fidelity and encoded SSIM.',
}
(D / 'native-check.json').write_text(json.dumps(report, indent=2))
print(json.dumps({key: report[key] for key in ['status', 'actualEngineSHA256', 'requestedFrames', 'changedCount', 'outsideCandidateHashIdentical']}))
