from pathlib import Path
from PIL import Image
from hashlib import sha256
import csv
import json
import re
import sys

dest=Path(sys.argv[1]).resolve()
review=dest/'review'
old=dest.parent/'inbox-contacts-review'
source=Path('/Users/darshan/Downloads/sidehoe.mp4')
def read(path):
    return json.loads(path.read_text())
def rows(path):
    with path.open() as handle:
        return list(csv.DictReader(handle))
def digest(path):
    return sha256(path.read_bytes()).hexdigest()

native=read(review/'native/report.json')
prior=read(old/'review/native/report.json')
assert native['reference']['sha256']==digest(source)==prior['reference']['sha256']
assert native['candidate']['sha256']==digest(dest/'candidate/sidehoe.mp4')
assert native['checks_sha256']==digest(dest/'comparison-checks.json')
assert native['decode_completed'] and native['exact_clock']
assert (review/'status.txt').read_text()=='HyperFrames exit 0\nNative comparison exit 1\n'
now=rows(review/'native/frames.csv')
prev=rows(old/'review/native/frames.csv')
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
for label,start,end in (('profile-arrival-portraits-through-motion',260,270),
                        ('profile-arrival-names-and-tags',260,270),
                        ('follow-up-pre-contact-handset-exposure',650,659)):
    r=native['regions'][label]
    assert r['frames']==[start,end] and r['expected_frames']==r['scanned_frames']==end-start+1
    assert (review/'native'/r['worst_pixel_difference']['crop']).is_file()
    print(label, r['worst_mae'], r['worst_mae_frame'])

hf=read(review/'hyperframes.json')
old_hf=read(old/'review/hyperframes.json')
assert hf['_meta']['version']=='0.9.77'
assert hf['reference']==str(source) and hf['yours']==str(dest/'candidate/sidehoe.mp4')
assert hf['pass'] and hf['cuts']['reference']==hf['cuts']['yours']==[5.36,6.4,8.52,16.04,27.72,30.8]
for name in ('mix.wav','score.wav','foley.wav','events.json'):
    assert digest(dest/'candidate/sound'/name)==digest(old/'candidate/sound'/name)

plan=read(review/'motion-plan.json')
motion=read(review/'motion/motion-observations.json')
assert motion['planSHA256']==digest(review/'motion-plan.json')
assert motion['sourceSHA256']==digest(source)
assert len(plan['tracks'])==len(motion['tracks'])
samples=0
unobserved=[]
for expected,track in zip(plan['tracks'],motion['tracks'],strict=True):
    assert track['actor']==expected['id']
    assert track['searchRect']==expected['rect']
    track_frames=[s['frame'] for s in track['samples']]
    assert track_frames==list(range(expected['start'],expected['end']+1))
    for obs in track['samples']:
        samples+=1
        assert obs['pts']==obs['frame']*2400
        evidence=review/'motion'/obs['evidence']['path']
        assert obs['evidence']['sha256']==digest(evidence)
        with Image.open(evidence) as image:
            assert image.size==tuple(expected['rect'][2:])
            image.verify()
        if not obs['pixels']:
            unobserved.append((track['actor'],obs['frame']))
print('Motion crops',samples,'unobserved',unobserved)

staged=read(review/'stage-metrics.json')
edits=staged['changed_frames']
rawwins=sum(r['revised']<r['previous'] for r in staged['measurements'] if r['different'])
rawreg=[r['frame'] for r in staged['measurements'] if r['revised']>r['previous']]
dif={f:float(now[f]['mean_abs_rgb'])-float(prev[f]['mean_abs_rgb']) for f in edits}
wins=sum(v<0 for v in dif.values())
reg=[f for f,v in dif.items() if v>0]
focus={int(r['frame']):r for r in rows(review/'focus/metrics.csv')}
worst=max(now,key=lambda row:float(row['mean_abs_rgb']))
f_worst=int(worst['reference_frame'])
worst_err=float(worst['mean_abs_rgb'])
final_changed=int(now[-1]['exact_changed_pixels'])
print('Native worst',f_worst,worst_err)
print('Whole-film error',prior['mean_abs_rgb'],native['mean_abs_rgb'])
print('Exact pixels',identical)
print('Stage',len(edits),rawwins,rawreg,'Encoded',wins,reg)
print('Candidate',native['candidate']['sha256'])
print('Ending pixels differ',final_changed)

table=[]
for f,feature in ((259,'Before the profile reveal adjustment'),(260,'Lisa and Ella enter'),
                  (263,'Names and tags begin'),(264,'Frame before the largest difference'),
                  (265,'All three profiles during the reveal'),(266,'Next reveal frame'),
                  (269,'Faces settling'),(271,'First held profile frame'),
                  (649,'Before the follow-up exposure adjustment'),(655,'Handset before contact'),
                  (658,'Handset and cursor before the push'),(659,'Last edited follow-up frame'),
                  (660,'First follow-up close-up')):
    r=focus[f]
    item=f"[{feature}](review/focus/{r['image']})"
    table.append(f"| {r['seconds']} s | {item} | {float(r['previous_mean_abs_rgb']):.2f} | {float(r['revised_mean_abs_rgb']):.2f} |")
frame_table='\n'.join(table)
format_frames=lambda seq: ', '.join(f'f{n}' for n in seq)
raw_note=f' The mean RGB error increased on {format_frames(rawreg)}.' if rawreg else ''
encoded_note=f' The decoded error increased on {format_frames(reg)}.' if reg else ''
unobserved_note=(' The planned color masks had no detections for '
                 + ', '.join(f'{track} at f{f}' for track,f in unobserved)+'.') if unobserved else ''
assert len(read(review/'editability.json'))==4
report=f"""# Sidehoe profile reveal and follow-up handset review

November 21, 2026. The [candidate MP4](candidate/sidehoe.mp4) was rendered from a clean
copy of the [editable project](project/README.md).

[Watch the source and candidate side by side](review/side-by-side.mp4) ·
[Step through all 778 matched frame pairs](review/native/index.html)

## Edits

- At f260–270, Lisa, Ella and Maria use separate disk and face
  positions and focus. The names, tags and emoji have independent
  positions and appear at the measured points in the reveal.
- At f650–659, the handset’s camera and directional exposure follow
  the pre-contact move. The cursor has a separate editable track.

The Motion library supplied {samples} native source crops across {len(plan['tracks'])} tracks.
All crop hashes, dimensions and presentation times verified.{unobserved_note}
Editing a portrait position, a profile name, an interest tag and the
handset exposure in a clean copy changed their visible regions.
[Motion observations](review/motion/motion-observations.json) ·
[Editability evidence](review/editability.json)

| Source time | Matched screenshots | Previous mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
{frame_table}

Each row compares the same crop and frame from the three encoded files.
[Selected crop bounds and metrics](review/focus/metrics.csv) ·
[Previous candidate](../inbox-contacts-review/README.md)

## Final MP4 review

**Exact comparison failed.** The final mux decodes cleanly, and all 778 frame indices,
presentation times and exclusive end times match at 2000 × 2000 and 25 fps.
Whole-film mean RGB error moved from {prior['mean_abs_rgb']:.3f} to {native['mean_abs_rgb']:.3f}.
The reviewer found {identical} pixel-identical frames. The last frame differs by
{final_changed} pixels. The highest remaining whole-frame RGB error is {worst_err:.2f}
at f{f_worst} ({f_worst/25:.2f} s).
[Exact verdict](review/native/report.json) ·
[All frame measurements](review/native/frames.csv) ·
[Highest-error frame](review/native/pairs/{f_worst:06}.jpg)

At 10.60 s, the portraits and tag silhouettes are closer. The
source’s partial letters and blurred tag shapes still differ during
their entrance. At 26.32 s, the handset exposure is closer and
the casing edge and some of the key shapes still differ.
[Title and hearts at 7.60 s](review/focus/f190-attached-title-and-hearts.png) ·
[Profile badge at 28.24 s](review/focus/f706-attached-profile-badge.png)

**HyperFrames 0.9.77 passed its visual thresholds.** Its mean SSIM moved from
{old_hf['ssim']['mean']:.4f} to {hf['ssim']['mean']:.4f}. All six cuts aligned at
5.36, 6.40, 8.52, 16.04, 27.72 and 30.80 s. All 202 files in the official reviewer
copy verified against its manifest.
[HyperFrames report](review/hyperframes.json) ·
[Ranked comparison sheet](review/hyperframes/worst.jpg) ·
[Pinned reviewer and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

{rawwins} of {len(edits)} edited frames improved before encoding.{raw_note}
{wins} improved in the decoded MP4.{encoded_note} The other {staged['same_by_hash']}
lossless frames, authored audio stems, audio cue map and AAC stream match the
previous candidate by hash.
[Lossless measurements](review/stage-metrics.json)

Source SHA-256  
`{native['reference']['sha256']}`

Candidate MP4 SHA-256  
`{native['candidate']['sha256']}`

## Rerun the review

Set `SOURCE` to the locked source and use a fresh review directory.

```sh
PYTHON=/path/to/render-environment/bin/python \\
HYPERFRAMES=/path/to/hyperframes \\
bash review.sh "$SOURCE" "$PWD/candidate/sidehoe.mp4" "$PWD/review-rerun"

/path/to/render-environment/bin/python focus.py \\
  "$SOURCE" ../inbox-contacts-review/candidate/sidehoe.mp4 \\
  candidate/sidehoe.mp4 review-rerun/focus
```
"""
for link in re.findall(r'\]\(([^)]+)\)',report):
    assert (dest/link).is_file(),link
(dest/'README.md').write_text(report)
assert (dest/'README.md').read_text()==report

index=dest.parent/'REVIEW.md'
previous=index.read_text()
a=previous.index('The November 21 candidate')
b=previous.index('\n## Earlier benchmark')
assert 'inbox-contacts-review/' in previous[a:b]
section=f"""The November 21 candidate aligns all 778 frames and still differs from
the source in the exact pixel comparison. [Current review]({dest.name}/README.md) ·
[Current MP4]({dest.name}/candidate/sidehoe.mp4) ·
[Frame-by-frame comparison]({dest.name}/review/native/index.html)
"""
for link in re.findall(r'\]\(([^)]+)\)',section):
    assert (index.parent/link).is_file(),link
content=previous[:a]+section+previous[b:]
index.write_text(content)
assert index.read_text()==content
print('Verified complete comparison, screenshots and benchmark links')
