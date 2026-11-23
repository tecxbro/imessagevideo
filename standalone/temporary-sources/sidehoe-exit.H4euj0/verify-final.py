from pathlib import Path
from hashlib import sha256
from PIL import Image
import csv
import json
import sys

new = Path(sys.argv[1]).resolve()
old = new.parent / 'inbox-review'
reference = Path('/Users/darshan/Downloads/sidehoe.mp4')
review = new / 'review'

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text())

def read_csv(path):
    with path.open() as handle:
        return list(csv.DictReader(handle))

native = read(review / 'native/report.json')
before = read(old / 'review/native/report.json')
assert native['reference']['sha256'] == digest(reference)
assert native['candidate']['sha256'] == digest(new / 'candidate/sidehoe.mp4')
assert native['checks_sha256'] == digest(new / 'comparison-checks.json')
assert native['decode_completed']
rows = read_csv(review / 'native/frames.csv')
past_rows = read_csv(old / 'review/native/frames.csv')
assert len(rows) == native['compared_frames'] == 778
assert native['exact_clock']
for frame, row in enumerate(rows):
    assert int(row['reference_frame']) == int(row['candidate_frame']) == frame
    assert int(row['reference_pts']) == int(row['candidate_pts']) == 2400 * frame
    assert int(row['reference_end_pts_exclusive']) == int(row['candidate_end_pts_exclusive']) == 2400 * (frame + 1)
pairs = {x.name for x in (review / 'native/pairs').glob('*.jpg')}
assert pairs == {f'{n:06}.jpg' for n in range(778)}
for name in ('000000.jpg', '000316.jpg', '000659.jpg', '000777.jpg'):
    with Image.open(review / 'native/pairs' / name) as image:
        image.verify()
assert sum(int(row['exact_changed_pixels']) == 0 for row in rows) == native['pixel_equality']['identical_frames']
hf = read(review / 'hyperframes.json')
old_hf = read(old / 'review/hyperframes.json')
assert hf['_meta']['version'] == '0.9.77'
assert hf['reference'] == str(reference) and hf['yours'] == str(new / 'candidate/sidehoe.mp4')
assert hf['pass'] and hf['cuts']['reference'] == hf['cuts']['yours']
assert hf['cuts']['reference'] == [5.36, 6.4, 8.52, 16.04, 27.72, 30.8]
for asset in ('mix.wav', 'score.wav', 'foley.wav', 'events.json'):
    assert digest(new / 'candidate/sound' / asset) == digest(old / 'candidate/sound' / asset)
assert (review / 'status.txt').read_text() == 'HyperFrames exit 0\nNative comparison exit 1\n'
focus = {int(z['frame']): z for z in read_csv(review / 'focus/metrics.csv')}
for f in (190, 270, 288, 300, 312, 613, 675, 694, 695, 706, 777):
    entry = focus[f]
    assert (review / 'focus' / entry['image']).is_file()
    print(f, entry['feature'], entry['previous_mean_abs_rgb'], entry['revised_mean_abs_rgb'])
print('Mean absolute RGB error', before['mean_abs_rgb'], native['mean_abs_rgb'])
print('SSIM', old_hf['ssim']['mean'], hf['ssim']['mean'])
print('Native equality', native['pixel_equality'])
print('Prior native equality', before['pixel_equality'])
print('Worst frames', [(int(x['frame']), float(x['mean_abs_rgb'])) for x in sorted(rows, key=lambda t: float(t['mean_abs_rgb']), reverse=True)[:10]])
print('Last-frame pixel difference', rows[-1]['exact_changed_pixels'])
changed=[*range(267,271), *range(287,313), 694, 695]
improved=[f for f in changed if float(rows[f]['mean_abs_rgb'])<float(past_rows[f]['mean_abs_rgb'])]
print('Encoded improvement for',len(improved),'of',len(changed),'edited frames.')
print('Edited frames without improvement',[(f,rows[f]['mean_abs_rgb'],past_rows[f]['mean_abs_rgb']) for f in changed if f not in improved])
print('Candidate', native['candidate']['sha256'])
for region in ('profiles-before-title-settles','profiles-across-push','profiles-ella-fade','follow-exit-display-animation','follow-exit-cursor-native'):
    row = native['regions'][region]
    assert row['scanned_frames'] == row['expected_frames'] == row['frames'][1] - row['frames'][0] + 1
    print(region, row['worst_mae'], row['worst_mae_frame'], row['failed_spans'])
    assert (review/'native'/row['worst_pixel_difference']['crop']).is_file()

for f in (270, 287, 288, 300, 312, 613, 675, 693, 694, 695, 696, 706, 777):
    print('Decoded frame', f, past_rows[f]['mean_abs_rgb'], rows[f]['mean_abs_rgb'])
