from pathlib import Path
from PIL import Image
from hashlib import sha256
import csv
import json
import sys

dest=Path(sys.argv[1]).resolve()
review=dest/'review'
before=dest.parent/'refraction-review'
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
for region in load(dest/'comparison-checks.json')['regions'][-7:]:
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
assert changed==[*range(153,162),*range(188,197),*range(701,712)] and all(v['revised']<v['previous'] for v in staged['measurements'] if v['different'])
assert len(load(review/'editability.json'))==6

motion=load(review/'motion/motion-observations.json')
plan=load(review/'motion-plan.json')
assert motion['planSHA256']==digest(review/'motion-plan.json') and motion['sourceSHA256']==digest(source)
assert len(plan['tracks'])==len(motion['tracks'])==7
samples=0
for expected,track in zip(plan['tracks'],motion['tracks'],strict=True):
    assert track['actor']==expected['id'] and track['searchRect']==expected['rect']
    assert [s['frame'] for s in track['samples']]==list(range(expected['start'],expected['end']+1))
    for obs in track['samples']:
        samples+=1
        assert obs['pts']==2400*obs['frame']
        assert obs['pixels']>0,(track['actor'],obs['frame'])
        path=review/'motion'/obs['evidence']['path']
        assert digest(path)==obs['evidence']['sha256']
        with Image.open(path) as image:
            assert image.size==tuple(expected['rect'][2:])
            image.verify()

focus={int(row['frame']):row for row in rows(review/'focus/metrics.csv')}
wins=sum(float(current[f]['mean_abs_rgb'])<float(previous[f]['mean_abs_rgb']) for f in changed)
worsened=[f for f in changed if float(current[f]['mean_abs_rgb'])>float(previous[f]['mean_abs_rgb'])]
largest=max(range(778),key=lambda f:float(current[f]['mean_abs_rgb']))
error=float(current[largest]['mean_abs_rgb'])
ending=int(current[-1]['exact_changed_pixels'])
assert samples==65
assert (review/'hyperframes/worst.jpg').stat().st_size>5000
assert (review/'side-by-side.mp4').stat().st_size>5000
assert hf['cuts']['reference']==hf['cuts']['yours']

temporal=rows(review/'temporal-metrics.csv')
assert len(temporal)==32
assert all(int(r['frame'])==int(r['previous_frame'])+1 for r in temporal)
temporal_worse=[int(r['frame']) for r in temporal
                if float(r['previous_temporal_rgb_error'])<float(r['revised_temporal_rgb_error'])]
assert temporal_worse==[153,712]
aac=(scratch/'aac-sha.txt').read_text().splitlines()
assert len(aac)==2 and aac[0]==aac[1] and aac[0].startswith('SHA256=')

labels=((153,'First revised case frame'),(158,'Moving shoulders and status'),
        (159,'Status streaks before the cut'),(160,'Curved rim and status at 6.40 s'),
        (161,'Last frame before the cut'),(192,'Title and floating hearts'),
        (704,'Badge shoulders in motion'),(706,'Profile badge'))
table=[]
for frame,label in labels:
    row=focus[frame]
    old,new=(float(row[k]) for k in ('previous_mean_abs_rgb','revised_mean_abs_rgb'))
    assert new<old,(frame,old,new)
    table.append(f"| {row['seconds']} s | [{label}](review/focus/{row['image']}) | {old:.2f} | {new:.2f} |")
comparison='\n'.join(table)
encoded_note=''
if worsened:
    encoded_note=f" Full-frame error rose at {', '.join(f'f{i}' for i in worsened)}."
report=f"""# Sidehoe handset exit, title hearts, and badge outline

November 21, 2026. The [candidate MP4](candidate/sidehoe.mp4) was rendered
from a clean copy of the [editable project](project/README.md).

[Watch the source and recreation side by side](review/side-by-side.mp4) ·
[Inspect all 778 time-matched frames](review/native/index.html)

- Rebuilt the handset exit around separate metal and glass contours.
  The bevel reflection follows the curved corners. The time, status symbols,
  and Messages labels have separate vertical shutter treatments over the
  underlying glass tint. This pass covers all nine frames from 6.12 to 6.44 s.
- Fitted the left and right lobes and the notch of the floating hearts
  through the held title at frames 188–196. The title and hearts remain
  separate editable layers.
- Refined the closing profile badge’s outline over frames 701–711.
  Its three cards and heart still have visible differences at 28.24 s.

| Source time | Matched encoded crop | Previous mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
{comparison}

The right shoulder retains a faint interior reflection at 6.40 s.
The source camera island is more defined and its status letters are
streaked more vertically. The title still has different ink edges at
7.68 s. In the closing badge, the artwork remains softer than the source.
Thirty of 32 adjacent-frame comparisons improved. The transitions
into frame 153 and out to frame 712 show a larger temporal difference.
[Adjacent-frame measurements](review/temporal-metrics.csv)
[Matched cut frames](review/focus/f161-last-phone-frame.png) ·
[First title frame](review/focus/f162-first-title-frame.png)

## Full export verdict

**Exact fidelity fails.** The mux decodes cleanly. All 778 frames have
identical presentation timestamps and exclusive end times at 2000 × 2000.
Mean RGB error moved from {prior['mean_abs_rgb']:.4f} to {native['mean_abs_rgb']:.4f}.
{identical} frames are pixel-identical. The last frame differs by {ending} pixels.
The largest full-frame error is {error:.3f} at f{largest} ({largest/25:.2f} s).
[Exact verdict](review/native/report.json) ·
[All frame measurements](review/native/frames.csv) ·
[Highest-error frame](review/native/pairs/{largest:06d}.jpg)

**HyperFrames 0.9.77 passed its visual thresholds** and matched all six cuts.
Mean SSIM moved from {old_hf['ssim']['mean']:.4f} to {hf['ssim']['mean']:.4f}.
The pinned reviewer copy passed all 202 file checks.
[Official diff result](review/hyperframes.json) ·
[Ranked misses](review/hyperframes/worst.jpg) ·
[Reviewer source and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

All 29 affected lossless stage frames improved, and the other 749 matched
the previous render by hash. {wins} of 29 improved in the encoded MP4.{encoded_note}
The 48 kHz stems, event map, and AAC stream match the previous export by hash.
Each of {samples} Motion crops was checked for region, timestamp, and file hash.
Six isolated edits verified independent control of the glass and metal
contours, rim lighting, clock streak, floating heart, and badge.
[Motion crops](review/motion/motion-observations.json) ·
[Lossless stage comparison](review/stage-metrics.json) ·
[Edit checks](review/editability.json) ·
[Previous review](../refraction-review/README.md)

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
  "$SOURCE" ../refraction-review/candidate/sidehoe.mp4 \\
  candidate/sidehoe.mp4 review-rerun/focus
```
"""
(dest/'README.md').write_text(report)
print('mean',prior['mean_abs_rgb'],native['mean_abs_rgb'],'exact',identical,'worst',largest,error,'edited',wins,worsened)
print('hash',native['candidate']['sha256'])
