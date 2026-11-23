from pathlib import Path
from PIL import Image
from hashlib import sha256
import csv
import json
import sys

dest=Path(sys.argv[1]).resolve()
review=dest/'review'
before=dest.parent/'assistant-detail-review'
source=Path('/Users/darshan/Downloads/sidehoe.mp4')
p=Path(sys.argv[2])
def read(path):
    return json.loads(path.read_text())
def rows(path):
    with path.open() as handle:
        return list(csv.DictReader(handle))
def digest(path):
    return sha256(path.read_bytes()).hexdigest()

native=read(review/'native/report.json')
prior=read(before/'review/native/report.json')
assert native['reference']['sha256']==digest(source)==prior['reference']['sha256']
assert native['candidate']['sha256']==digest(dest/'candidate/sidehoe.mp4')
assert native['checks_sha256']==digest(dest/'comparison-checks.json')
assert native['decode_completed'] and native['exact_clock'] and native['verdict']=='FAIL'
assert (review/'status.txt').read_text()=='HyperFrames exit 0\nNative comparison exit 1\n'
now=rows(review/'native/frames.csv')
prev=rows(before/'review/native/frames.csv')
assert len(now)==len(prev)==778==native['compared_frames']
pairs=review/'native/pairs'
assert sorted(x.name for x in pairs.glob('*.jpg'))==[f'{n:06}.jpg' for n in range(778)]
for index,row in enumerate(now):
    assert int(row['reference_frame'])==int(row['candidate_frame'])==index
    assert int(row['reference_pts'])==int(row['candidate_pts'])==index*2400
    assert int(row['reference_end_pts_exclusive'])==int(row['candidate_end_pts_exclusive'])==(index+1)*2400
    with Image.open(pairs/f'{index:06}.jpg') as image:
        image.verify()
identical=sum(int(row['exact_changed_pixels'])==0 for row in now)
assert identical==native['pixel_equality']['identical_frames']
for region in read(dest/'comparison-checks.json')['regions'][-8:]:
    label,start,end=region['id'],region['start'],region['end']
    r=native['regions'][label]
    assert r['frames']==[start,end] and r['expected_frames']==r['scanned_frames']==end-start+1
    assert (review/'native'/r['worst_pixel_difference']['crop']).is_file()
    print(label,r['worst_mae'],r['worst_mae_frame'])

hf=read(review/'hyperframes.json')
old_hf=read(before/'review/hyperframes.json')
assert hf['_meta']['version']=='0.9.77'
assert hf['reference']==str(source) and hf['yours']==str(dest/'candidate/sidehoe.mp4')
assert hf['pass'] and hf['cuts']['reference']==hf['cuts']['yours']==[5.36,6.4,8.52,16.04,27.72,30.8]
vendor=(p/'hyperframes-check.log').read_text().splitlines()
assert len(vendor)==202 and all(l.endswith(': OK') for l in vendor)
for name in ('mix.wav','score.wav','foley.wav','events.json'):
    assert digest(dest/'candidate/sound'/name)==digest(before/'candidate/sound'/name)
yes=rows(review/'yes-contact.csv')
for version in ('Source','Revised'):
    selection=[r for r in yes if r['version']==version]
    assert [int(r['frame']) for r in selection]==list(range(673,691))
    assert next(int(r['frame']) for r in selection if r['gap pixels']=='0')==675
    assert selection[1]['gap pixels']=='2'

plan=read(review/'motion-plan.json')
motion=read(review/'motion/motion-observations.json')
assert motion['planSHA256']==digest(review/'motion-plan.json')
assert motion['sourceSHA256']==digest(source)
assert len(plan['tracks'])==len(motion['tracks'])==6
samples=0
for expected,track in zip(plan['tracks'],motion['tracks'],strict=True):
    assert track['actor']==expected['id']
    assert track['searchRect']==expected['rect']
    track_frames=[s['frame'] for s in track['samples']]
    assert track_frames==list(range(expected['start'],expected['end']+1))
    for obs in track['samples']:
        samples+=1
        assert obs['pts']==obs['frame']*2400 and obs['pixels']>0
        evidence=review/'motion'/obs['evidence']['path']
        assert obs['evidence']['sha256']==digest(evidence)
        with Image.open(evidence) as image:
            assert image.size==tuple(expected['rect'][2:])
            image.verify()

staged=read(review/'stage-metrics.json')
edited=staged['changed_frames']
assert len(edited)==42
assert all(r['revised']<r['previous'] for r in staged['measurements'] if r['different'])
dif={f:float(now[f]['mean_abs_rgb'])-float(prev[f]['mean_abs_rgb']) for f in edited}
wins=sum(delta<0 for delta in dif.values())
reg=[f for f,delta in dif.items() if delta>0]
focus={int(r['frame']):r for r in rows(review/'focus/metrics.csv')}
worst=max(now,key=lambda row:float(row['mean_abs_rgb']))
f_worst=int(worst['reference_frame'])
worst_err=float(worst['mean_abs_rgb'])
final_changed=int(now[-1]['exact_changed_pixels'])
assert len(read(review/'editability.json'))==5
lines=[]
for f,label in ((324,'Sofia’s handset during the push'),(658,'Follow-up casing and header'),
                (674,'Cursor just before contact'),(675,'First Yes contact'),
                (681,'Held Yes close-up'),(685,'First press feedback'),(693,'Withdrawal')):
    r=focus[f]
    b,a=float(r['previous_mean_abs_rgb']),float(r['revised_mean_abs_rgb'])
    text=f"[{label}](review/focus/{r['image']})"
    lines.append(f"| {r['seconds']} s | {text} | {b:.2f} | {a:.2f} |")
frames='\n'.join(lines)
encoded_note=f" Error increased at {', '.join(f'f{f}' for f in reg)}." if reg else ""
report=f"""# Sidehoe handset and cursor close-up review

The November 21, 2026 [candidate MP4](candidate/sidehoe.mp4) was rendered from
a clean copy of the [editable project](project/README.md).

[Watch the source and candidate side by side](review/side-by-side.mp4) ·
[Step through all 778 time-matched pairs](review/native/index.html)

## Changes in the rendered film

- Registered Sofia’s casing and glass through the push at f319–329, then
  refined the follow-up handset’s header, corners and composer at f650–659.
- Rebuilt the follow-up’s side buttons and rail reflections as independent
  stage controls. Fitted the outgoing message and gray reply, composer,
  two visible keyboard rows, response chips and inset emoji through contact.
- Adjusted the cursor silhouette, position and blur during the hold.
  Its first contact with Yes is f675 (27.00 s) in both decoded exports.
  Both show a two-pixel gap on the preceding frame. The tap remains at
  sample 1,296,000 on the 48 kHz clock.

[Cursor and target measurements](review/yes-contact.csv) ·
[Independent layer edit checks](review/editability.json) ·
[Verified Motion source observations]({{motion}})

| Source time | Encoded comparison | Previous mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
{frames}

Each row uses the same frame and native crop from the three encoded
files. At f681 the full-frame error moved from
{float(prev[681]['mean_abs_rgb']):.3f} to {float(now[681]['mean_abs_rgb']):.3f}.
The first gray reply’s weight and focus, the key shadows, and the bottom
edge of the response are still visibly different.
[Crop bounds and scores](review/focus/metrics.csv) ·
[Previous candidate](../assistant-detail-review/README.md)

## Full export verdict

**Exact fidelity fails.** All 778 frames match in their native 2000 × 2000
dimensions, presentation timestamps and exclusive end times. The mux
decodes cleanly. Mean full-film RGB error moved from
{prior['mean_abs_rgb']:.4f} to {native['mean_abs_rgb']:.4f}.
{identical} frames are pixel-identical. The final frame differs by
{final_changed} pixels, each by one grayscale level. The greatest remaining
full-frame error is {worst_err:.3f} at f{f_worst} ({f_worst/25:.2f} s).
[Exact verdict](review/native/report.json) ·
[Full frame measurements](review/native/frames.csv) ·
[Highest-error matched frame](review/native/pairs/{f_worst:06d}.jpg)

**HyperFrames 0.9.77 passed its visual thresholds.** It matched all six
cuts and its mean SSIM moved from {old_hf['ssim']['mean']:.4f}
to {hf['ssim']['mean']:.4f}. The official reviewer copy passed all 202
file checks.
[HyperFrames report](review/hyperframes.json) ·
[Ranked misses](review/hyperframes/worst.jpg) ·
[Pinned reviewer and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

All 42 modified lossless frames improved. The other 736 lossless
frames are byte-identical to the prior render. In the final decoded MP4,
{wins} of 42 modified frames improved.{encoded_note}
The 48 kHz stems, event map and AAC stream match the previous candidate
by hash. The Motion review verifies {samples} native source crops by
timestamp, region and SHA-256.
[Lossless render comparison](review/stage-metrics.json)

Source SHA-256  
`{native['reference']['sha256']}`

Candidate SHA-256  
`{native['candidate']['sha256']}`

## Rerun the comparison

Set `SOURCE` to the locked reference and use a fresh review output directory.

```sh
PYTHON=/path/to/render-environment/bin/python \\
HYPERFRAMES=/path/to/hyperframes \\
bash review.sh "$SOURCE" "$PWD/candidate/sidehoe.mp4" "$PWD/review-rerun"

/path/to/render-environment/bin/python focus.py \\
  "$SOURCE" ../assistant-detail-review/candidate/sidehoe.mp4 \\
  candidate/sidehoe.mp4 review-rerun/focus
```
""".format(motion="review/motion/motion-observations.json")
(dest/'README.md').write_text(report)
print('mean',prior['mean_abs_rgb'],native['mean_abs_rgb'],'identical',identical,'worst',f_worst,worst_err,'edited',wins,reg)
print('hash',native['candidate']['sha256'])
