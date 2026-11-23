from pathlib import Path
from hashlib import sha256
import csv
import json
import re
import sys

dest=Path(sys.argv[1]).resolve()
review=dest/'review'
before=dest.parent/'inbox-and-lens-review'/'review/native'
intermediate=dest.parent/'opening-and-sofia-review'
def data(path):
    return json.loads(path.read_text())
def rows(path):
    with path.open() as handle:
        return list(csv.DictReader(handle))

native=data(review/'native/report.json')
original=data(before/'report.json')
hf=data(review/'hyperframes.json')
prior_hf=data(before.parent/'hyperframes.json')
focus={int(row['frame']):row for row in rows(review/'focus/metrics.csv')}
before_frames=rows(before/'frames.csv')
after_frames=rows(review/'native/frames.csv')
stage=data(review/'stage-metrics.json')
changed=stage['final_changed_frames']
wins=sum(float(after_frames[f]['mean_abs_rgb'])<float(before_frames[f]['mean_abs_rgb']) for f in changed)
losses=[f for f in changed if float(after_frames[f]['mean_abs_rgb'])>float(before_frames[f]['mean_abs_rgb'])]
ties=len(changed)-wins-len(losses)
assert len(before_frames)==len(after_frames)==778
assert hf['pass'] and native['exact_clock']
assert native['pixel_equality']['identical_frames']==0
worst=max(after_frames,key=lambda row: float(row['mean_abs_rgb']))
worst_frame=int(worst['reference_frame'])
assert worst_frame==136
source_hash=native['reference']['sha256']
candidate_hash=native['candidate']['sha256']
end_delta=int(after_frames[-1]['exact_changed_pixels'])
assert sha256((dest/'candidate/sidehoe.mp4').read_bytes()).hexdigest()==candidate_hash

lines=[]
for frame, label in ((0,'Opening streaks'),(9,'Pins, note and inbox rows'),
                     (136,'Glossy reveal lighting'),(319,'Sofia’s handset entrance'),
                     (619,'Calendar tile at exit'),(675,'Cursor at contact'),
                     (685,'Cursor during the hold'),(694,'Cursor withdrawing')):
    row=focus[frame]
    lines.append(f"| {row['seconds']} s | [{label}](review/focus/{row['image']}) | "
                 f"{float(row['previous_mean_abs_rgb']):.2f} | {float(row['revised_mean_abs_rgb']):.2f} |")
table='\n'.join(lines)
regressions=''
if losses:
    regressions=' The full-frame error increased slightly at '+', '.join(f'f{f}' for f in losses)+'.'
if ties:
    regressions+=f' {ties} scored the same.'
motion=data(review/'motion/motion-observations.json')['tracks']
samples=sum(len(a['samples']) for a in motion)
found=sum(bool(s['pixels']) for a in motion for s in a['samples'])
rendered=stage['final_same_by_hash']

report=f"""# Sidehoe tile, lighting and cursor review

November 21, 2026. The [candidate MP4](candidate/sidehoe.mp4) was rendered from a clean
copy of the [editable project](project/README.md) and reviewed against the locked reference.

[Watch side by side with the source on the left](review/side-by-side.mp4) ·
[Step through the same-time screenshots for all 778 frames](review/native/index.html)

## What changed

- **Calendar tile, f615–619.** The editable curves for “31” have their own position and stroke treatment.
  The upper shoulder and fold use separate light fields. The source digits still have a sharper core
  during the vertical exit.
- **Handset lighting, f136–137.** The upper rim and lower flare were fitted independently. The source
  spreads the rainbow more at the left edge, and its dark rim is rounder. The entrance at f314–328
  also registers the outer case, glass, conversation and keyboard separately.
- **Cursor, f670–694.** The editable arrow shape now has a wider stem and rounder endpoint through
  the approach, contact and withdrawal. Visible differences remain at the stem edges and in the
  emoji and bubble behind the arrow. The original pinned inbox entrance at f0–9 also has independently
  timed status streaks, pinned contacts, note and first two rows.

The Motion library extracted {samples} native crops across {len(motion)} tracks.
Every sample verified against its crop hash and presentation time. The selected blue-dot
mask found no matching pixels at f4 and found the dot from f5. Reopening a clean copy
and editing the inbox note, Sofia reply, “31” placement and cursor contour changed the
corresponding regions. [Motion observations](review/motion/motion-observations.json) ·
[Edit evidence](review/editability.json)

| Time | Same-time source, previous export and revised export | Previous mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
{table}

Scores are mean absolute RGB errors on the same crop in the two encoded exports.
The [selected frame measurements](review/focus/metrics.csv) give the crop bounds.
The [previous candidate](../inbox-and-lens-review/README.md) is the baseline.

## Full export verdict

**Exact comparison failed.** The mux decodes cleanly and all 778 frames align by index,
presentation time and exclusive end time at 2000 × 2000 and 25 fps. Whole-film mean RGB
error moved from {original['mean_abs_rgb']:.3f} to {native['mean_abs_rgb']:.3f}.
Zero frames are pixel-identical. The last frame differs by {end_delta} pixels. The glossy handset
at f136 has the highest mean RGB error, {float(worst['mean_abs_rgb']):.2f}.
[Exact verdict](review/native/report.json) · [Measurements for every frame](review/native/frames.csv)

**HyperFrames 0.9.77 passed its visual thresholds.** Its mean SSIM rose from
{prior_hf['ssim']['mean']:.4f} to {hf['ssim']['mean']:.4f}.
It found the same six cuts at 5.36, 6.40, 8.52, 16.04, 27.72 and 30.80 s.
All 202 files in the official reviewer copy verified against the pinned file manifest.
[HyperFrames report](review/hyperframes.json) ·
[Ranked comparison sheet](review/hyperframes/worst.jpg) ·
[Pinned reviewer code and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

All {len(changed)} edited lossless frames improved on mean RGB error. {wins} of them also improved
in the decoded export.{regressions} The other {rendered} lossless frames, authored audio
stems, cue map and AAC payload match the preceding baseline by hash.
[Opening, lighting and Sofia render measurements](review/stage-metrics.json) ·
[Tile and cursor render measurements](review/tile-and-cursor-stage-metrics.json)

The title and hearts at 7.60 s and the profile badge at 28.24 s still have the same crop
errors as the previous candidate. [Title and hearts](review/focus/{focus[190]['image']}) ·
[Profile badge](review/focus/{focus[706]['image']})

Source SHA-256  
`{source_hash}`

Candidate MP4 SHA-256  
`{candidate_hash}`

## Rerun the review

Set `SOURCE` to the locked reference and use a fresh review directory.

```sh
PYTHON=/path/to/render-environment/bin/python \\
HYPERFRAMES=/path/to/hyperframes \\
bash review.sh "$SOURCE" "$PWD/candidate/sidehoe.mp4" "$PWD/review-rerun"

/path/to/render-environment/bin/python focus.py \\
  "$SOURCE" ../inbox-and-lens-review/candidate/sidehoe.mp4 \\
  candidate/sidehoe.mp4 review-rerun/focus
```
"""
report=report.replace(f'Every sample verified against its crop hash and presentation time.',f'All {samples} crop hashes and presentation times verified.')
assert found==samples-1
for link in re.findall(r'\]\(([^)]+)\)',report):
    assert (dest/link).exists(),link
(dest/'README.md').write_text(report)
assert (dest/'README.md').read_text()==report

snapshot=data(intermediate/'review/native/report.json')
checkpoint=f"""# Sidehoe opening and Sofia entrance review

November 21, 2026. This checkpoint registers the opening inbox, glossy handset light
and Sofia entrance. The export decodes cleanly and all 778 frames align.
Whole-film mean RGB error fell from {original['mean_abs_rgb']:.3f} to {snapshot['mean_abs_rgb']:.3f}.
The exact comparison found zero pixel-identical frames.

[Candidate](candidate/sidehoe.mp4) · [Side-by-side video](review/side-by-side.mp4) ·
[All frame pairs](review/native/index.html) · [Exact comparison](review/native/report.json) ·
[HyperFrames comparison](review/hyperframes.json) · [Editable project](project/README.md)

[Later tile and cursor review](../{dest.name}/README.md)
"""
for link in re.findall(r'\]\(([^)]+)\)',checkpoint):
    assert (intermediate/link).exists(),link
(intermediate/'README.md').write_text(checkpoint)
assert (intermediate/'README.md').read_text()==checkpoint

anchor=dest.parent/'REVIEW.md'
old=anchor.read_text()
start=old.index('The November 21 candidate')
end=old.index('\n## Earlier benchmark')
assert 'inbox-and-lens-review/' in old[start:end]
new=f"""The November 21 candidate aligns all 778 frames and still differs from
the source in the exact pixel comparison. [Current review]({dest.name}/README.md) ·
[Current MP4]({dest.name}/candidate/sidehoe.mp4) ·
[Frame-by-frame comparison]({dest.name}/review/native/index.html)
"""
for link in re.findall(r'\]\(([^)]+)\)',new):
    assert (anchor.parent/link).exists(),link
updated=old[:start]+new+old[end:]
anchor.write_text(updated)
assert anchor.read_text()==updated
print('Wrote verified reports and updated the benchmark links')
