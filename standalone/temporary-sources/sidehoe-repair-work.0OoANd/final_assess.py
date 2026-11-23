from pathlib import Path
from hashlib import file_digest
import csv
import json
import os

case=Path('sidehoe-skill-trial/repair')
plan_file=case.parent/'repair-review/review-plan.json'
results_file=case/'evidence/visual-review.json'
evidence=case/'evidence/final-comparison'
stats_file=evidence/'report.json'
plan=json.loads(plan_file.read_text())
stats=json.loads(stats_file.read_text())
baseline=json.loads((case.parent/'repair-review/baseline-comparison/report.json').read_text())
baseline_state=json.loads((case.parent/'repair-review/baseline-acceptance.json').read_text())
review=[
    (False,0,4,"Separate portrait, header and note tracks restore the side portraits at f2. At f0 the source status marks fan outward while the candidate uses a soft translation. The f3 source tag and downward label streak still read earlier."),
    (True,22,22,"At f22 the three portrait disks, centered note and first two inbox rows retain the held layout. The portrait artwork is independently rendered."),
    (True,42,101,"Named Eleanor and Charlotte anchors agree through acceleration. The late fit tracks both the rising rows and the change in spacing and scale. Darla and El align at f95 and the leading Margot row is visible again at f101. The home bar and the strength of the departing streak around f56 still differ."),
    (False,103,114,"The opening and settled badge use separate measured dimensions. At f108 the leftmost original glyph is darker and the trailing part is more displaced. The independently drawn card illustration still has visibly wider pink shapes."),
    (False,136,150,"The fitted rim and pad improve the shape and lower light. The f136 island and rainbow edge still bend and spread differently. The held lower-right wash and rim contrast at f150 differ."),
    (False,178,212,"The candidate opens on ‘For’ and layers the arriving disks under the outgoing title at f212. Around f180, parts of the second line brighten in a different order and several of the tiny incoming patches remain fainter at f212."),
    (True,213,253,"Individual disk tracks carry the early components into the settled 13-disk layout through f226–227. At f242 and f249 the major centers and component count correspond. The independently authored portrait expressions and final perimeter still differ."),
    (False,254,264,"Measured islands restore parts of the outgoing mosaics and a padded streak brings Lisa in at f258. The visible remnants still have different edges and the profile label fragments at f262–264 resolve differently."),
    (False,290,300,"The green disk and Ella’s falloff use separate tracks. At f290 the outline on Lisa’s chip is more uniform. At f300 the source’s facial expression and Ella’s fading edge differ from the blended sprites."),
    (False,313,327,"The first visible hull bottom and the later rim are closer after fitting the clipped edge. On f316–319 the source keyboard is already sharper and vertically registered differently while the candidate streak persists."),
    (True,336,359,"There is no suggestion at f335. Both blue bubbles appear separately at f336. Measured boxes preserve their spacing through the push, and the first No and Send? controls appear below the lower bubble at f341 and f343. Both controls detach below the bubble at f359."),
    (True,394,394,"The detached controls sit under the suggestion at f394, and the pointer reaches the Send? capsule from below."),
    (True,397,429,"The lower calendar band is visible at f397 with the suggestion still above it. Appointments rise through consecutive frames; by f403 the calendar has replaced the suggestion. The padded cursor follows the measured turn around f408–415 and lands beside the lower appointment."),
    (True,435,435,"At f435 the violet appointment remains above cyan through their overlap. The grid stays registered."),
    (True,460,460,"At f460 cyan sits below the violet appointment on the same calendar grid."),
    (False,475,479,"The ring tile leads at f478, then red and blue enter. The source still has a stronger violet block behind the ring and different holes in the outgoing calendar grid."),
    (False,536,612,"Individual centers and depth changes keep the four glyphs readable. At f536 and f612 the dark tile has different scale and edge softness, and the red and blue artwork and overlap edges still differ."),
    (True,613,623,"Separate tile paths and a fitted glow move downward together. Motion streaks persist on the last occupied frame f621, and f622–623 are blank. The tile edge blur differs locally."),
    (False,624,647,"The visible bottom at f624 and the detached pointer are much closer. At f626–632 the candidate body and keyboard are streaked longer, and the settled bottom and keyboard proportions still differ."),
    (True,648,674,"No and Yes become visible on f648 and f650. In the sampled fast approach, the chip and fitted pointer follow separate measured paths, with the tip just above the composer at f665–667 and nearly at Yes by f674."),
    (True,675,695,"The decoded tip has zero gap to Yes at f675. Rim and interior offsets follow the late retreat and keep the chip and tip registered through f695. The keyboard keys and surrounding bubble type still differ."),
    (False,696,708,"Width and height are separately fitted from the first squash to the held badge. The held center card and heart proportions still differ visibly at f703–708."),
    (True,717,765,"Each word has separate measured bounds and opacity. ‘The’ reads first at f717, ‘iMessage’ enters on f741, and the complete second line is in place by the final set pose. Wash falloff is approximate."),
    (True,766,777,"Both movies reduce exposure into the final black frame at f777 and share the 40 ms final hold."),
]
assert len(review)==len(plan['shots'])==24

def digest(path):
    with path.open('rb') as h:
        return file_digest(h,'sha256').hexdigest()

def media_link(frame):
    return f"[f{frame:03d}](evidence/final-comparison/index.html?frame={frame})"

disp=csv.DictReader((evidence/'frames.csv').open())
frame_rows={int(r['frame']):r for r in disp}
total_exact=sum(float(r['mean_abs_rgb'])==0. for r in frame_rows.values())
assert len(frame_rows)==778 and all(float(row['clock_delta_ms'])==0. for row in frame_rows.values())
def mean(rows,span):
    return sum(float(rows[i]['mean_abs_rgb']) for i in range(span[0],span[1]+1))/(span[1]-span[0]+1)
with (case.parent/'repair-review/baseline-comparison/frames.csv').open() as f:
    old={int(r['frame']):r for r in csv.DictReader(f)}
assert len(old)==778
gross=stats['mean_abs_rgb']; prior=baseline['mean_abs_rgb']
assert stats['candidate']['sha256']==digest(case/'exports/sidehoe.mp4')
assert stats['reference']['sha256']==plan['reference_sha256']
metric=stats['worst_frame']
n_pass=sum(p for p,*_ in review)
n_closed=sum(p and s['id'] in baseline_state['open_shots'] for (p,*_),s in zip(review,plan['shots']))
n_regions=sum(f['check']=='region' for f in stats['failures'])
head=f"""# Sidehoe recreation repair and verification

**Full-export verdict is FAIL.** {n_pass} of 24 shots meet the frozen shot criteria. {n_closed} of the original 19 failures now pass and {24-n_pass} remain open. The original and repair have {len(frame_rows)} frames at 25 fps, matching every decoded presentation time and the 31.12-second picture end. The full-frame mean RGB error decreased from {prior:.2f} to {gross:.2f}. {total_exact} of {len(frame_rows)} frames are pixel-identical. The largest average error is at {media_link(metric["frame"])} ({metric["mean_abs_rgb"]:.2f}). {n_regions} of 23 named diagnostic regions still fail their preset RGB limit.

[Original left, repair right](exports/original-left-repair-right.mp4) · [Frame-by-frame viewer](evidence/final-comparison/index.html) · [Full native measurements](evidence/final-comparison/report.json) · [Repaired MP4](exports/sidehoe.mp4) · [Editable project](exports/editable-project.zip)

The comparison video carries the original audio. The repaired MP4 carries the editable score and Foley. The score and picture use the same timeline events. The Yes pointer is in the decoded target at frame 675. The frames in the viewer derive from the same hashed MP4 as the shot verdicts. [Contact measurements](evidence/yes-contact.csv) · [Timeline](evidence/resolved-events.json)

## Shot verdicts

The ranges and criteria are frozen from the prior repair plan. A pass applies to that shot’s recorded criterion. The RGB columns report the average over all frames of the shot, using the same measurements for both builds. Each observation links to decoded evidence. [Frozen plan](../repair-review/review-plan.json) · [Recorded observations](evidence/visual-review.json) · [Machine-verified acceptance](evidence/acceptance.json)

| Shot and range | Verdict | RGB error, prior → repaired | Observed result |
| --- | --- | --- | --- |
"""
scoped={}
lines=[]
for s,(passed,a,b,reason) in zip(plan['shots'],review):
    sid=s['id']; start,end=s['frames']
    window=s['checks']['appearance']['frames'] if passed else [a,b]
    tag='PASS' if passed else 'FAIL'
    pos=f'{media_link(a)}' if a==b else f'{media_link(a)}–{media_link(b)}'
    evidence_name='final-comparison/index.html' if passed else f'final-comparison/pairs/{a:06d}.jpg'
    scoped[sid]={'appearance':{'verdict':tag.lower(),'frames':window,'observation':reason,'evidence':evidence_name}}
    number,title=sid.split('-',1)
    title=title.replace('-',' ').capitalize().replace('Yes','Yes')
    lines.append(f'| {number} · {title} · {start}–{end} | {tag} | {mean(old,(start,end)):.2f} → {mean(frame_rows,(start,end)):.2f} | {reason} {pos} |')
results_file.write_text(json.dumps({'plan_sha256':digest(plan_file),'candidate_sha256':stats['candidate']['sha256'],
                                   'results':scoped},ensure_ascii=False,indent=2)+'\n')
tail="""

## Iterations and reusable changes

The original 19 failures were reworked in groups and checked in decoded probes before merging repairs into complete exports. The full-film RGB averages from the original benchmark and three intermediate builds were 8.85, 7.83, 7.42 and 7.22. The next benchmarks measured 7.13 and 7.00 before the inbox pullback and handset exposure refinements. The same checks file stayed in use.

- The two missing onsets came from scene geometry and tween opacity. The suggestion and calendar now have positive visible coverage at f336 and f397. The transition layers remain independent. [Suggestion probes](evidence/suggestion-probe.jpg) · [Calendar and follow-up probes](evidence/calendar-and-contact-probe.jpg)
- Independent row, portrait, tile, keyboard and word measurements replaced several shared paths. The phone hull can continue using its side walls for scale while registering the on-screen controls against an interior feature. [Portrait probes](evidence/portrait-transition-probe.jpg) · [Closing probes](evidence/closing-probe.jpg)
- The calendar pointer shrank at sharp angles because the renderer rotated it inside a tightly cropped image. Transparent padding preserves its outline, and the angle and tip are fitted independently. Testing only the starting and ending pointer poses missed that defect. [Calendar turn](evidence/final-comparison/index.html?frame=408)
- The reusable skill now calls for identifiable repeated features, an interior landmark when the hull is cropped, per-word ink bounds, enough space for a rotated or blurred layer, and color and opacity samples across both light and dark areas. [Updated visual review](../../codex-trial/skill/imessage-motion-recreation/recreate/VISUAL-REVIEW.md)

The remaining material, artwork and mask differences are visible in the decoded comparison. The supplied reference is a flattened film. This project uses independent art and compositing, including the previously generated head sprites, and has no original editable portrait, handset or effects layers. The review uses the authored visual criteria and records pixel equality independently. The film still falls short of the requested one-to-one match.

## Reproduce the review

From the workspace root, set `REF` to the supplied original MP4. Use Python with Pillow and NumPy, plus FFmpeg. The export command renders the editable project into a new directory. The comparison below checks the delivered MP4.

```sh
D=sidehoe-skill-trial/repair
S=codex-trial/skill/imessage-motion-recreation/recreate
B=sidehoe-skill-trial/repair-review
"$D/project/export.sh" /tmp/sidehoe-check-export /tmp/sidehoe-check-frames
python3 "$S/recreate.py" compare "$REF" "$D/exports/sidehoe.mp4" \
  --checks sidehoe-skill-trial/evidence/checks/diagnostic-settings.json \
  --out /tmp/sidehoe-check-comparison --pairs
python3 "$S/recreate.py" verify-review "$D/exports/sidehoe.mp4" \
  --plan "$B/review-plan.json" --review "$D/evidence/visual-review.json" \
  --comparison "$D/evidence/final-comparison/report.json" --out /tmp/sidehoe-check-acceptance.json
```

The two review commands return exit 1 while the recorded visual failures remain open. [Project instructions](project/README.md)
"""
(case/'REVIEW.md').write_text(head+'\n'.join(lines)+tail)
print({'pass':n_pass,'new':n_closed,'open':len(review)-n_pass,'mae':gross,'exact':total_exact})
