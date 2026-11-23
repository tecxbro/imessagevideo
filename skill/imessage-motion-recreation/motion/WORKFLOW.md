---
name: imessage-motion-library
description: Choose, inspect, extract, and apply editable motion to Messages scenes.
---

Start in `skill/imessage-motion-recreation`. Describe what changes, what must stay anchored and what the viewer should notice. The [catalog](catalog.json) has 77 playable entries for 75 distinct motions, including one composite and one variant. Read the source ranges and provenance. Some entries carry a measured source track, while others are authored mechanisms or adaptations.

`info` gives the preview, editable implementation, supporting assets, moving actors, local anchors and event targets. Its production mapping states which Messages components an adapter recipe requires. A primitive such as a mask, chart count or camera move can be reused inside a composition after it is attached to the chosen scene's layers and verified there.

```sh
node motion/cli.mjs select --brief "Move the photos beneath a fixed heading"
node motion/cli.mjs select --brief "Hold the photos still while the heading moves"
node motion/cli.mjs info --id heading-over-fixed-photos
node motion/cli.mjs preview --id heading-over-fixed-photos
node motion/cli.mjs preview --id heading-over-fixed-photos --frame 30 --out /tmp/photo-motion-frame-30.png
node motion/cli.mjs render --id heading-over-fixed-photos --out /tmp/gallery.mp4
```

The first brief selects a clipped rail with an anchored heading. The second selects a moving title above stationary image crops. Play the selected MP4 or extract its decoded frame by index. A checkout without the published clips renders the preview locally and reports the new hash, scene and event map.

- **Retrieve** uses a matching recipe.
- **Adapt** recommends an editable change. `render --brief ...` applies its structured values, and your `--content` file can override them.
- **Combine** suggests successive beats. Pass the brief to `render`, or use `--ids ID1,ID2` for a sequence of cuts. A reading hold within a selected sequence freezes the adjacent shot for one second.
- **Hold** means the intended beat needs quiet reading time. Keep the current scene's image and timing.
- **Missing** states which requested relationship or mechanism needs a new recipe.
- **Inspect** opens a selected preview for playback or frame seeking.

Write replacement copy and artwork to a JSON file, then pass it with `--content`. Use `info` for field types and entry-specific photo limits. The inverse heading entry takes one or two photos. The photo rail takes two through twelve. File paths resolve from the content file. Use short text when replacing labels and keep evidence such as the send or reply readable.

```json
{
  "heading": "Workshop crew",
  "copy": "Can you open the west entrance?",
  "reply": "It is open. Use the ramp.",
  "detail": "Event operations"
}
```

```sh
node motion/cli.mjs render --id conversation-handoff --content /tmp/workshop.json --out /tmp/workshop.mp4
node motion/cli.mjs scene --id conversation-handoff --content /tmp/workshop.json --out /tmp/workshop.scene.json
```

The default uses Pillow and FFmpeg. Set `MOTION_PYTHON` to the Python executable with the [pinned dependencies](../RUNNING.md). Use `--method html`, `gsap`, `remotion` or `motion-canvas` to select another installed engine. The default MP4s decode at 720×480 and 30 fps. Renderer evidence distinguishes complete previews from nine-frame probes. Set `--fps` to 24, 25, 30 or 60 and `--duration` to 1.6–12 seconds per motion. After changing timing or content, check the consecutive frames where each relevant event first affects the picture.

## Bind a motion to Messages

Start from an editable conversation and its existing event IDs. Choose the
recipe by action and by the components it moves and holds. Specify the event
changes in a binding file. This send uses an existing typed draft and moves the
send and its anchored cue to frame 24.

```json
{"events":[{"id":"ui.send-keyboard.send","frame":24,"durationFrames":14}]}
```

```sh
node motion/cli.mjs apply --id draft-send-flight --project ui/examples/send-keyboard.json \
  --binding /tmp/send-motion.json --out /tmp/send-motion-project
python3 observer/imv.py render /tmp/send-motion-project/scene.json \
  --out /tmp/send-motion-project/picture.mp4 --method pillow
python3 observer/imv.py inspect /tmp/send-motion-project/picture.mp4 \
  --out /tmp/send-motion-review --frame 24
```

`apply` returns the editable conversation, compiled scene, resolved events,
and bindings to the actual scene graph. Review decoded before, onset and
settle frames, including the required fixed components. Use the existing
renderer and approved appearance of a project. Give Director a sequence of
these in-context actions and declared holds on one picture clock only after
the selected motions and UI states are proven.

## Extract source motion

Use the Recreation source ledger to select an inclusive native frame window.
Name the actor and provide a crop and RGB tolerance for a separable landmark.
`extract` writes each native frame crop and its hash, exact source PTS,
visible bounds, centroid and missing observations.

```json
{"tracks":[{"id":"outgoing-bubble","start":14,"end":23,"rect":[20,60,350,400],"rgb":[0,122,255],"tolerance":18}]}
```

```sh
node motion/cli.mjs extract --source /path/to/reference.mp4 \
  --plan /tmp/landmarks.json --out /tmp/motion-observations
```

Inspect the ordered crops to resolve overlaps and low contrast. A color
threshold can lose a fading component before it disappears. Keep those
frames unresolved until you measure the actual actor with another landmark,
a registered contour or a labelled manual sample. Record onset, intermediate
poses, clipping, final hold, and uncertainty before authoring a reusable track.

## Render a catalog study with the shared conversation UI

Use `--ui` with a catalog entry that lists an adapter variant. The motion compiler sends editable messages, assets and frame-addressed actions through Clone iMessage UI. The adapter owns layout, transit clips and interaction behavior. The local recipe and adapter give you two editable treatments where timing or styling differs, with separate exact previews and event maps.

```sh
node motion/cli.mjs render --id conversation-handoff --ui --content /tmp/workshop.json --out /tmp/workshop-ui.mp4
node motion/cli.mjs render --id photos-under-fixed-heading --ui --out /tmp/attachment-ui.mp4
```

If `ui/` lives in a separate checkout, use `--ui-root /absolute/path/to/skill/imessage-motion-recreation`. For the pinned version used in the review files, `git archive 5e2ff5a skill/imessage-motion-recreation/ui` yields the adapter from its fetched ref. Unpack it into a working directory and pass the skill directory as `--ui-root`.

For attachment browsing, see the [photo swipe comparison](PHOTO-SWIPE.md) and its portable inputs. It shows the venue rail, the overlapping stack and the adapter’s send, page, viewer and return sequence.

Render produces an MP4, an editable `.scene.json` and an `.events.json` with the shared frame clock. `scene` produces the same editable scene and event map without encoding. For programmatic inspection use `buildMotion` from [scene.mjs](scene.mjs), `buildUiMotion` from [ui-bridge.mjs](ui-bridge.mjs) and `describeMotionComponents` from [components.mjs](components.mjs). Use [composeScenes](sequence.mjs) for preview reels or deliberate hard cuts. It resets UI state at cuts and prefixes each occurrence's layer, event and cue links. Keep a production conversation continuous through its editable event sequence.

Read [source provenance](SOURCES.md), the [observed-only inventory](observed.json) and the [review evidence](../../../review/imv-v3/motion/README.md) for limits and reuse results. Selector tests include unfamiliar wording, negation, invariant layers and near matches.

```sh
node --test motion/tests/*.test.mjs
```

## Count between two totals

`metric-count` updates the displayed value in place while the label and heading hold. The settled event is the first frame showing the final value. Use `values` for two distinct whole numbers, `copy` for the metric label and `detail` for an optional unit. The selector can fill these fields and run the recipe with `render --brief`. A rolling numeral treatment lives under `metric-wheel-roll`.

When the brief leaves the endpoints unspecified, supply the actual values in a content file. This command uses the editable [counter input](examples/metric-hold.json).

```sh
node motion/cli.mjs render --brief "Show a count climb to the real total then give the statistic time to read" \
  --content motion/examples/metric-hold.json --out /tmp/metric-hold.mp4
```
