---
name: imessage-video
description: Recreate a whole reference film or one gesture, learn unfamiliar motion graphics into a persistent executable library, direct original iMessage films from a brief, and revise specific text, shots or movements using another reference. Use when someone sends a video, asks to save its movements or wants an iMessage film with storyboard and playable motion choices.
---

# iMessage Video

Act as the decision layer throughout production. Interpret what the viewer must see, inspect the actual input, choose a reusable movement and a single suitable renderer, then check the decoded result. A video attachment may be a target, inspiration, or a donor for one gesture. Multiple intents may coexist: a recreation of an unfamiliar film includes learning its motions.

## Start with the request

Run the following from the directory containing this file. Use an ordinary project directory for `JOB`. Use the user's chosen persistent library for `LIB`, or omit `--library` to use `assets/library` inside this skill. `IMESSAGE_VIDEO_MOTION_LIBRARY` can point every command at an existing shared library. Use the **same** library for recognizing, learning and replaying. Start with 77 bundled catalog entries: 75 core motions, one composite and one named variant. The default library also contains a separately learned switch whose thumb settles before its track finishes changing color.

```sh
python3 scripts/decide.py "the user's request" --video "$REF" --workdir "$JOB" --library "$LIB"
```

Omit `--video` for a blank brief. Add `--donor FILE` for a donor, `--project FILE` for an existing edit, and `--motion "what moves and what stays fixed"` for a shot-level search. Read the words in context. Pass `--intent recreate|learn|direct|edit` when the user's meaning is clear from the conversation or their language. Pass `--scope motion` for a particular passage. Ask one short question if choosing between two meanings would materially change the work. Carry out the returned workflow. A printed decision is the beginning of the job.

| User's intent | What to do |
|---|---|
| Recreate this swipe, shot, or whole film | Identify the exact scope. Return an already verified matching editable result when available. Otherwise perform intake and learning for missing coverage, recreate the requested passage, and compare its export with the original. |
| Learn the moves in this film | Find all distinct movements in scope. Split a camera move from an object moving under it. Reuse existing recipes where their behavior matches. Save and replay each genuinely new movement. Return its preview, editable source and when to select it. |
| Make an iMessage film | Resolve the audience, action and intended result. For a vague brief, ask whether the user has a reference and fill only consequential gaps. When they have none, direct from the catalog. With an inspirational clip, use the requested features in the new story. |
| Change this video, use this other move | Identify the target and donor separately. Open the current editable project, locate the precise shot/message and retain its identity. If all you have is video, recover the required editable layers first. Apply the copy or motion change, rerender, and check the surrounding unaffected passage. |

For each new goal or correction, repeat the shot decision. “Let me browse photos while the place name stays visible” calls for `photos-under-fixed-heading`. “Actually, show which message I’m answering” calls for `swipe-to-quote`. Show the new preview and explain what changes. In an original film, ask for approval on that revision. For an explicitly requested literal reconstruction, proceed using the reference.

## Recognize → measure → save → replay

1. Run the entry point with `--workdir` on each incoming reference. It identifies exact known source bytes and prepares a reusable frame inventory and a chronological overview for unfamiliar footage. If a pinned REA executable is available, set `IMESSAGE_VIDEO_REA` or `--rea-bin` to run local shot decomposition in the same intake. Set up REA and HyperFrames **once** per persistent machine/cache. Reuse existing checkouts and use only the needed parts. See [upstream commands and tool choices](references/upstreams.md).
2. Inspect coverage, not just identity. An exact known source with a verified whole-film project and master can be returned directly if the brief matches. For the six archived films, open the recorded scene and master and check their fit, including the sound requirement. A reused recipe covers its measured interval. A visually similar re-encode or excerpt is a candidate: align the frames and check the sound and changed regions before reuse. See [source recognition and registration](references/sources.md).
3. For new footage, inventory every requested shot and its distinct motions before synthesis. For each motion note frame bounds, moving and fixed layer IDs, occlusion, relative position/scale, camera, holds, easing samples, cue timing and when it is useful. Inspect original-resolution consecutive frames where the direction changes. REA's observations and sampled frames are a starting point. Motion meaning, shot boundaries and asset choices require the agent's visual judgment.
4. Search before authoring. `python3 scripts/recipes.py suggest "describe the intended change"` and `python3 scripts/learn.py --library "$LIB" list "search terms" --json` search the bundled and newly learned entries. `decide.py --motion` searches both. Inspect the moving and fixed layers, fit, exclusions, actual MP4 and code. Associate an already-covered motion with the new source through the verified seed binding in [sources](references/sources.md). Skip duplicate entries.
5. Author missing movements as editable layers and parameters. Use Pillow or the Node/SVG renderer for a portable learned scene and keep the chosen engine with its recipe. Use [the candidate format and replay instructions](references/learning.md). Run the following for each approved measurement. A failed comparison or a deliberate mistake that goes undetected leaves the candidate unpublished.

   ```sh
   python3 scripts/save_motion.py candidate.json "$REF" --frames FIRST:EXCLUSIVE_END --library "$LIB" --reviewed-by "actual reviewer"
   python3 scripts/learn.py --library "$LIB" replay MOTION_ID --out "$JOB/replay.mp4" --set 'parameter=JSON_VALUE'
   ```

   Use `--crop X,Y,W,H` for a measured component and retain the limits of that evidence. Verify that a fresh process can find the entry, change its content, and preserve which layers move. The saved motion includes its implementation, assets, preview, applicability, source span and frame evidence. The combined save also indexes the original film. If interrupted between publishing the motion and indexing the film, retry with identical inputs. For future isolated sessions, persist the added library entries and film records in the same private project or personal skill that owns them.
6. During recreation, build from those saved implementations and the measured shot plan. Check every learned interval is represented in the cut before declaring it complete. For an entire verified film, register the editable project, rendered master and full comparison as described in [sources](references/sources.md). A source match alone cannot certify every shot.

## Choose one implementation and verify it

Reuse the selected recipe’s working engine when it matches the requirements. For a new shot, nominate one engine for the hardest visible constraint with `python3 scripts/renderer.py --material raster|dom|timeline|react|vector`. Respect an explicit engine via `--required`. Python/Pillow suits pixel-based layers. HyperFrames and other browser timelines suit editable type and UI. An existing React, GSAP or Motion Canvas implementation may be the best choice for its own shot. Language preference alone cannot establish fidelity.

Render a short pilot covering entry, peak, settle and reading hold at the reference frame clock. Compare native frames and a meaningful ROI. Check actual text, actor, gesture, clipping, anchors and sound. If the first implementation passes, use it for the full film. If it misses an important feature, correct it or compare one alternative on the identical passage. `renderer.py --pilots pilots.json` accepts an array of `engine`, `report` (from frames.py), `visual_review` and `observation`; it chooses one passing candidate against common thresholds and ROIs. Only call a renderer verified once it produces the inspected output.

```sh
python3 scripts/frames.py "$REF" "$EXPORT" --out "$JOB/comparison" --require-structure-match --roi subject:X,Y,W,H --max-mae TOLERANCE
```

The report includes every presented frame, timestamps, source/output tails, region errors and the worst pair. Inspect consecutive frames around errors and verify the audio independently. Set the error threshold from the visible event and a deliberately wrong control. Record the actual result, including any remaining difference. See [frame review](references/frame-review.md). Never use reference footage as filler in an independently authored result.

## Direct and revise

Use [shot plans and edits](references/direction.md). Explain what each shot looks like, what the viewer learns and why the particular movement fits. Give the user its playable example and editable code. Use generated stills when composition or staging needs a picture; use real editable text/UI for judgments about iMessage behavior. Show the shot plan and obtain the user's approval before rendering an original full film. For revisions, update the named shot and its dependent transition, preserve other shots, and present the changed preview. Deliver the film, editable sources, and where the comparison passed or still varies.
