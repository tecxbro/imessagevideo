from pathlib import Path
from PIL import Image
from hashlib import sha256
import csv
import json
import sys

dest=Path(sys.argv[1]).resolve()
review=dest/'review'
before=dest.parent/'assistant-reveal-review'
source=Path('/Users/darshan/Downloads/sidehoe.mp4')
scratch=Path(sys.argv[2])
def load(path):
    return json.loads(path.read_text())
def rows(path):
    with path.open() as handle:
        return list(csv.DictReader(handle))
def digest(path):
    return sha256(path.read_bytes()).hexdigest()

native=load(review/'native/report.json')
prior=load(before/'review/native/report.json')
assert native['reference']['sha256']==digest(source)==prior['reference']['sha256']
assert native['candidate']['sha256']==digest(dest/'candidate/sidehoe.mp4')
assert native['checks_sha256']==digest(dest/'comparison-checks.json')
assert native['decode_completed'] and native['exact_clock'] and native['verdict']=='FAIL'
assert (review/'status.txt').read_text()=='HyperFrames exit 0\nNative comparison exit 1\n'
current=rows(review/'native/frames.csv')
previous=rows(before/'review/native/frames.csv')
assert len(current)==len(previous)==778==native['compared_frames']
pairs=review/'native/pairs'
assert sorted(x.name for x in pairs.glob('*.jpg'))==[f'{n:06}.jpg' for n in range(778)]
for frame,row in enumerate(current):
    assert int(row['reference_frame'])==int(row['candidate_frame'])==frame
    assert int(row['reference_pts'])==int(row['candidate_pts'])==2400*frame
    assert int(row['reference_end_pts_exclusive'])==int(row['candidate_end_pts_exclusive'])==2400*(frame+1)
    with Image.open(pairs/f'{frame:06}.jpg') as image:
        image.verify()
identical=sum(int(row['exact_changed_pixels'])==0 for row in current)
assert identical==native['pixel_equality']['identical_frames']
for region in load(dest/'comparison-checks.json')['regions'][-8:]:
    name,start,end=region['id'],region['start'],region['end']
    r=native['regions'][name]
    assert r['frames']==[start,end] and r['expected_frames']==r['scanned_frames']==end-start+1
    assert (review/'native'/r['worst_pixel_difference']['crop']).is_file()
    print(name,r['worst_mae'],r['worst_mae_frame'])

hf=load(review/'hyperframes.json')
old_hf=load(before/'review/hyperframes.json')
assert hf['_meta']['version']=='0.9.77'
assert hf['reference']==str(source) and hf['yours']==str(dest/'candidate/sidehoe.mp4')
assert hf['pass'] and hf['cuts']['reference']==hf['cuts']['yours']==[5.36,6.4,8.52,16.04,27.72,30.8]
vendor=(scratch/'hyperframes-check.log').read_text().splitlines()
assert len(vendor)==202 and all(x.endswith(': OK') for x in vendor)
for name in ('mix.wav','score.wav','foley.wav','events.json'):
    assert digest(dest/'candidate/sound'/name)==digest(before/'candidate/sound'/name)
staged=load(review/'stage-metrics.json')
changed=staged['changed_frames']
assert len(changed)==46 and all(v['revised']<v['previous'] for v in staged['measurements'] if v['different'])
assert len(load(review/'editability.json'))==6

motion=load(review/'motion/motion-observations.json')
plan=load(review/'motion-plan.json')
assert motion['planSHA256']==digest(review/'motion-plan.json') and motion['sourceSHA256']==digest(source)
assert len(plan['tracks'])==len(motion['tracks'])==8
samples=0
for expected,track in zip(plan['tracks'],motion['tracks'],strict=True):
    assert track['actor']==expected['id'] and track['searchRect']==expected['rect']
    assert [s['frame'] for s in track['samples']]==list(range(expected['start'],expected['end']+1))
    for obs in track['samples']:
        samples+=1
        assert obs['pts']==2400*obs['frame'] and obs['pixels']>0
        path=review/'motion'/obs['evidence']['path']
        assert digest(path)==obs['evidence']['sha256']
        with Image.open(path) as image:
            assert image.size==tuple(expected['rect'][2:])
            image.verify()

reveal=rows(review/'reveal-timing.csv')
for version in ('Source','Revised'):
    for name,frame in (('no',648),('yes',650)):
        sampled=[r for r in reveal if r['version']==version and r['control']==name]
        assert [int(r['frame']) for r in sampled]==list(range(646,652))
        assert next(int(r['frame']) for r in sampled if int(r['detected pixels'])>=15)==frame

focus={int(row['frame']):row for row in rows(review/'focus/metrics.csv')}
wins=sum(float(current[f]['mean_abs_rgb'])<float(previous[f]['mean_abs_rgb']) for f in changed)
worsened=[f for f in changed if float(current[f]['mean_abs_rgb'])>float(previous[f]['mean_abs_rgb'])]
largest=max(range(778),key=lambda f:float(current[f]['mean_abs_rgb']))
error=float(current[largest]['mean_abs_rgb'])
ending=int(current[-1]['exact_changed_pixels'])
labels=((478,'Ring tile and foreground calendar cell'),(479,'Flame and 31 tile arrival'),
        (482,'First four-tile overlap'),(633,'Handset settles'),(648,'First No response'),
        (650,'First Yes response'),(658,'Handset case and keyboard'),
        (660,'First cropped push frame'),(667,'Lens deformation during the push'))
table=[]
for frame,label in labels:
    row=focus[frame]
    b,a=(float(row[k]) for k in ('previous_mean_abs_rgb','revised_mean_abs_rgb'))
    table.append(f"| {row['seconds']} s | [{label}](review/focus/{row['image']}) | {b:.2f} | {a:.2f} |")
comparison='\n'.join(table)
note=f" Error increased at {', '.join(f'f{f}' for f in worsened)}." if worsened else ''
report=f"""# Sidehoe follow-up handset and app-tile handoff

November 21, 2026. The [candidate MP4](candidate/sidehoe.mp4) was rendered
from a clean copy of the [editable project](project/README.md).

[Watch side by side with the reference](review/side-by-side.mp4) ·
[Inspect all 778 time-matched frames](review/native/index.html)

## What changed

- Registered the calendar fragments that overlap the ring tile at f478
  and fitted the arrival positions, focus and coverage of the other tiles
  through f482.
- Fitted the follow-up conversation, composer, keys, and handset bevel
  across f630–659. The No and Yes controls each have editable shape,
  lettering and emoji at their first visible frames.
- Measured the handset’s deformation through f660–670 and applied it
  before the renderer draws the cursor. The cursor is still an
  independently editable layer.

| Source time | Encoded comparison | Previous mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
{comparison}

Each row uses the same frame and crop from the three encoded files.
Native checks of the six frames around the reveals found the first
visible No at f648 (25.92 s) and the first Yes at f650 (26.00 s) in both
movies. The source No still has a sharper label and a smaller emoji
highlight at its first visible frame. The curvature of the keyboard
and composer still differs during the cropped camera push.
[Decoded reveal measurements](review/reveal-timing.csv) ·
[Crop measurements](review/focus/metrics.csv) ·
[Independent layer edit checks](review/editability.json)

The matched views for the requested screenshot examples still show
differences in the floating heart silhouettes and badge artwork.
[Title and hearts at 7.68 s](review/focus/f192-attached-active-title-and-hearts.png) ·
[Profile badge at 28.24 s](review/focus/f706-attached-profile-badge.png)

## Full export verdict

**Exact fidelity fails.** All 778 frames have identical presentation
timestamps and exclusive end times at 2000 × 2000 resolution. The mux
decodes cleanly. Mean full-film RGB error moved from
{prior['mean_abs_rgb']:.4f} to {native['mean_abs_rgb']:.4f}.
{identical} frames are pixel-identical. The last frame differs by
{ending} pixels. The largest remaining full-frame error is {error:.3f}
at f{largest} ({largest/25:.2f} s).
[Exact verdict](review/native/report.json) ·
[All frame measurements](review/native/frames.csv) ·
[Highest-error frame](review/native/pairs/{largest:06d}.jpg)

**HyperFrames 0.9.77 passed its visual thresholds.** It matched all six cuts.
Mean SSIM moved from {old_hf['ssim']['mean']:.4f} to {hf['ssim']['mean']:.4f}.
The pinned reviewer copy passed all 202 file checks.
[Official diff result](review/hyperframes.json) ·
[Ranked misses](review/hyperframes/worst.jpg) ·
[Reviewer copy and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

All 46 affected lossless frames improved and the other 732 matched the
previous render by hash. In the encoded MP4, {wins} of the 46 affected
frames improved.{note}
The 48 kHz stems, event map and AAC stream match the previous export
by hash. Motion supplied {samples} native source crops, verified by
timestamp, region and hash.
[Source observations](review/motion/motion-observations.json) ·
[Stage measurements](review/stage-metrics.json) ·
[Previous export review](../assistant-reveal-review/README.md)

Source SHA-256  
`{native['reference']['sha256']}`

Candidate SHA-256  
`{native['candidate']['sha256']}`

## Rerun the comparison

Set `SOURCE` to the locked reference and use a fresh output folder.

```sh
PYTHON=/path/to/render-environment/bin/python \\
HYPERFRAMES=/path/to/hyperframes \\
bash review.sh "$SOURCE" "$PWD/candidate/sidehoe.mp4" "$PWD/review-rerun"

/path/to/render-environment/bin/python focus.py \\
  "$SOURCE" ../assistant-reveal-review/candidate/sidehoe.mp4 \\
  candidate/sidehoe.mp4 review-rerun/focus
```
"""
(dest/'README.md').write_text(report)
print('mean',prior['mean_abs_rgb'],native['mean_abs_rgb'],'identical',identical,'worst',largest,error,'edited',wins,worsened)
print('hash',native['candidate']['sha256'])
