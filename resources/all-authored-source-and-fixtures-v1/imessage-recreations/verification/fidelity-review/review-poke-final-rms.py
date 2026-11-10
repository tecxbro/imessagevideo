from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import shutil
import subprocess
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation

R = Path('/workspace/imessage-recreations')
D = R / 'verification/method-parity/04-poke/native-review'
D.mkdir(parents=True, exist_ok=True)
old = D / 'before7080-frame205'
old.mkdir(exist_ok=True)
for path in list(D.iterdir()):
    if path.is_file() and not (old / path.name).exists():
        shutil.copy2(path, old / path.name)
work = D / 'current7080'
work.mkdir(exist_ok=True)
frames = [932, 958]
meta = {m: json.loads((R / f'outputs/04-poke/{m}.mp4.render.json').read_text()) for m in ['gsap', 'motion-canvas']}
movies = {'source': R / 'references/04-poke/source.mp4', **{m: R / f'outputs/04-poke/{m}.mp4' for m in meta}}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
hashes = {key: sha(value) for key, value in movies.items()}
assert hashes['motion-canvas'] == '2423f1be2099458c548fc6ebc236c9b0518489189bdaf31da0ed7165da259a06'
def decode(item):
    key, movie = item
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-threads', '1', '-i', str(movie), '-vf', 'select=eq(n\\,932)+eq(n\\,958)', '-fps_mode', 'passthrough', '-frames:v', '2', str(work / f'{key}-%02d.png')], check=True)
with ThreadPoolExecutor(max_workers=3) as pool:
    list(pool.map(decode, movies.items()))
def native(method, frame):
    folder = Path(meta[method]['frameDirectory'])
    for name in [f'{frame:06d}.png', f'frame{frame:06d}.png']:
        path = folder / name
        if path.exists():
            return path
    raise FileNotFoundError(folder)
def pixels(path):
    return np.asarray(Image.open(path).convert('RGB')).astype(float)

rows = []
contact = Image.new('RGB', (2000, 430 * len(frames)), '#bcbcbc')
draw = ImageDraw.Draw(contact)
for index, frame in enumerate(frames, 1):
    paths = {
        'source': work / f'source-{index:02d}.png',
        'nativeG': native('gsap', frame),
        'nativeMC': native('motion-canvas', frame),
        'encodedG': work / f'gsap-{index:02d}.png',
        'encodedMC': work / f'motion-canvas-{index:02d}.png',
    }
    arrays = {key: pixels(value) for key, value in paths.items()}
    g = arrays['nativeG']
    gradient_x = np.max(np.abs(g[:, 1:] - g[:, :-1]), axis=2)
    gradient_y = np.max(np.abs(g[1:] - g[:-1]), axis=2)
    edges = np.zeros(g.shape[:2], dtype=bool)
    edges[:, 1:] |= gradient_x > 12
    edges[1:] |= gradient_y > 12
    near = binary_dilation(edges, iterations=3)
    native_error = np.abs(arrays['nativeMC'] - g)
    total = float(native_error.mean())
    pairs = [('nativeMC', 'nativeG'), ('encodedMC', 'encodedG'), ('encodedMC', 'nativeMC'), ('encodedG', 'nativeG'), ('nativeG', 'source'), ('nativeMC', 'source')]
    row = {'frame': frame, 'exactSourceIndex': frame, 'time': frame * 1001 / 30000, 'comparisons': {}}
    for left, right in pairs:
        delta = np.abs(arrays[left] - arrays[right])
        row['comparisons'][left + 'Vs' + right] = {'mae': float(delta.mean()), 'maxChannelDelta': int(delta.max()), 'changedPixels': int(np.any(delta, axis=2).sum())}
    row['nativeEdgeAttribution'] = {
        'definition': 'RGB adjacent-pixel gradient>12 in nativeG, dilated3pixels; contributions sum to full-frameMAE.',
        'nearEdgesContribution': float((native_error * near[:, :, None]).mean()),
        'interiorContribution': float((native_error * (~near)[:, :, None]).mean()),
        'nearEdgesShareOfAbsoluteError': float(native_error[near].sum() / native_error.sum()) if total else 1,
    }
    row['paths'] = {key: str(value.relative_to(R)) for key, value in paths.items()}
    rows.append(row)
    for col, key in enumerate(['source', 'nativeG', 'nativeMC', 'encodedMC']):
        image = Image.fromarray(arrays[key].astype('uint8'))
        image.thumbnail((495, 395))
        contact.paste(image, (col * 500, (index - 1) * 430 + 25))
        draw.text((col * 500 + 4, (index - 1) * 430 + 4), f'{frame} {key}', fill='black')
contact.save(work / 'contact.jpg', quality=96)
report = {'reference': '04-poke', 'sceneSHA256': meta['motion-canvas']['sceneSha256'], 'engineSHA256': meta['motion-canvas']['engineSha256'], 'currentMovieSHA256': hashes['motion-canvas'], 'gsapSHA256': hashes['gsap'], 'sourceSHA256': hashes['source'], 'fpsExact': '30000/1001', 'sourceMediaAndCachesChanged': False, 'rows': rows}
(work / 'measurements.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
