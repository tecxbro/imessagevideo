from pathlib import Path
from PIL import Image
from hashlib import sha256
import csv
import json
import sys

dest=Path(sys.argv[1]).resolve()
review=dest/'review'
before=dest.parent/'follow-handset-review'
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
assert changed==[*range(134,138),*range(343,352)] and all(v['revised']<v['previous'] for v in staged['measurements'] if v['different'])
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
assert samples==32
assert (review/'hyperframes/worst.jpg').stat().st_size>5000
assert (review/'side-by-side.mp4').stat().st_size>5000
assert hf['cuts']['reference']==hf['cuts']['yours']
assert wins==13,(wins,worsened)
labels=((134,'First handset frame'),(135,'Colored rim and refracted controls'),
        (136,'Portrait lighting and rail reflection'),(137,'Settling refraction'),
        (343,'Sofia handset at the start of the close-up'),
        (345,'Composer and keys during the push'),
        (347,'Composer and keys at closest approach'),(351,'End of the push'))
table=[]
for frame,label in labels:
    row=focus[frame]
    old,new=(float(row[k]) for k in ('previous_mean_abs_rgb','revised_mean_abs_rgb'))
    table.append(f"| {row['seconds']} s | [{label}](review/focus/{row['image']}) | {old:.2f} | {new:.2f} |")
comparison='\n'.join(table)
report=f"""# Sidehoe handset refraction and Sofia close-up

November 21, 2026. The [candidate MP4](candidate/sidehoe.mp4) was rendered
from a clean copy of the [editable project](project/README.md).

[Watch the source and recreation side by side](review/side-by-side.mp4) ·
[Inspect all 778 time-matched frames](review/native/index.html)

## What changed

- Fitted the assistant handset’s badge size, Messages glyphs, status controls,
  portrait lighting, and colored reflections over frames 134–137. The color
  and blur distort live authored shapes and type.
- Aligned Sofia’s handset rails, attachment control, microphone, composer
  outline, and keyboard over frames 343–351. The attachment control and
  keyboard glyphs can be moved independently.
- Checked the calendar tile arrival and the follow-up cursor at the
  same source times. [Calendar tile at 19.16 s](review/focus/f479-calendar-31-tile-arrival.png) ·
  [Cursor contact at 27.00 s](review/focus/f675-yes-cursor-contact.png) ·
  [Earlier tile and cursor repair](../tile-and-cursor-review/README.md)

| Source time | Matched encoded crop | Previous mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
{comparison}

The source rim remains softer and its camera island has a different highlight
at 5.40 seconds. The attached examples still show differences in the
title, heart contours, and profile badge artwork.
[Title and hearts at 7.68 s](review/focus/f192-attached-active-title-and-hearts.png) ·
[Profile badge at 28.24 s](review/focus/f706-attached-profile-badge.png)

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

All 13 affected frames improved in both the lossless render and the encoded
MP4. The other 765 lossless stage frames match the previous render by hash.
The 48 kHz stems, event map, and AAC stream also match the previous export by hash.
Motion supplied {samples} native source crops. Each crop’s region, timestamp,
and file hash were verified. Six isolated edits verified the badge, text,
refraction, light, and Messages layers.
[Motion observations](review/motion/motion-observations.json) ·
[Stage comparison and adjacent control frames](review/stage-metrics.json) ·
[Editability checks](review/editability.json) ·
[Previous review](../follow-handset-review/README.md)

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
  "$SOURCE" ../follow-handset-review/candidate/sidehoe.mp4 \\
  candidate/sidehoe.mp4 review-rerun/focus
```
"""
(dest/'README.md').write_text(report)
print('mean',prior['mean_abs_rgb'],native['mean_abs_rgb'],'identical',identical,'worst',largest,error,'edited',wins,worsened)
print('hash',native['candidate']['sha256'])
