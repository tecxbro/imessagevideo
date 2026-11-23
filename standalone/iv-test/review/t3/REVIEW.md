# INDEPENDENT REVIEW — t3: "Make an iMessage video about two friends getting concert tickets."

Reviewer: independent. Method: re-ran entry point, recomputed plan revisions via `shots.py check`, diffed shot records, ffprobe'd every MP4, sha256'd proofs vs catalog, decoded and eyeballed film/proof frames. Builder report prose was not trusted.

Skill under test: `/Users/darshan/Documents/video-analysis/imessagevideo-dl/skill/imessage-video`
Job dir: `/Users/darshan/Documents/video-analysis/iv-test/jobs/t3`
Evidence in this review dir: `frames/` (decoded film + proof PNGs), `decide-run*/` (my own decide.py runs).

## Per-claim verdicts

### 1. Entry point → intent=direct, next=clarify_missing_brief — PASS
Re-ran myself:
`decide.py "Make an iMessage video about two friends getting concert tickets." --workdir review/t3/decide-run --library iv-test/library`
Output: `intent:"direct"`, `scope:"film"`, `next:"clarify_missing_brief"`, workflow `establish_brief→…→render_approved_cut`, guidance: "…With a vague brief and no reference, offer the choice to supply one once; an empty answer or no reference proceeds to the director and saved library." Matches claim.

### 2. Shot plan v1: 4 shots, seed motions, playable proofs, pitch, confirmation gate — PASS
- `brief.json`/`v1.json`: shots `ask`/`conversation-handoff`, `browse`/`photos-under-fixed-heading`, `celebrate`/`reaction-attach`, `ticket`/`tear-perforated-ticket`; each has purpose, visual, `motion:{kind:seed}`, copy+copy_key+bindings; `confirmation:true`, fps 30, 72 frames each.
- `proof-{ask,browse,celebrate,ticket}/preview.mp4` all probe h264 720x480, 30/1 fps, nb_read_frames=72 (real files, not stubs).
- `pitch-v1.md` exists, header "**Director** · 30 fps · awaiting confirmation", links preview/code/board per shot + seed "Motion example"/"Implementation"; every link path verified to resolve on disk (incl. `../../../imessagevideo-dl/...` seed files). Printed revision `45c906b5…bc12b`.
- Recomputed `check v1-final.json` → revision `45c906b5…` (matches pitch), `confirmation_required:true, approved:false, open_work:{}`; `--for-production` exit **1** (gate holds before approval).

### 3. Goal change: browse → swipe-to-quote, only that shot touched — PASS
- `v2.json` `derived_from = {revision: 45c906b5…, changed_shot: browse}` — provably derived from the pitched v1-final revision.
- browse: motion `photos-under-fixed-heading`→`swipe-to-quote`; new purpose/visual; copy `YES. Get us in!` with `copy_key:copy`; bindings `{heading:"Maya", reply:"Neon Pines tickets drop at 10 - grab us two?", title:"Replying to Maya"}`; stale preview/code/board auto-cleared (fields absent in v2.json).
- ask/celebrate/ticket records JSON-equal between v1-final.json and v2-final.json (and vs approved.json). Verified programmatically.
- `proof-quote/` is a fresh render (receipt `method:pillow`, staging path `jobs/t3/tmp…/bundle`, `sceneSha256` == sha256 of shipped `proof-quote/scene.json`); content.json = plan bindings. `pitch-v2.md` prints new revision `70b19107…f8c5`, browse section shows "Swipe one message to quote it" + new bindings, links to proof-quote which resolves.
- Decoded `proof-quote` frame 40: gray "YES. Get us in!" bubble mid-drag with blue ← reply arrow; frame 60: "Replying to Maya / YES. Get us in!" quote bar above composer. Real swipe-to-quote render of plan copy.

### 4. Approval beat: bound to v2 revision + recorded response; gate passes — PASS
- `approved.json` `approval = {revision:"70b19107…f8c5", response:"Looks good — make it."}` — the exact revision printed in pitch-v2.md and recomputed by `check`.
- Re-ran `check approved.json --for-production` → `approved:true, open_work:{}`, **exit 0**.
- `check v2-final.json --for-production` (pre-approval same content) → `approved:false`, **exit 1**. Gate behavior exactly as claimed.
- Plan inside approved.json is JSON-identical to v2-final.json (all 4 shots), so nothing was swapped post-approval.

### 5. Film: concat of 4 approved renders, correct specs + content — PASS
- `film.mp4` probes: h264, 720x480, 30/1 fps, **288 frames**, 9.6 s, single video stream (no audio — consistent with the silent seed packs; not claimed otherwise).
- `concat.txt` lists `final-shots/{ask,browse,celebrate,ticket}/preview.mp4` in order; all four probe 720x480@30/72f.
- Decoded-frame MAE between film segments and the corresponding `final-shots` files ≈ **0.21/255** (re-encode noise; content identical). `final-shots/*/preview.mp4` sha256 == corresponding proof renders (`browse` == `proof-quote`), i.e. the film uses the approved swipe-to-quote render, not the old browse proof.
- Visual check (frames in `review/t3/frames/`):
  - f0/f36: conversation-handoff — iMessage transcript under "Maya" header, blue "Neon Pines tickets drop at 10 - grab us two?" flying in, "iMessage - Today" footer.
  - f72–143: **swipe-to-quote** — f96/f108 bubble mid-drag with ← arrow; f126 "Replying to Maya / YES. Get us in!" quote draft over composer. NOT photo browsing.
  - f180: reaction-attach — "Booked - two GA floor tickets" + "Love" badge landing, "You're the BEST!" gray bubble.
  - f252/f287: tear-perforated-ticket — "The Neon Pines / GA Floor - 2 tickets - Fri Jun 12", "Open" stub torn and dropped.
  - On-screen text matches approved plan copy/bindings exactly (Maya, Neon Pines, GA Floor, Jun 12, YES. Get us in!, You're the BEST!, Love, Open).

### 6. Library hygiene — PASS
`iv-test/library/entries/` contains only `jelly-settle-arrive`. Other files (projects/unseen-doors, films/source-8a77…, locks) pre-date the job (mtimes ≤13:33). No new entries authored.

### 7. Fabrication check — PASS
- All five proof preview sha256s differ from the catalog seed previews; scene.json files embed the plan's own copy strings ("YES. Get us in!" ×2 in proof-quote, "Ticket options"/"The Neon Pines" in proof-browse, etc.).
- proof-browse (v1) decoded frame shows the authored `assets/ticket-*.png` cards (BALCONY $64, VIP PIT) sliding under the pinned "Ticket options" heading — genuine render of plan bindings, not a catalog copy.
- Receipts' `sceneSha256` match shipped scene.json for all proofs.

## Defects / observations

1. **Minor (builder-visible, skill-level UX):** `decide.py` on the literal user reply "No reference — just make it. Two friends chatting about getting concert tickets." returns `intent:"clarify", next:"ask_intent"` — reproduced. Builder's workaround (`--intent direct --brief-ready`) is the skill-prescribed flag; acceptable.
2. **Cosmetic:** approved plan's top-level `brief` string still says "…the seating options get browsed under one pinned heading…" — it's the original brief record, not the shot; the actual shot 2 is correctly swipe-to-quote. No functional impact; note only.
3. **Environment note (not attributable to t3):** `git status` shows `M skill/imessage-video/references/sources.md` (+5-line "Binding limits" paragraph, mtime 13:39). Doc-only; `iv-test/jobs/{t1,t2}` exist, so a concurrent run plausibly wrote it. Does not affect any t3 artifact. Flagging because the skill dir was nominally read-only.
4. **Film has no audio stream.** Consistent with the silent bundled packs; claims didn't require audio. Noted for completeness.
5. No defects found in the artifacts themselves: no copied catalog proofs, no swapped plans post-approval, no fabricated checks — every gate result was reproduced independently.

## Overall verdict: **PASS**

All five claims verified against real artifacts. The conversation beats are genuinely represented: clarify (decide output) → v1 pitch with rendered playable choices + confirmation gate failing pre-approval → surgical browse-shot revision to swipe-to-quote with fresh proof and new revision → approval recorded at the pitched v2 revision → approved plan passing `--for-production` → film assembled from the approved renders with the revised shot in place.
