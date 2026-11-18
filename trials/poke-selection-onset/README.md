# Poke selection-onset trial

Frozen projects and resources are unchanged. The portable patch is
`selection.patch.json`; run `python derive_scene.py` to create the ignored derived
scene here. Absolute asset/font references point back to the unchanged project.
The derived copy contains no other visual changes.

Original scene SHA256:
`bf46102ecdc578cdadac244ba85dec7e5ab19fe07b80277a2fdcdb4c2b191df1`.
Source movie SHA256:
`a3d5dd064dc4482813a332d7e3821a43d557c015c5cbb5be6ff09b29874db50f`.
Accepted reference-audio movie SHA256:
`1004ce2e9ab70da7f5a1e0d7a849156cf06b89902ee0aadb8d2bddb2e416e176`.

The blue overlay `p0249` and checkmark `p0250` have lifecycle starts, not
selection keyframe tracks. Change both from 21.5 to `633*1001/30000 = 21.1211`
seconds. At the native 30000/1001 cadence, frame 632 precedes that threshold and
frame 633 reaches it. Previously the first eligible frame was 645.
The frozen audio cue at 645 must follow picture to 633 in any future audio revision;
this trial does not change audio.

## CLI (from repository root, Python 3.12 environment active)

```
GATE=skill/imessage-motion-recreation/scripts/verification/event_onsets.py
SOURCE=projects/04-poke-complete-v1/imessage-recreations/references/04-poke/source.mp4
ACCEPTED=projects/04-poke-complete-v1/imessage-recreations/deliverables/04-poke/gsap.mp4
python "$GATE" scan "$SOURCE" --out /Users/devin/poke-investigation/events.json
python "$GATE" compare "$SOURCE" "$ACCEPTED" --events /Users/devin/poke-investigation/events.json --tolerance 2 --out trials/poke-selection-onset/accepted-report.json
python "$GATE" compare "$SOURCE" /Users/devin/poke-investigation/repaired.mp4 --events /Users/devin/poke-investigation/events.json --tolerance 2 --out trials/poke-selection-onset/repaired-report.json
```

Optional `--roi-events manual.json` adds `{ "events": [...] }` records with
zero-based `frame`, normalized xyxy `bbox`, `kind`, `time` and `magnitude`.
`--frame-map anchors.json` accepts an ordered array of source/candidate frame
pairs, interpolated linearly. Without it, frame rates determine expected time.
`--window 20`, `--threshold 5`, `--stable 6` are configurable. Outputs include
JSON, CSV (all results) and short Markdown (failures). Nonzero means source-event
timing failures; candidate-only events are separate review candidates, not
automatically certified defects.

The detector decodes at up to 480 pixels wide, keeping aspect ratio and native
cadence. It measures a tile grid and merges four-connected changed tiles. It
retains isolated stable-state changes, abrupt impulses above decaying motion,
motion settling, and broad changes (cut candidates). Signed RGB transition
matching is deliberately a heuristic, not semantic object tracking. Camera
motion, similar repeated controls, lighting changes, or cancellation of colors
can cause false/missed matches. Stable windows omit events at film boundaries;
very small/low-contrast or gradual events need manual ROIs/other checks. The
decoder retains downscaled RGB frames in memory, so long films need ample RAM.
This complements, not replaces, all-frame image comparisons and visual review.

## Results and triage

Full-film automatic source scan: 1283 frames, 84 events, 2.736 seconds.
Initial permissive settings produced 2943 events. Requiring quiet new states
and sustained stable windows reduced motion chatter; permitting a strong local
impulse over decaying motion preserves selection detection at 633.

| Automatically discovered event | Accepted | Repaired |
|---|---|---|
| 633, selection ROI `[.7333,.4528,.8,.5444]` | 645, +12, late | 633, 0, pass |
| Whole-film source-event failures | 9 / 84 | 8 / 84 |
| Candidate-only review candidates | 40 | 43 |

Both whole-film comparisons exit 1: the targeted selection passes after repair,
but other heuristic flags remain. Do not call the entire repaired film gate-green.
Accepted comparison took 16.718 seconds; repaired 16.863 seconds.

Other accepted flags: cut candidates 455→458 and 577→582; two right-edge regions
at 480→461; settle 634→629; local regions 682→669 and 710→728; settle 1062→1065.
Source/accepted contact-sheet inspection at 455, 480, 577, 682 and 710 shows:

- 455 and 577 are continuous camera/sheet transitions, not hard cuts. Broad
  changing tiles misclassify motion as cuts; inferred offsets are review noise,
  not proven event delays.
- 480 concerns almost blank right-edge regions; the same-frame subject poses
  agree. Treat the distant match as boundary/compression noise.
- 710 shows a real blur/rendering difference, but both pictures already show
  the phone at 710. The +18 match is not evidence of a delayed phone cut.
- 682 shows small typography/control differences, not a visibly absent onset;
  -13 remains an ambiguous match, not a confirmed timing defect.
- 634 and 1062 settling flags were not independently visually adjudicated.

Contact sheet: `/Users/devin/poke-investigation/triage.png` (outside Git).
Only the selection delay is independently confirmed as a timing defect here.

## Render

Full 1283-frame GSAP film rendered in 91.318 seconds, using installed Chrome:

```
CHROME_PATH='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' \
node projects/04-poke-complete-v1/imessage-recreations/engines/render.mjs \
 --method gsap --scene trials/poke-selection-onset/derived-scene.json \
 --out /Users/devin/poke-investigation/repaired.mp4 \
 --frames-dir /Users/devin/poke-investigation/repaired-frames
```

The actual first render used an equivalent generated scene at
`/Users/devin/poke-investigation/repaired-scene.json`, with the same two edits and
absolute assets. Rendered media, frame caches, and generated scene are not tracked.
Tests: `python -m unittest discover -s skill/imessage-motion-recreation/scripts/verification -p test_event_onsets.py -v`.
