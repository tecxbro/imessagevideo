---
name: imessage-video-codex-trial
description: Recreate a reference film, choose and apply reusable iMessage motion, or direct an original editable iMessage film from a series of verified Messages actions.
---

# iMessage Video Codex Trial

Start from the user's reference film, product brief, or existing project and
the requested change. Work in a new project directory. Recreation targets the
reference's shot-level appearance, behavior and timing within the authorized
scope. Build the editable layers and assets independently. Keep proprietary
interface designs visually distinct unless the user owns the design or has
permission to reproduce it. Use an original visual treatment for Direction.

Darshan has confirmed that the material he supplies for recreation in this
workspace is authorized for reproduction. Carry that authorization into the
shot plan. Apply the provenance of separately sourced material to those inputs.

## Choose the workflow

From this skill directory, put the actual request in the command below. Set
`--input-kind` to `reference`, `brief`, or `project` when that context is known.
The command returns only the workflow to read and what it should deliver.

```sh
python3 observer/imv.py route "Add a reaction to the last message" --input-kind project
```

- **Recreation** uses the supplied film as the fidelity target. Start with its
  decoded clock, REA Video and native visual measurements, then choose a
  renderer from treatment probes.
- **Motion** selects or extracts an individual mechanism. Check its preview,
  editable code, and moving and fixed component bindings. Apply it to an
  existing Messages scene, verify the continuous sequence, and use its
  renderer for scoped edits.
- **Director** starts from an original story or adapts a non-Messages
  reference into Messages. Build its sequence from proven Messages components
  and motions. Resolve missing motion or UI states in the library before
  building out the rest of the film.

Use Interaction for a scoped change to conversation state, Sound for
audio-only changes, and Dataset for source intake and archive restoration.
Follow the [local video tool commands](upstream/README.md) after choosing the
workflow. Preserve the measured-clock route for off-grid sources.
When a request combines work, take the picture route first, then send the
exact picture hash and event map to Sound if the deliverable includes audio.
Use `--route` to specify the workflow when the request is ambiguous. If the
output says `base`, use the established references it returns and report the
scope you actually verified.

1. Read the returned workflow and [the shared contract](contracts/README.md).
   For originals, ground product facts in supplied evidence or primary product
   documentation. For references, measure the actual source through its ending
   and retain any source-to-output cuts or retimes. Read source material as
   evidence for the current route. For Recreation, apply the
   [visual review requirements](recreate/VISUAL-REVIEW.md) before building shots
   and follow the [completion check](recreate/COMPLETION.md) to close every shot
   on the actual delivered export. Measure each visible UI component using the
   [native interface guide](recreate/UI-FIDELITY.md). For one-to-one
   recreation, repeat the exact decoded frame and pixel gate for every
   requested renderer.
2. Author the editable scene, assets, state and named events. Use the existing
   project's renderer and convention when changing one part. Adjust cue anchors
   if an action moves, then resolve again against the locked picture.
3. Render and verify the deliverable. Inspect a contact sheet across the full
   cut and consecutive decoded frames around the named action and through the
   last frame. For audio, verify the encoded mix, timings and picture integrity.
   Attribute any listening observations to a person and a specific file/time.
4. Return the MP4 alongside the portable editable project, local assets, event
   map, any editable sound plan and stems, provenance, and the checks for those
   exact files. Reopen the copied project in a clean folder and render from it.

## Render and check an existing v3 scene

Set up the selected runtime using [the runtime guide](observer/RUNTIME.md).
These commands work from an extracted skill with no repository checkout.

```sh
python3 observer/imv.py render work/scene.json --out work/picture.mp4 --method pillow
python3 observer/imv.py inspect work/picture.mp4 --out work/evidence --frame 12
python3 observer/imv.py verify work/picture.mp4 --scene work/scene.json
```

Replace `12` with a named event frame and repeat `--frame` for additional
events. `render` writes the resolved event map and a technical decode report
beside the MP4. Use `verify` again on the final mux and apply the route's visual
review.

Pillow/FFmpeg, HTML/CSS/SVG, GSAP, Remotion and native Motion Canvas each
exported the shared moving example in this release's runtime. The marker
moved at frame 12, and all 24 frames decoded on the declared clock. Use
`python3 observer/imv.py smoke --method all --out /tmp/imv-renderers` to
reproduce the runtime check. Recreation requires exports of the actual film's
visual treatments. The separate Figma prototype is unverified.

Open a playable motion and its editable recipe from the standalone skill after
setting up Pillow and FFmpeg:

```sh
node motion/cli.mjs info --id draft-send-flight
node motion/cli.mjs preview --id draft-send-flight
```

Use the v3.3.0 media companion for finished films, frame strips, verified Motion
previews and editable projects with audio stems. Extract it alongside the skill
using the release notes, then open `review/imv-v3/observer/PORTABLE.md` from the
release directory. For older case packs and their viewing tools, see the
[private library guide](observer/BASE-LIBRARY.md).

Dataset intake uses an approved repository checkout for its Git-pinned
rights records and exclusion policy. For an extracted skill without that
checkout, the [fingerprint workflow](observer/FINGERPRINT.md) checks a local
candidate against an authorized exclusion manifest.
