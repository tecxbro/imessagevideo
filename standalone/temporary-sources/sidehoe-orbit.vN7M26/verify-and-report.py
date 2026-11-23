from pathlib import Path
from PIL import Image
from hashlib import sha256
import csv
import json
import sys

dest=Path(sys.argv[1]).resolve()
review=dest/'review'
before=dest.parent/'keyboard-exposure-review'
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
for region in load(dest/'comparison-checks.json')['regions'][-6:]:
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
assert changed==[*range(340,347),*range(483,622)] and all(v['revised']<v['previous'] for v in staged['measurements'] if v['different'])
assert len(load(review/'editability.json'))==6

motion=load(review/'motion/motion-observations.json')
plan=load(review/'motion-plan.json')
assert motion['planSHA256']==digest(review/'motion-plan.json') and motion['sourceSHA256']==digest(source)
assert len(plan['tracks'])==len(motion['tracks'])==6
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
assert samples==60
assert (review/'hyperframes/worst.jpg').stat().st_size>5000
assert (review/'side-by-side.mp4').stat().st_size>5000
assert hf['cuts']['reference']==hf['cuts']['yours']

temporal=rows(review/'temporal-metrics.csv')
assert len(temporal)==150
assert all(int(r['frame'])==int(r['previous_frame'])+1 for r in temporal)
temporal_worse=[int(r['frame']) for r in temporal
                if float(r['previous_temporal_rgb_error'])<float(r['revised_temporal_rgb_error'])]
assert temporal_worse==[505,515,522,523,524,525]
temporal_wins=sum(float(r['revised_temporal_rgb_error'])<float(r['previous_temporal_rgb_error']) for r in temporal)
assert temporal_wins==144
aac=(scratch/'aac-sha.txt').read_text().splitlines()
assert len(aac)==2 and aac[0]==aac[1] and aac[0].startswith('SHA256=')

labels=((340,'First revised suggestion'),(342,'Sofia’s suggestion and live text'),
        (483,'First revised orbit frame'),(486,'Four independent tile positions'),
        (557,'Rings cross forward'),(575,'Curved 31 tile beside the rings'),
        (617,'Tiles descend'),(621,'Last tile streak'))
table=[]
for frame,label in labels:
    row=focus[frame]
    old,new=(float(row[k]) for k in ('previous_mean_abs_rgb','revised_mean_abs_rgb'))
    assert new<old,(frame,old,new)
    table.append(f"| {row['seconds']} s | [{label}](review/focus/{row['image']}) | {old:.2f} | {new:.2f} |")
comparison='\n'.join(table)
encoded_note=''
if worsened:
    encoded_note=" Full-frame error rose at "+", ".join(f"f{i}" for i in worsened)+"."
report=f"""# Sidehoe tile orbit and Sofia’s suggestion

November 21, 2026. The [candidate MP4](candidate/sidehoe.mp4) was rendered
from a clean copy of the [editable project](project/README.md).

[Watch source and recreation side by side](review/side-by-side.mp4) ·
[Inspect all 778 time-matched frames](review/native/index.html)

- Registered the red flame, dark glyph, overlapping rings, and blue
  calendar tile independently over frames 483–621. Their positions,
  proportions, depth of focus, and coverage remain editable.
- Fitted the outlines and tint of Sofia’s reply and suggestion over
  frames 340–346. The edited outline and live text each have a
  measured slope and brightness.

| Source time | Matched encoded crop | Previous mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
{comparison}

Of the 150 adjacent-frame comparisons, 144 improved. All ten
measured steps around the suggestion improved. The six regressions
are in the tile orbit at frames 505, 515, and 522–525.
At 13.68 s the suggestion lettering is still softer than the
reference. At 22.28 s the ring outline and purple reflection
still differ.
[Adjacent-frame measurements](review/temporal-metrics.csv)

[Title and hearts at 7.68 s](review/focus/f192-attached-title-and-hearts.png) ·
[First 31 tile at 19.16 s](review/focus/f479-calendar-31-tile-arrival.png) ·
[Cursor contact at 27.00 s](review/focus/f675-cursor-contact.png) ·
[Profile badge at 28.24 s](review/focus/f706-attached-profile-badge.png)

## Full export verdict

**Exact fidelity fails.** The mux decodes cleanly. All 778 frames have
matching presentation timestamps and exclusive end times at 2000 × 2000.
Mean full-film RGB error moved from {prior['mean_abs_rgb']:.4f} to {native['mean_abs_rgb']:.4f}.
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

All 146 affected lossless frames improved, and the other 632 match
the previous stage render by hash. {wins} of 146 improved in the encoded MP4.{encoded_note}
The 48 kHz stems, event map, and AAC stream match the previous export by hash.
Each of {samples} Motion source crops was checked for region, timestamp, and hash.
Six isolated edits verified separate control of ring position,
calendar height, dark-glyph focus, bubble slope, and live text.
[Motion crops](review/motion/motion-observations.json) ·
[Stage comparison](review/stage-metrics.json) ·
[Edit checks](review/editability.json) ·
[Previous review](../keyboard-exposure-review/README.md)

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
  "$SOURCE" ../keyboard-exposure-review/candidate/sidehoe.mp4 \\
  candidate/sidehoe.mp4 review-rerun/focus
```
"""
(dest/'README.md').write_text(report)
print('mean',prior['mean_abs_rgb'],native['mean_abs_rgb'],'exact',identical,'worst',largest,error,'edited',wins,worsened)
print('hash',native['candidate']['sha256'])
