# External research: HyperFrames + Serena Launch archive (lead study, 2026-11-18)

Sources: github.com/heygen-com/hyperframes (86k*, Apache-2.0), github.com/serenakeyitan/awesome-ai-clonable-launch-videos (MIT). Studied docs/skills only; nothing installed.

## HyperFrames — what to borrow

Product: "Write HTML. Render video. Built for agents." HTML/CSS + seekable paused-timeline animation → deterministic MP4. Ships 9 agent skills; the transferable patterns:

1. **`/reverse-any-video`** (their recreation skill — closest analog to ours):
   - Probe decides the frame: composition size = source exactly, `data-fps` rational (NTSC kept as fraction), duration = frames ÷ fps (not audio length).
   - `measure cuts <video>`: every cut incl. jump cuts/punch-ins ffmpeg scene-score misses. Times written as `frame ÷ fps` **floored** — "2.767 lands a frame late". Same defect class as our Poke 12-frame-late selection.
   - Sound = the original played as one `<audio>` over the film; all clips muted.
   - Read *consecutive* frames around every change (cuts, entrances, exits, transitions ±few). "Sheets a second or quarter apart miss 1–3-frame timing, which way things enter/leave, blurs/dissolves, one-frame flashes."
   - Layer taxonomy: component (rebuild in HTML) | sub-asset (cut from original on its own box) | person (re-shot) | animated film. Never play the original's whole frame.
   - Verification: `diff <video> . --at t,t,t` while building; final `check` + render + `diff` which names missing/extra cuts, duration drift, sound offset, missing-content stretches, worst moments side-by-side. Fix what it names, re-render once, stop.
   - `REVERSE.md` handover: what's rebuilt/cut/re-shot, what's approximate, last diff numbers.
   - "One agent holding the whole film beats subagents that each re-watch it."

2. **`/hyperframes` core skill**:
   - Contract with `check --json` → violations each with a `Fix:` line (lint before render). Determinism contract: no Date.now/unseeded random/network/timers/repeat:-1 — everything f(timeline time).
   - Editability conventions: timed elements in HTML (not script-created), stable ids; copy/brand colors/media as variables; one kind per track; 90% action-safe / 80% title-safe areas.
   - Work loop: `timeline --json` (what plays when), `history --since mine` (user's changes), `snapshot --review` → REVIEW.md before delivery render.
   - New films: "three storylines that are three different films, in words only" → pick → SPEC.md (every adjective a number, banned defaults by name, shots by frame).
   - "Search the registry before hand-writing any named visual"; "show real things from their source; draw only what has none."

3. **`/hyperframes-registry`** (~450 blocks/components):
   - `catalog --query "<what the beat should do, in English>"` — local keyword tier + optional on-device meaning tier. `add <name>` installs EDITABLE SOURCE into the project (`compositions/<name>.html`) + prints mount snippet. Installed item is ordinary source — change/cut/restyle it.
   - Blocks (own timeline, mount by composition-src) vs Components (snippet merged into scene). Per-mount variables via `data-variable-values`.
   - Gap reporting: `catalog` prints a pre-filled `report_gap` feedback line when nothing fits — catalog self-improvement loop.

## Serena Launch archive — what to borrow

96 launch-video references, MIT. Entry = playable preview MP4 + one plain-language sentence of what happens visually + copyable "remake prompt" + source credit/date + metadata (duration, aspect, resolution, audio presence, stats). Six visual-taxonomy categories (Device & UI Transformations; Clean UI/Data/Graphics; Pastel UI & Cursor Demos; Typography & Abstract; Dark/Gradient/Mixed Media; Illustrated Mascot). Our six films appear in it (Poke, Photon/danieltian, PhotonHQ).

- `data/videos.json` canonical catalog; `agent/workflow.md` = remake instructions **live-loaded by the MCP tools at every call** — instructions versioned with the catalog, no reinstall needed. Tools: get_launch_context / search_launch_videos / get_launch_video / report_launch_task. Keyword (not embedding) search suffices at ~100-entry scale.
- Workflow's verification clause worth importing verbatim-in-spirit: audit reference & output frame-by-frame at matched resolution with overlays/diffs, watch each transition in MOTION, "never claim pixel-perfect fidelity without this comparison"; disclose remaining differences.
- Their default remake brief: "Clone this video for [product], pixel by pixel, 1:1 ... Replace only product-specific content; match composition, layout, typography and every animation/transition frame-by-frame including paths, zoom scale/origin, easing, timing and pauses."

## Where each idea lands in OUR skill (lead's mapping, applied at integration)

- Recreation: consecutive-frame reads around events + floor(frame÷fps) + event-boundary diff that names defects → recreation agent owns; integrate into `references/reconstruction-playbook.md` / new `references/recreate-quickstart.md` if proposals support it.
- Catalog: registry entries already ≈ their model (preview+description+frame range+editable impl); add "remake-in-one-line" usage string + gap-report convention + visual-category facet → catalog agent briefed to choose via experiments.
- Creative: "three storylines" + spec-numbers discipline already echoed in director/directing.md; keep, don't duplicate.
- Sound: "film >15s that tells something gets sound on visible actions" ≈ our ui-audio rules; verify sound agent's workflows align.
- Verification: encoded-export replay + frame-compare + heard-vs-measured honesty → observer's grading protocol.
