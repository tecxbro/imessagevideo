from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
import json
import hashlib

root = Path('/workspace/imessage-recreations')
review = root / 'verification/fidelity-review/05-flight'
frozen = root / 'outputs/05-linq/flight-document-review-05'
frames = [353, 355, 357, 366, 370, 372, 374, 377, 379, 387, 397, 398, 399, 413, 414]
rows = []
panels = []
(review / 'baseline').mkdir(exist_ok=True)
for frame in frames:
    capture = 'check-v4' if frame < 397 else 'check-v5'
    candidate = Image.open(review / capture / f'{frame/30:.3f}.png').convert('RGB')
    baseline = Image.open(root / 'outputs/05-linq/frames-gsap' / f'{frame:06d}.png').convert('RGB')
    baseline.save(review / 'baseline' / f'{frame}.png')
    source_path = review / ('source' if frame >= 355 else 'pre-source') / f'{frame-354 if frame >= 355 else frame-349:04d}.png'
    row = dict(frame=frame, checkpoint=capture, baseline_candidate_pixels_identical=np.array_equal(np.array(baseline), np.array(candidate)))
    if source_path.exists():
        source = Image.open(source_path).convert('RGB')
        source_pixels = np.array(source).astype(float)
        for label, picture in [('before', baseline), ('after', candidate)]:
            pixels = np.array(picture).astype(float)
            difference = np.abs(source_pixels - pixels)
            mask = np.any(source_pixels < 242, axis=2) | np.any(pixels < 242, axis=2)
            row[label + '_mae'] = float(difference.mean())
            row[label + '_foreground_mae'] = float(difference[mask].mean()) if mask.any() else 0
    else:
        source = Image.new('RGB', baseline.size, 'white')
        row['source_not_decoded_control_only'] = True
    rows.append(row)
    panel = Image.new('RGB', (1440, 390), 'white')
    drawing = ImageDraw.Draw(panel)
    for index, picture in enumerate([source, baseline, candidate]):
        picture.thumbnail((480, 360))
        panel.paste(picture, (index * 480, 24))
        drawing.text((index * 480 + 4, 3), f'{frame} ' + ['source', 'v10', 'reviewed flight'][index], fill='red')
    panels.append(panel)
sheet = Image.new('RGB', (1440, len(panels) * 390), 'white')
for index, panel in enumerate(panels):
    sheet.paste(panel, (0, index * 390))
sheet.save(review / 'comparison-v5.jpg', quality=95)
acceptance = dict(
    status='Scoped structural/timing improvement, remaining motion-shutter/AA residuals; not100%',
    scene=str(frozen / 'scene.json'),
    scene_sha256=hashlib.sha256((frozen / 'scene.json').read_bytes()).hexdigest(),
    helper=str(root / 'references/05-linq/apply-flight-document-review.py'),
    elements=str(frozen / 'flight-document-review-elements.json'),
    changed_native_frames=[[353, 397]],
    outside_proof='all-frame-scope-proof-v5.json',
    checkpoint_inheritance='checkpoint-inheritance-v4-v5.json',
    native_metrics=rows,
    coverage='13 decoded source/native samples plus398/414 control-only frames. First10v4 samples inherited via all45native-state SVG identity proof; final397–414 boundary checkpoints captured from frozen05.',
    limitations=[
        'Five355–359 bounded authentic app-panel color poses retain native source blend, including chat seen through panel; product UI bitmap internals explicit.',
        'Native continuous document camera, static top/sky/independent Basic/Economy cards,41native exposure samples, nonnegative measured shutter weights. Computed transparent color masks370–379 model linear-light exposure locally.',
        'Residual motion-blur/color/AA at370–379, backdrop approximation and static texture/source-compression differences remain.',
        'Accepted original rich4/backdrop398+ preserved because it is better at399/413. No full MP4 or independent adapter QA launched here.'
    ]
)
(review / 'acceptance.json').write_text(json.dumps(acceptance, indent=2))
(review / 'native-metrics-v5.json').write_text(json.dumps(rows, indent=2))
print(json.dumps(rows))
