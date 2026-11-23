# Local film workflow

Use Python 3.12, FFmpeg and ffprobe, Node.js 22.19 or later, and a local
Chromium or Chrome executable. Messages authoring also needs Fontconfig and
DejaVu Sans regular and bold. Run from the skill directory.

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r upstream/runtime/requirements.txt
npm ci --prefix upstream/runtime
export IMV_REA_VIDEO="$PWD/.venv/bin/rea-video"
export HYPERFRAMES_BROWSER_PATH="/path/to/local/Chrome"
PY="$PWD/.venv/bin/python"
```

Use `IMV_NODE_RUNTIME` to point to an alternate install of the npm lockfile.
There are no desktop app or account prerequisites. The wrapper disables
HyperFrames telemetry, update checks and global skill changes. REA gets a
run-local preferences directory, explicit local OCR and tool analysis, and
no VLM or model-backed stem separation.

## Supplied reference

```sh
"$PY" upstream/film.py reference "$REFERENCE" work/intake
# Inspect the images listed in work/intake/rea/review_tasks.json and record observed answers.
"$PY" upstream/film.py apply-reference-review "$REFERENCE" work/intake
```

Open `rea/VIDEO.md` first, then the linked rhythm, shot and review files.
`shot-ledger.json` translates half-open upstream source windows into inclusive
review windows and supplies native PTS and the measured exclusive end. It
keeps uncertain source classifications open. Review cut neighborhoods and
split long spans into separate criterion windows when a component, action,
camera move or treatment changes. Sidehoe has nine upstream segments and 24
historical review windows across those segments.

For each consequential object, complete the shot's `layers` entries with
its ID, visible property and source frame, independent asset/build method,
and the intended probe and target. Link the evidence crop or consecutive
range. Preserve the distinction between a measured visible result and an
inferred method. Use [Recreation](../recreate/WORKFLOW.md) to lock the
review plan and run native probes. Source frames and analysis crops stay in
the intake directory. The renderer recommendation records whether the
measured picture fits the HyperFrames clock and geometry. For off-grid SDR
use the measured-clock encoder with independently authored indexed frames.
Resolve other display cases through a renderer-specific probe.

## Editable Messages project

Use [HyperFrames creation](../vendor/hyperframes/skills/hyperframes/UPSTREAM.md),
its [story brief](../vendor/hyperframes/skills/hyperframes/references/story.md),
and the [spec template](../vendor/hyperframes/skills/hyperframes/references/spec.md).
Verify product claims and identify the action the viewer needs to see using
[Direction](../direction/WORKFLOW.md). For local reuse, consult the copied
[number pop-in](../vendor/hyperframes/registry/components/number-pop-in/number-pop-in.html)
and the [registry skill](../vendor/hyperframes/skills/hyperframes-registry/UPSTREAM.md).

```sh
"$PY" upstream/film.py messages ui/examples/send-keyboard.json work/messages
"$PY" upstream/film.py recompile-messages work/messages
"$PY" upstream/film.py review work/messages work/messages-review
"$PY" upstream/film.py render work/messages work/messages.mp4
"$PY" observer/imv.py verify work/messages.mp4 --scene work/messages/messages.scene.json
```

Start with the conversation and bind its actions through the
[Motion library](../motion/WORKFLOW.md#bind-a-motion-to-messages). The
Messages route takes edit input in `conversation.json`.
It writes a seekable composition, the resolved event/cue map and local
fonts and images. Edit the conversation, then regenerate its composition.
The Messages event map is local to that composition. When mounting it
inside a larger film, resolve its offset from the host's output frame on
the same frame grid before scheduling film-level cues. A new Messages
canvas size, duration or rate requires a fresh scaffold. Include the source
font notices with fonts in the copied project. For an existing project,
continue using its own renderer, named layers and edit conventions.

## Review and delivery

`review` runs the upstream check and writes the beat, cut and 360 px sheets.
Review the weakest beat and the changed states in the decoded export. Add
`--reference "$REFERENCE" --candidate "$EXPORT"` to run upstream diff
against the encoded candidate. A diff failure keeps the diagnostic JSON
and images. Select the failing cuts and worst local cells as places to
inspect. For exact delivery, run [native acceptance](../recreate/COMPLETION.md)
on the final mux. Use the [Sound workflow](../sound/WORKFLOW.md) for picture
hash and encoded cue verification.

Record the technical decode and timing result, the editorial decisions and
open notes, and the source-fidelity verdict independently. Package the
project with its local assets, then reopen and render a clean copy.
