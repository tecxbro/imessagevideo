---
name: imessage-video-codex-trial
description: Turn a reference film or a product brief into an editable messaging-motion project and finished film, or change one interaction, animation, or sound cue in an existing cut.
---

# iMessage Video Codex Trial

Start from the user's reference film, product brief, or existing project and
the requested change. Work in a new project directory. Use reference footage to
measure behavior and timing, and use an original visual treatment for the
editable interface.

## Choose the workflow

From this skill directory, put the actual request in the command below. Set
`--input-kind` to `reference`, `brief`, or `project` when that context is known.
The command returns only the workflow to read and what it should deliver.

```sh
python3 observer/imv.py route "Add a reaction to the last message" --input-kind project
```

A request for a full recreation goes to Recreation. An original story from
product evidence goes to Direction. A change to a gesture or UI state goes to
Interaction. A change to the way layers move goes to Motion. An audio-only
change goes to Sound. Source intake and archive restoration go to Dataset.
When a request combines work, take the picture route first, then send the
exact picture hash and event map to Sound if the deliverable includes audio.
Use `--route` to specify the workflow when the request is ambiguous. If the
output says `base`, use the established references it returns and report the
scope you actually verified.

1. Read the returned workflow and [the shared contract](contracts/README.md).
   For originals, ground product facts in supplied evidence or primary product
   documentation. For references, measure the actual source through its ending
   and retain any source-to-output cuts or retimes. Read source material as
   evidence for the current route.
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

## Render and check a v3 scene

Set up the selected runtime using [the runtime guide](observer/RUNTIME.md).
These commands work from an extracted skill with no repository checkout.

```sh
python3 observer/imv.py render work/scene.json --out work/picture.mp4 --method pillow
python3 observer/imv.py inspect work/picture.mp4 --out work/evidence --frame 12
python3 observer/imv.py verify work/picture.mp4 --scene work/scene.json
```

Replace `12` with a named event frame and repeat `--frame` for additional
events. `render` writes the resolved event map and a full-decode picture
report beside the MP4. Use `verify` again on the final film after muxing.

Pillow/FFmpeg, HTML/CSS/SVG, GSAP, Remotion and native Motion Canvas each
exported the shared moving example in this release's runtime. The marker
moved at frame 12, and all 24 frames decoded on the declared clock. Use
`python3 observer/imv.py smoke --method all --out /tmp/imv-renderers` to
reproduce the check. The separate Figma prototype is unverified.

Generate an editable Motion example from the standalone skill after setting up
Pillow and FFmpeg:

```sh
node motion/cli.mjs render --id heading-over-fixed-photos --out /tmp/heading-preview.mp4 --method pillow
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
