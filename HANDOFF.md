# Codex motion catalog handoff

Tested implementation commit [`5e0065feb9cac0ab012fa48376d81566c220bdab`](https://github.com/tecxbro/imessagevideo/commit/5e0065feb9cac0ab012fa48376d81566c220bdab) on `film-trials/codex-catalog`. The catalog ships four editable motion examples. Each exposes its source or interaction reference, its moving and fixed parts, a default configuration, a moving preview and canonical scene export. [Motion library](skill/imessage-motion-recreation/director/motion-library/README.md)

## Playable examples

| Motion | Catalog preview | Fresh-agent recut |
| --- | --- | --- |
| One clipped strip of place photos beneath fixed copy and actions | [Saltwater House](skill/imessage-motion-recreation/director/motion-library/previews/place-photo-strip.mp4) | [Night Garden](reports/motion-catalog/blind/night-garden/night-garden.mp4) |
| Two swipes through overlapping conversation attachments | [Location scouting](skill/imessage-motion-recreation/director/motion-library/previews/messages-attachment-stack.mp4) | [Field Crew](reports/motion-catalog/blind/field-crew/field-crew.mp4) |
| A sheet rises over a dimmed conversation | [Draft in context](skill/imessage-motion-recreation/director/motion-library/previews/inline-card-expand.mp4) | |
| Portraits assemble around a shrinking, centered headline | [Scouting crew](skill/imessage-motion-recreation/director/motion-library/previews/avatar-ring-assemble.mp4) | |

The fresh agent matched all four specific requests and asked a clarifying question for bare “carousel.” It replaced the copy and eight images across the two recuts. The old planner's preserved wrong result was `message-wall`. The new catalog selects the attachment stack for the same brief. [Trial and exact prompts](reports/motion-catalog/blind/README.md) · [Old result](reports/motion-catalog/baseline-wrong-retrieval.json) · [Revised result](reports/motion-catalog/revised-retrieval.json)

## Search, preview, edit, render

Run from the checkout root. The renderer uses Node.js, Python 3.12, FFmpeg, and the existing pinned Pillow engine requirements. For Homebrew Cairo on macOS, set the library path in the second block. The search and stored previews run without renderer dependencies.

~~~sh
work=$(mktemp -d /tmp/motion-catalog-run.XXXXXX)
python3.12 -m venv "$work/venv"
"$work/venv/bin/python" -m pip install -r skill/imessage-motion-recreation/scripts/engines/requirements.txt
~~~

~~~sh
cli=skill/imessage-motion-recreation/director/cli.mjs
brief="Let's make a quick carousel for night market stalls. I want the pictures to glide sideways underneath Night Garden while the Hours and Get there buttons stay put."
node "$cli" motion search "$brief" > "$work/search.json"
motion_id=$(node -e 'const r=JSON.parse(require("node:fs").readFileSync(process.argv[1])); if(r.status!=="match") { console.error(r.question ?? r.status); process.exit(1); } console.log(r.selected)' "$work/search.json")
node "$cli" motion show "$motion_id"
node "$cli" motion preview "$motion_id" --out "$work/catalog-preview.mp4"
# View catalog-preview.mp4, then use the blind agent's edited config below.
if [ "$(uname -s)" = Darwin ] && command -v brew >/dev/null; then
  export DYLD_FALLBACK_LIBRARY_PATH="$(brew --prefix cairo)/lib${DYLD_FALLBACK_LIBRARY_PATH:+:$DYLD_FALLBACK_LIBRARY_PATH}"
fi
node "$cli" motion render "$motion_id" --config reports/motion-catalog/blind/night-garden/replacements.json --python "$work/venv/bin/python" --out "$work/night-garden.mp4"
~~~

Use [Night Garden's editable config](reports/motion-catalog/blind/night-garden/replacements.json) as the replacement example. Relative artwork paths resolve from the config directory. The render also writes `night-garden.scene.json`. The [blind trial](reports/motion-catalog/blind/README.md) has the Field Crew command and replacement files.

To open the original Linq beat locally, run `node "$cli" motion preview place-photo-strip --source --out "$work/linq-1091-1111.mp4"`. It extracts exactly the 21 decoded source frames. [Source intervals and observed layer behavior](reports/motion-catalog/README.md)

## Verification and dependency evidence

- The director suite passed 45 tests. FFmpeg decoded 600 frames across all six MP4s. Ordered frame sheets were visually reviewed. Both contextual renders rebuilt byte for byte in the same environment. [Export probes and hashes](reports/motion-catalog/preview-results.json) · [Blind render checks](reports/motion-catalog/blind/frames/verification.json)
- Fetched the Observer note at `262877b84fd153d8f6471a633ab71479cfe32d0d`. Its cold reading covers the Pinch Hit film and calls out where acceptance and the scorekeeper identity were inferred. [OBSERVER.md](https://github.com/tecxbro/imessagevideo/blob/262877b84fd153d8f6471a633ab71479cfe32d0d/OBSERVER.md)
- Fetched the UI trial at `ef83db187d7291a5d70f6dedb1f436f55b5abba3`. Its source checkpoints corroborate the venue-local rail and separate Mail sheet. Its Apple and Keiki references document the stacking rule and opened-stack swipe. The preview stages an authored inline peel. The native inline geometry and timing remain unverified. [UI attachment evidence](https://github.com/tecxbro/imessagevideo/blob/ef83db187d7291a5d70f6dedb1f436f55b5abba3/skill/imessage-motion-recreation/director/ui-trial/ATTACHMENT-EVIDENCE.md) · [UI handoff](https://github.com/tecxbro/imessagevideo/blob/ef83db187d7291a5d70f6dedb1f436f55b5abba3/HANDOFF.md)
- The three catalog source films passed the repository’s SHA-256 records. The 102 measured source frames passed the presentation timestamp check. Use `python3 tools/sync_library.py` with the tracked archive parts to restore the full film library. [Source verification](reports/motion-catalog/source-interval-results.json)
