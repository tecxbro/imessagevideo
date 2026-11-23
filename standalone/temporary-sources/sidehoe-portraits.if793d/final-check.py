from pathlib import Path
from hashlib import sha256
import csv,json,sys
p=Path(sys.argv[1]).resolve()
def digest(path):
    with path.open('rb') as handle:
        return sha256(handle.read()).hexdigest()
def read(path):
    return json.loads(path.read_text())
prev=p.parent/'handoff-review'
src=Path('/Users/darshan/Downloads/sidehoe.mp4')
review=p/'review'
native=read(review/'native/report.json')
before=read(prev/'review/native/report.json')
hf=read(review/'hyperframes.json')
before_hf=read(prev/'review/hyperframes.json')
assert native['reference']['sha256']==digest(src)
assert native['candidate']['sha256']==digest(p/'candidate/sidehoe.mp4')
assert native['checks_sha256']==digest(p/'comparison-checks.json')
assert native['decode_completed']
assert hf['_meta']['version']=='0.9.77'
assert hf['reference']==str(src) and hf['yours']==str(p/'candidate/sidehoe.mp4'), hf['yours']
with (review/'native/frames.csv').open() as handle:
    rows=list(csv.DictReader(handle))
assert set(x.name for x in (review/'native/pairs').glob('*.jpg'))=={f'{n:06}.jpg' for n in range(778)}
assert len(rows)==778 and native['compared_frames']==778 and native['exact_clock']
for frame,row in enumerate(rows):
    assert int(row['reference_frame'])==int(row['candidate_frame'])==frame
    assert int(row['reference_pts'])==int(row['candidate_pts'])==2400*frame
    assert int(row['reference_end_pts_exclusive'])==int(row['candidate_end_pts_exclusive'])==2400*(frame+1)
assert sum(int(x['exact_changed_pixels'])==0 for x in rows)==native['pixel_equality']['identical_frames']
known_regions=('assistant-entrance-casing','assistant-entrance-sidehoe-pin','assistant-entrance-lower-rail-light','sofia-pullback-screen-and-keyboard','follow-moving-thread-and-keyboard','orbit-calendar-face','follow-pointer-approach','closing-profile-badge','personal-title-and-hearts',
'personal-title-registered-words','tile-face-refraction-and-numerals','follow-cursor-native-hull','profile-badge-contour-and-finish',
'sofia-push-screen-and-keyboard','send-controls-at-transition','calendar-bars-exposure','follow-keyboard-before-contact',
'portrait-cluster-disk-and-shell','profile-disks-and-expressions','profile-names-and-interest-chips')
regions = native['regions']
for name in known_regions:
    row=regions[name]
    print('region',name,{k:v for k,v in row.items() if k in ('verdict','pass','worst_mae','start','end','frames') and not isinstance(v,list)})
for asset in ('mix.wav','score.wav','foley.wav','events.json'):
    assert digest(p/'candidate/sound'/asset)==digest(prev/'candidate/sound'/asset)
print('Mean absolute RGB error',before['mean_abs_rgb'],native['mean_abs_rgb'])
print('SSIM',before_hf['ssim']['mean'],hf['ssim']['mean'])
print('Native equality',native['pixel_equality'])
print('HyperFrames',hf['pass'],hf['cuts'])
print('Worst frames',[(int(x['frame']),float(x['mean_abs_rgb'])) for x in sorted(rows,key=lambda t: float(t['mean_abs_rgb']),reverse=True)[:10]])
print('Last',rows[-1]['exact_changed_pixels'])
print('Candidate',native['candidate']['sha256'])
with (review/'focus/metrics.csv').open() as handle:
    focus={int(z['frame']):z for z in csv.DictReader(handle)}
for f in [190,217,218,221,225,226,227,240,253,255,270,271,275,281,286,287,316,401,706,777]:
    rec=focus[f]
    assert (review/'focus'/rec['image']).is_file()
    print(f,rec['feature'],rec['previous_mean_abs_rgb'],rec['revised_mean_abs_rgb'])
