# Sidehoe recreation benchmark

The November 21 candidate aligns all 778 frames. The exact pixel
comparison still fails. [Current review](sofia-casing-review/README.md) ·
[Current MP4](sofia-casing-review/candidate/sidehoe.mp4) ·
[Frame-by-frame comparison](sofia-casing-review/review/native/index.html)

## Earlier benchmark

**Overall visual verdict: Fail. 5 of 24 shots pass their visual criteria.** The complete frame clock and ending hold pass. Sidehoe is a regression against the existing reference. The goal of a visually interchangeable recreation is still open.

[Watch the benchmark MP4](exports/sidehoe.mp4) · [Benchmark project ZIP](exports/editable-project.zip) · [All pre-render probes](PROBES.md) · [Original audit](../sidehoe-recreation/REVIEW.md)

## Full-length comparisons

The same original region limits are used for all four iterations and the baseline. These RGB checks are diagnostics. The visual verdicts below also use direct feature checks and the aligned frames.

| Full encode | Mean RGB error | Worst frame RGB error | Failed regions out of 23 | Frames over the whole-frame limit |
| --- | ---: | ---: | ---: | ---: |
| Original Sidehoe revision | 13.33 | 40.56 | 12 | 121 |
| C | 10.37 | 35.18 | 8 | 85 |
| E | 10.31 | 35.68 | 9 | 90 |
| H | 9.20 | 35.06 | 7 | 69 |
| I | 8.85 | 26.57 | 6 | 61 |

The final worst frame is 690, during the follow-up withdrawal. Its handset and crop diverge during the pullback. The early glossy handset remains the largest sustained mismatch. [Native frame results](evidence/checks/frames.csv) · [Region results](evidence/checks/regions.csv) · [Comparison report](evidence/checks/report.json)

## Visual verdict for every shot

Pass means the shot clears its visible action and appearance criteria at viewing scale. For a failure, the listed frame is a checkpoint that exhibits the miss. Evidence includes decoded checkpoints and longer crops around the events. The native compare covers every frame.

| Frames | Shot | Verdict | Evidence and reasoning | Mean RGB error |
| --- | --- | --- | --- | ---: |
| 0–9 | Pinned inbox entrance | **Fail** | f000. The status chrome is already crisp while the source is still streaked. The center portrait and note reveal differ. [Probe](evidence/probe-h/01-pinned-inbox-entrance.jpg) · [Full export](evidence/final-pairs/01-pinned-inbox-entrance.jpg) · [Detail](evidence/final-pairs/01-pinned-inbox-entrance-detail.jpg) | 7.11 |
| 10–41 | Inbox hold | **Pass** | f022. The three pinned avatars, note and first two rows read in their settled positions. Independently authored faces have minor contour differences. [Probe](evidence/probe-h/02-inbox-hold.jpg) · [Full export](evidence/final-pairs/02-inbox-hold.jpg) · [Detail](evidence/final-pairs/02-inbox-hold-detail.jpg) | 9.68 |
| 42–101 | Inbox scroll | **Fail** | f056. Row spacing, sweep and settlement are closer. Mid-sweep streak length and row alignment still differ. [Probe](evidence/probe-h/03-inbox-scroll.jpg) · [Full export](evidence/final-pairs/03-inbox-scroll.jpg) · [Detail](evidence/final-pairs/03-inbox-scroll-detail.jpg) | 9.67 |
| 102–133 | Identity | **Fail** | f106. Measured badge track matches its scale and travel more closely. The first pink glyph and the internal card shapes differ. [Probe](evidence/probe-h/04-identity.jpg) · [Full export](evidence/final-pairs/04-identity.jpg) · [Detail](evidence/final-pairs/04-identity-detail.jpg) | 4.96 |
| 134–161 | Glossy handset | **Fail** | f135. Glossy rim and top-edge ripple are present. Refraction spreads differently across the island, and the lower wash and phone details differ. [Probe](evidence/probe-i/05-glossy-handset.jpg) · [Full export](evidence/final-pairs/05-glossy-handset.jpg) · [Detail](evidence/final-pairs/05-glossy-handset-detail.jpg) | 21.09 |
| 162–212 | Personal title | **Fail** | f162. The fitted wash and settled line widths are closer. The first phrase appears too far along, and the late frames miss the first portrait disks. [Probe](evidence/probe-h/06-personal-title.jpg) · [Full export](evidence/final-pairs/06-personal-title.jpg) · [Detail](evidence/final-pairs/06-personal-title-detail.jpg) | 6.45 |
| 213–253 | Dimensional portrait cluster | **Fail** | f213. The five portrait centers and colored disks are much closer when settled. The first disks are softer and less visible than in the reference. [Probe](evidence/probe-h/07-dimensional-portrait-cluster.jpg) · [Full export](evidence/final-pairs/07-dimensional-portrait-cluster.jpg) · [Detail](evidence/final-pairs/07-dimensional-portrait-cluster-detail.jpg) | 10.35 |
| 254–281 | Cluster wipe and profile reveal | **Fail** | f254. The masked cluster and the three measured entrances occur in order. White gap positions and streaks around frames 256–258 remain different. [Probe](evidence/probe-h/08-cluster-wipe-and-profile-reveal.jpg) · [Full export](evidence/final-pairs/08-cluster-wipe-and-profile-reveal.jpg) · [Detail](evidence/final-pairs/08-cluster-wipe-and-profile-reveal-detail.jpg) | 7.95 |
| 282–312 | Profile push | **Fail** | f290. Lisa's card moves forward and Ella fades. The face angle, highlighted chip and Ella's fade envelope differ. [Probe](evidence/probe-h/09-profile-push.jpg) · [Full export](evidence/final-pairs/09-profile-push.jpg) · [Detail](evidence/final-pairs/09-profile-push-detail.jpg) | 12.44 |
| 313–335 | First phone entrance | **Fail** | f313. The vertical drop, streaking and black shell read. The exit of blur and the handset framing still diverge during the push. [Probe](evidence/probe-i/10-first-phone-entrance.jpg) · [Full export](evidence/final-pairs/10-first-phone-entrance.jpg) · [Detail](evidence/final-pairs/10-first-phone-entrance-detail.jpg) | 12.40 |
| 336–359 | Suggestion and controls | **Fail** | f336. Both control states and the detach are present. The source suggestion is visible earlier and the keyboard and control positions diverge during the move. [Probe](evidence/probe-i/11-suggestion-and-controls.jpg) · [Full export](evidence/final-pairs/11-suggestion-and-controls.jpg) · [Detail](evidence/final-pairs/11-suggestion-and-controls-detail.jpg) | 17.11 |
| 360–396 | Isolated suggestion and pointer | **Pass** | f394. Both detached bubble bounds track the reference and the pointer approaches and reaches Send? from below. No sent message appears. [Probe](evidence/probe-h/12-isolated-suggestion-and-pointer.jpg) · [Full export](evidence/final-pairs/12-isolated-suggestion-and-pointer.jpg) · [Detail](evidence/final-pairs/12-isolated-suggestion-and-pointer-detail.jpg) | 6.25 |
| 397–429 | Calendar entry | **Fail** | f397. The settled marker aligns to measurement precision, but the calendar is too faint at first overlap and the entry cursor looks different. [Probe](evidence/probe-h/13-calendar-entry.jpg) · [Full export](evidence/final-pairs/13-calendar-entry.jpg) · [Detail](evidence/final-pairs/13-calendar-entry-detail.jpg) | 6.07 |
| 430–451 | Violet appointment drag | **Pass** | f435. Violet rises ahead of cyan, passes through the overlap and retains an independent grid anchor. Minor pointer shape difference. [Probe](evidence/probe-h/14-violet-appointment-drag.jpg) · [Full export](evidence/final-pairs/14-violet-appointment-drag.jpg) · [Detail](evidence/final-pairs/14-violet-appointment-drag-detail.jpg) | 4.92 |
| 452–473 | Cyan appointment drag | **Pass** | f460. Cyan drops beneath violet and both settle in successive slots. Direct position and ordering checks clear. [Probe](evidence/probe-h/15-cyan-appointment-drag.jpg) · [Full export](evidence/final-pairs/15-cyan-appointment-drag.jpg) · [Detail](evidence/final-pairs/15-cyan-appointment-drag-detail.jpg) | 4.76 |
| 474–486 | Calendar mosaic and app entry | **Fail** | f478. The white blocks begin in the right window. The ring tile should dominate the first app reveal; the brighter tiles arrive early. [Probe](evidence/probe-h/16-calendar-mosaic-and-app-entry.jpg) · [Full export](evidence/final-pairs/16-calendar-mosaic-and-app-entry.jpg) · [Detail](evidence/final-pairs/16-calendar-mosaic-and-app-entry-detail.jpg) | 6.41 |
| 487–612 | App orbit | **Fail** | f487. Red and blue follow measured bounds and the foreground order is recognizable. Ring and dark tile positions and glyph sizes still differ. [Probe](evidence/probe-h/17-app-orbit.jpg) · [Full export](evidence/final-pairs/17-app-orbit.jpg) · [Detail](evidence/final-pairs/17-app-orbit-detail.jpg) | 7.12 |
| 613–623 | App exit | **Fail** | f613. The tiles streak down and the blank beat is present. The quiet background glow and some tile scale changes fail to follow the source's exit. [Probe](evidence/probe-h/18-app-exit.jpg) · [Full export](evidence/final-pairs/18-app-exit.jpg) · [Detail](evidence/final-pairs/18-app-exit-detail.jpg) | 6.75 |
| 624–647 | Second phone entrance | **Fail** | f624. The second handset drops and settles with the right transcript. Its keyboard height and drop exposure still differ. [Probe](evidence/probe-i/19-second-phone-entrance.jpg) · [Full export](evidence/final-pairs/19-second-phone-entrance.jpg) · [Detail](evidence/final-pairs/19-second-phone-entrance-detail.jpg) | 10.52 |
| 648–674 | Follow-up buttons and push | **Fail** | f648. Both buttons appear and the camera push reads. The initial button presentation and the cue at the middle of the push remain visually different. [Probe](evidence/probe-i/20-follow-up-buttons-and-push.jpg) · [Full export](evidence/final-pairs/20-follow-up-buttons-and-push.jpg) · [Detail](evidence/final-pairs/20-follow-up-buttons-and-push-detail.jpg) | 15.43 |
| 675–695 | Yes contact and withdrawal | **Fail** | f687. The cursor touches Yes on the same measured frame. The late tint, pointer appearance and pullback still differ from the reference. [Probe](evidence/probe-h/21-yes-contact-and-withdrawal.jpg) · [Full export](evidence/final-pairs/21-yes-contact-and-withdrawal.jpg) · [Detail](evidence/final-pairs/21-yes-contact-and-withdrawal-detail.jpg) | 17.27 |
| 696–716 | Closing badge entrance | **Fail** | f696. The measured outer badge scale and center are close by 703. The pop begins with a different shape, and card details remain visible. [Probe](evidence/probe-h/22-closing-badge-entrance.jpg) · [Full export](evidence/final-pairs/22-closing-badge-entrance.jpg) · [Detail](evidence/final-pairs/22-closing-badge-entrance-detail.jpg) | 4.06 |
| 717–765 | Closing copy and wash | **Fail** | f717. The wash and final line widths are closer. The word build, weight, and brand art still read differently side by side. [Probe](evidence/probe-h/23-closing-copy-and-wash.jpg) · [Full export](evidence/final-pairs/23-closing-copy-and-wash.jpg) · [Detail](evidence/final-pairs/23-closing-copy-and-wash-detail.jpg) | 4.95 |
| 766–777 | Closing fade and black hold | **Pass** | f777. The exposure declines through the full fade. Frame 777 is black and its full 40 ms sample is present. [Probe](evidence/probe-h/24-closing-fade-and-black-hold.jpg) · [Full export](evidence/final-pairs/24-closing-fade-and-black-hold.jpg) | 4.63 |

## Playback and editability checks

- Source and final both contain 778 frames at 25 fps and end at 31.120 s. Every paired start and exclusive end matches. The closing fade mean RGB differs by at most 3.33 levels in the 500 px samples, and the final frame is black.
- The red day marker at f420 aligns at the measurement resolution. The maximum position error across the 12 checked marker frames is 4.0 coded pixels. The Yes cursor touches its control on frame 675 in both exports. [Direct measurements](evidence/checks/landmark-summary.json) · [Yes contact](evidence/checks/yes-contact.csv)
- The editable ZIP was extracted in a clean directory. Python source access was denied by an audit hook. FFmpeg read the independent PNGs and authored WAVs. All 303 H probe frames and all 93 I probe frames matched the clean render cache by SHA-256. The final pass recaptured 64 frames and reused 714. [Clean reopen checks](evidence/reopen.json)
- An isolated edit swaps Yes for Go! and moves contact from frame 675 to 681. The cue moves 11,520 samples, and the decoded frames show the changed label and cursor timing. [Edit proof](evidence/edit-proof/yes-to-go.jpg) · [Edit preview](evidence/edit-proof/edit-proof.mp4) · [Cue delta](evidence/edit-proof/cue-delta.json)
- The original authored 48 kHz stereo score and 22 cues are editable. The silent picture and mux have identical decoded video frame hashes. Audio verification covers signal and timing. [Event map](exports/events.json) · [Score](exports/sound/score.wav) · [Foley](exports/sound/foley.wav)

## Changes carried into the skill

The installed skill carries forward authorization for supplied material in this workspace. It now directs authors to measure independently moving features, fit light from unobstructed patches, verify recognizable assets in shot before animating, and reuse verified frames when a repair is local. A complete benchmark can be rendered with probe failures recorded. The release package and routing tests passed.

The practical gain came from measuring the two bubble boxes, cursor tip, grid marker, badge center and portrait entrances separately. Image generation guided by the reference worked better than a generic dimensional look. Cache reuse let the last full export repaint only 64 frames.
