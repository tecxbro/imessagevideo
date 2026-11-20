---
name: imessage-sound
description: Design and revise sound for an iMessage picture cut. Author original audio, keep editable stems, resolve cues from decoded picture frames, and verify synchronization in the encoded MP4.
---

# Sound design and editing

Take the current silent master, its SHA-256, and Direction or Recreation's event map. Work against the playable cut from Pillow, GSAP, Remotion, HTML/SVG, or Motion Canvas. Their scene and event map give actions stable names. The decoded picture supplies the clock.

## Spot the cut

1. Probe each input with `ffprobe -v error -show_streams -show_format -of json INPUT`. Record its path, hash and classification. A silent picture master has no audio stream. A reference export or finished mix can have the same stream types, so establish which it is from provenance. Standalone sounds and stems need asset-specific origin, rights and intended role. Request the silent export if the supplied picture still carries its reference soundtrack. When stripping known guide audio, explicitly use `mix --replace-audio`.
2. Inspect a contact sheet for structure, then consecutive decoded frames around each action. Name the first visible state that earns a cue. Describe the state in ordinary language, name its event ID, and save the frame evidence. Track the composition's visual hierarchy and leave reading space around dialogue and substantial text.
3. For each passage state what the viewer should notice, understand or feel. Choose dialogue, music, ambience, a physical or interface sound, or silence to serve that purpose. A tap can clarify agency, a reply can shift attention, a quiet room can carry a screen-to-world cut, and an unanswered message can read more clearly with a silent hold. Keep soft interfaces away from speech attacks. For a consequential beat, make two distinct, level-matched treatments of the same picture with anonymous A/B labels. If the problem is the cut, audition quiet versions of both picture edits and send the filmmaker both.
4. Record where each source came from. Use original synthesis, authorized recorded material or correctly licensed effects. Keep IDs and sample offsets stable across revisions, and write gain, placement and source preparation into an editable plan. Separate source file zero, an onset marker, and a perceptual impact marker. An inhale, whoosh or mechanical latch can start early while its accent belongs to a later picture frame. This workflow estimates the timing of the chosen markers by matching the waveform.
5. Take notes in two forms. Measurements include observed frame, impact error, gain, peak and gaps. Audition notes name the listener, file and time, what they heard, and a change to try. For example, “impact is 18 ms behind the cut” is a measurement. “Adele heard the click mask the first word at 00:04” is a listening note. Until a person listens, record human audition as pending.

## Author the plan

Use the [small runnable plan](fixtures/plan.json) as a starting point. Dependencies are Python 3.11+, NumPy, SciPy, Pillow, `ffmpeg` and `ffprobe`. Run commands from the repository root.

```sh
python3 -m pip install -r skill/imessage-motion-recreation/sound/requirements.txt
S=skill/imessage-motion-recreation/sound
python3 "$S/example.py" /tmp/imv-sound-example
```

The example runs six decoded exports and writes reports for the original cue, late cue, missing cue, jointly shifted manifest/audio, stale mix, and corrected picture revision. The score and audio recipe are the same for both picture versions. Both exact test pictures travel in the skill package. The repository review folder records their hashes and measured results.

### Landmark and cue fields

| Field | Meaning |
| --- | --- |
| `landmarks` | Map from shared event IDs to independent visual detectors. The shared scene's `timeline.events[].frame` is useful for choosing frames to inspect. Detector input contains a visual predicate and can run again without that frame number. |
| `roi` | Normalized `[left, top, width, height]` in the stored picture orientation. Pick a region that changes in a recognizable way. |
| `color`, `tolerance`, `min_fraction` | RGB target, maximum channel difference, and minimum fraction of crop pixels matching. Useful for a bubble or newly revealed component. |
| `template`, `template_roi`, `max_distance` | Template image path relative to the plan, optional normalized crop if it is a full frame, and maximum mean RGB distance on a 0–1 scale. Useful when a unique icon or pattern defines the state. Choose either color or template. |
| `settle_frames`, `allow_initial`, `search_s` | Minimum consecutive matching frames, optional initial frame match, and optional broad picture-relative search range for repeated visible states. The detector returns the first frame of the qualifying run and fails on zero or multiple qualifying transitions. Search bounds identify a shot and account for possible edits. |
| `id`, `event`, `purpose`, `source` | Unique cue ID, event ID, editorial purpose, and source provenance. For a wall-clock bed, provide `time_s` in place of `event`. Set up a visual landmark for any sound whose timing matters to an action. |
| `bus`, `asset`, `gain_db` | One of `dialogue`, `music`, `atmosphere`, `effects`; source path relative to plan; and its gain. Adjust overall bus gain via the optional top-level `bus_gain_db` object. Prepare any source fades, pans and loops in the source recipe or edit. |
| `offset_samples` or `offset_ms` | Signed offset of the cue's impact from the decoded event. Use integer `offset_samples` to carry a shared `offsetSamples` exactly when the marker represents the same synchronization point. |
| `onset_ms`, `impact_ms` | Markers relative to source zero. Asset start is decoded event sample plus signed offset minus source impact. The decoded waveform check estimates where both authored markers landed. |
| `tolerance_ms`, `search_ms`, `fingerprint_ms`, `min_correlation` | Impact timing tolerance and larger search radius, optional two-element source time range for identifying a distinctive sound, and normalized match threshold. Choose a unique transient with at least 12 ms of usable audio. The default picks the most energetic 80 ms of the filtered source. |
| `silence` | Optional array of planned quiet ranges with `start_s`/`end_s` or `start_event`/`end_event`, `purpose`, and an optional `max_peak_dbfs` defaulting to −55. Leave encoder margin between a loud cue and exact digital silence. |

For a fade or gradual motion, define the visible threshold with the filmmaker and check neighboring frames. If a recrop or redesign changes what is visible, reauthor the detector from the picture and inspect the resolved boundary. Local RGB/template checks can drift as artwork changes. A repeated visual motif needs a distinctive crop or a broad, independently established shot window. Repeated or buried audio needs a recognizable fingerprint. If the final mix makes one indeterminate, revise the cue or get a timed audition before approving that sync point.

## Render, exchange and remap

```sh
python3 "$S/sound.py" resolve score/plan.json picture.mp4
python3 "$S/sound.py" mix score/plan.json picture.mp4 work/cut-01
python3 "$S/sound.py" verify score/plan.json picture.mp4 work/cut-01/mix.mp4 \
  work/cut-01/manifest.json --report work/cut-01/verify.json
```

Use a zero-start H.264 MP4 with one full-frame video stream and a positive duration. Conform other formats in the renderer before scoring. Existing media with a reference or mix requires explicit replacement. All four stereo 48 kHz float WAV stems start at sample zero and end on the same picture boundary. `mix.wav` is their sum. The mux copies picture packets and encodes 48 kHz stereo AAC. The manifest binds the plan, source assets, measured landmarks, mix WAV and MP4 to the exact picture SHA-256.

When a new cut arrives, preserve the prior export. Compare version hashes, run `resolve` on the new picture, inspect neighboring frames for changed landmarks, and compare cue offsets. Remap event-bound cues by running `mix` with the new picture and a new output directory. Check fixed-time beds and quiet holds against the revised scene, adjust the source edit when needed, and rerender. Review both picture and audio from the newly encoded file.

`verify` decodes the MP4 to locate visible events independently of the cue sheet. It compares the muxed picture payload and presentation timestamps with the handed-off master. It finds each distinctive cue waveform in decoded AAC, compares its impact with the visible event plus the authored offset, and reports early, late or missing cues. It also checks the stream profile, audio start and duration, decoded audio frame continuity, clipping, quiet passages, plus substantial energy drops or changes relative to the approved PCM. A ±48-sample stream duration allowance covers MP4 rounding. Decoded AAC may expose up to 1,024 samples of final frame padding. Estimated true peak uses 4× oversampling. A wall-clock bed receives continuity and dropout checks. For timing acceptance, bind the bed's distinctive story beat to a visual landmark.

Deliver the plan, source recipes or assets, separately editable stems, mix WAV and MP4, verification report, updated listening notes, and exact SHA-256. Keep old timings alongside the revised timings in the evidence. Split tracked review payloads above 24 MiB in repository archive style and verify the rejoined hash. In the team issue, include the pushed commit, run command and expected result. For a cold retiming check, supply the skill, old plan and a new silent cut with no moved-event hint.

## More examples

- Run `python3 "$S/quality_controls.py" /tmp/imv-sound-quality` for encoded stream, clipping and gap controls.
- The [silent-master examples](masters/README.md) cover independent sound design, source classification and five renderer smoke checks in the complete repository.
- See [source studies](SOURCES.md) for the six pinned repositories, primary tool documentation, and the measured failure in the historical checker.
