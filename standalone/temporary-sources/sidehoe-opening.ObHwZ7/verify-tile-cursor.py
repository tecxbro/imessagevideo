from pathlib import Path
from hashlib import sha256
from PIL import Image
import csv
import json
import sys

new = Path(sys.argv[1]).resolve()
old = new.parent / 'inbox-and-lens-review'
intermediate = new.parent / 'opening-and-sofia-review'
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
phase_2 = read(intermediate / 'review/native/report.json')
print('Intermediate whole-film error',phase_2['mean_abs_rgb'])
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
for name in ('000000.jpg', '000336.jpg', '000613.jpg', '000619.jpg', '000659.jpg', '000660.jpg', '000675.jpg', '000694.jpg', '000777.jpg'):
    with Image.open(review / 'native/pairs' / name) as image:
        image.verify()
assert sum(int(row['exact_changed_pixels']) == 0 for row in rows) == native['pixel_equality']['identical_frames']
hf = read(review / 'hyperframes.json')
old_hf = read(old / 'review/hyperframes.json')
assert hf['_meta']['version'] == '0.9.77'
assert hf['reference'] == str(reference) and hf['yours'] == str(new / 'candidate/sidehoe.mp4')
assert hf['cuts']['reference'] == hf['cuts']['yours']
print('HyperFrames overall verdict',hf['pass'])
assert hf['cuts']['reference'] == [5.36, 6.4, 8.52, 16.04, 27.72, 30.8]
for asset in ('mix.wav', 'score.wav', 'foley.wav', 'events.json'):
    assert digest(new / 'candidate/sound' / asset) == digest(old / 'candidate/sound' / asset)
assert (review / 'status.txt').read_text() == 'HyperFrames exit 0\nNative comparison exit 1\n'
focus = {int(z['frame']): z for z in read_csv(review / 'focus/metrics.csv')}
for f in (0,2,5,9,10,135,136,137,190,313,314,318,319,321,325,328,329,532,613,614,615,617,618,619,620,627,675,676,685,694,695,706,777):
    entry = focus[f]
    assert (review / 'focus' / entry['image']).is_file()
    print(f, entry['feature'], entry['previous_mean_abs_rgb'], entry['revised_mean_abs_rgb'])
print('Mean absolute RGB error', before['mean_abs_rgb'], native['mean_abs_rgb'])
print('SSIM', old_hf['ssim']['mean'], hf['ssim']['mean'])
print('Native equality', native['pixel_equality'])
print('Prior native equality', before['pixel_equality'])
print('Worst frames', [(int(x['frame']), float(x['mean_abs_rgb'])) for x in sorted(rows, key=lambda t: float(t['mean_abs_rgb']), reverse=True)[:10]])
print('Last-frame pixel difference', rows[-1]['exact_changed_pixels'])
stage1 = read(review/'stage-metrics.json')
stage2 = read(review/'tile-and-cursor-stage-metrics.json')
changes1=set(stage1['changed_frames'])
changes2={m['frame'] for m in stage2 if m['changed_pixels']}
changed=sorted(changes1|changes2)
assert len(changes1)==27 and len(changes2)==29 and len(changed)==56
assert all(m['full'][1]<m['full'][0] and m['local'][1]<m['local'][0]
           for m in stage2 if m['changed_pixels'])
print('Stage ranges', sorted(changes1), sorted(changes2))
improved=[f for f in changed if float(rows[f]['mean_abs_rgb'])<float(past_rows[f]['mean_abs_rgb'])]
print('Encoded improvement for',len(improved),'of',len(changed),'edited frames.')
print('Edited frames without improvement',[(f,rows[f]['mean_abs_rgb'],past_rows[f]['mean_abs_rgb']) for f in changed if f not in improved])
print('Candidate', native['candidate']['sha256'])
for region in ('opening-first-status-streaks','opening-pinned-contacts-and-note','opening-first-two-transcript-rows','sofia-entrance-measured-glass','sofia-keyboard-and-footer','handset-reveal-upper-light','handset-reveal-lower-light','tile-numerals-and-material-through-exit','follow-cursor-contact-core','follow-cursor-native-hull'):
    row = native['regions'][region]
    assert row['scanned_frames'] == row['expected_frames'] == row['frames'][1] - row['frames'][0] + 1
    print(region, row['worst_mae'], row['worst_mae_frame'], row['failed_spans'])
    assert (review/'native'/row['worst_pixel_difference']['crop']).is_file()

for f in (154,156,158,159,160,161,190,332,336,529,531,532,533,535,544,618,623,624,625,626,627,628,629,630,631,660,675,694,706,777):
    print('Decoded frame', f, past_rows[f]['mean_abs_rgb'], rows[f]['mean_abs_rgb'])

motion_dir=review/'motion'
m=read(motion_dir/'motion-observations.json')
assert m['sourceSHA256']==digest(reference)
assert m['planSHA256']==digest(review/'motion-plan.json')
plan=read(review/'motion-plan.json')['tracks']
assert len(m['tracks'])==len(plan)==7
counts=[]
for track, requested in zip(m['tracks'],plan,strict=True):
    assert track['actor']==requested['id']
    assert track['searchRect']==requested['rect']
    assert [s['frame'] for s in track['samples']]==list(range(requested['start'],requested['end']+1))
    count=0
    for sample in track['samples']:
        f=sample['frame']
        i=motion_dir/sample['evidence']['path']
        assert digest(i)==sample['evidence']['sha256']
        assert sample['pts']==f*2400
        with Image.open(i) as crop:
            assert crop.size==tuple(track['searchRect'][2:])
        count += bool(sample['pixels'])
    counts.append((track['actor'],count,len(track['samples'])))
print('Motion observations present',counts)
print('Final focal differences',[(f,focus[f]['revised_mean_abs_rgb']) for f in (136,190,319,619,675,685,694,706)])
