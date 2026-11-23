# INDEPENDENT REVIEW — t4 edit request

Request under test: "Change this message to 'Meet at the doors' and replace this shot's motion with the swipe from this second clip."
Artifacts reviewed: `iv-test/jobs/t4/` (plan chain, film-v2.mp4, evidence), baseline `iv-test/jobs/t3/`, donor `iv-test/donor-swipe.mp4`, library `iv-test/library`.
Method: own diffs, own ffmpeg/Pillow decoding and measurement (`review/t4/measure.py`, `review/t4/frames/`), own runs of `shots.py check` and `sources.py identify`. Report prose not trusted.

## Per-item results

### a) Plan diff — PASS (with two disclosed extras)
- `approved.json → plan-v0`: only `confirmation: true→false` and `approval{}` dropped. **This is a plan-level change beyond the two edit fields** — but the builder disclosed it prominently ("Confirmation choice") and it is what makes `check --for-production` pass without a fabricated approval.
- `v0→v1`: `ask.copy` "Neon Pines tickets drop at 10 - grab us two?" → `"Meet at the doors"` — exact string in plan (verified byte-exact in JSON) **and** in `final-v2/ask/content.json`. Stale `preview/code/board` auto-cleared.
- `v1→v2`: `ticket` shot — `motion.id` tear-perforated-ticket → **seed `photos-under-fixed-heading`**; bindings → `heading:"Maya", direction:"left", photos:[4× assets/ticket-*.png]` — all 4 PNGs exist on disk; **also** `copy`, `copy_key` (title→detail), `purpose`, `visual` changed — more than "motion + bindings", but disclosed in the report's patch table and required to repurpose the shot.
- `v2→v3`/`v3→v4`: only re-attach of `preview/code/board` to `final-v2/*` for ask then ticket.
- Shot ids `ask/browse/celebrate/ticket` stable throughout; `frames:72` untouched; `browse`/`celebrate` shot objects byte-identical across all plans; `derived_from` chain updates each step (v4 parent rev `ed3bed62…`); `check` recomputes rev `e30eeb2e…` = the rev printed in pitch-v2.md.

### b) Decoded frames — PASS
- Frame 60 (ask): outgoing blue bubble literally reads **"Meet at the doors"**; reply "YES. Get us in!", "Maya" header, "iMessage - Today" footer unchanged. Diff vs t3 frame 60: 696 px >30 delta, bbox x165–482/y66–221 — localized to bubble glyphs.
- Frame 250 (ticket): a clipped horizontal rail of ticket cards (BALCONY centered, VIP PIT and a purple card peeking at edges) sliding under the **fixed "Maya" heading**, detail line pinned at bottom — the photos-under-fixed-heading gesture, **not** a ticket tear.

### c) My ticket-shot measurement (frames 216–287, own ROIs vs frame 216)
| ROI | box (x0,y0,x1,y1) | max MAE | verdict |
|---|---|---|---|
| heading | 115,50–605,100 | **0.0010** | static (encode noise) |
| rail | 115,130–605,340 | **43.16** | moves then settles at new state |
| footer | 115,392–605,435 | 0.0063 | static |
- Consecutive-frame MAE>0.5 on local frames **20–39** (film 236–255) — exactly the recipe's declared `rail-start@20`/`rail-settle@39` events (verified in `recipes.info`). Sub-threshold pauses at locals 21/26/31/36 = stepped easing.
- Builder's numbers (0.0008 / 41.33 / frames 236–255) confirmed — mine differ only by ROI-box choice.

### d) Boundaries — PASS
Decoded and inspected 70–73, 142–145, 214–217, 286–287:
- 70/71 ask settled (new copy) → 72/73 browse start. Clean.
- 142/143 browse end (quote draft "Replying to Maya / YES. Get us in!") → 144/145 celebrate (Love badge mid-flight→settling). Clean.
- 214/215 celebrate settled (Love badge on "You're the BEST!") → 216/217 ticket (GA FLOOR + LOWER BOWL rail). **No donor-motion bleed at 215**; 216 starts the gesture cleanly.
- 286/287 VIP PIT settled. Film ends correctly.

### e) Unaffected shots vs t3/film.mp4 (frames 72–215) — PASS
- Whole-frame per-frame MAE, n=144: **max 0.3197 (frame 119), mean 0.2251**. Worst cluster 117–122.
- Stronger check: v2's browse+celebrate segments vs the reused `baseline-final-shots/*/preview.mp4`: **max 0.000000, 0 nonzero pixels** — bit-identical decodes.
- Explained residual: t3's `concat.txt` used `-c:v libx264` (re-encode); v2 used `-c copy`. The 0.32 delta is entirely t3's own generation loss; v2 changed nothing in these segments. `baseline-final-shots` previews sha256-identical to `t3/final-shots` (943911a2…, 42782622…).

### f) Donor identity — PASS
My own `sources.py identify` run on `donor-swipe.mp4` (sha befaf0d9…): status `candidate` → **05-linq "Linq iMessage Apps"**, visual-sequence, 6 matched samples, input 0.0–3.0 s ↔ **catalog 35.0–38.0 s**, coverage archived-reconstruction, audio not compared. Decoded donor frames 30/60 confirm a restaurant page whose photo rail swipes under a fixed heading — the donated gesture is real and matches the applied recipe (measured-adaptation of 05-linq 36.367–37.067 s).

### g) Library hygiene — PASS
`entries/` contains only `jelly-settle-arrive`; `films/` one source record + lock; `projects/` only `unseen-doors`. `stat` on every file: newest mtime 13:24:55 — all before the t4 job window (13:46–13:50). No registrations, bindings, or entries added.

### h) Flagged nuance — CONFIRMED REAL (consistency gap)
Frames 100/140/142/143 (browse shot): the transcript's blue bubble still reads the **old** text "Neon Pines tickets drop at 10 - grab us two?" — i.e., `browse.bindings.reply` still carries the pre-edit copy while shot 1 now says "Meet at the doors". The quote draft itself quotes "YES. Get us in!" (the reply being answered), which is internally consistent with the baseline design. So the film now shows two different outgoing messages for the same ask across shots 1 and 2. Builder disclosed this as an out-of-scope observation in the report; it is real and visible in the delivered film.

## Additional integrity checks
- `film-v2.mp4` sha256 `c8457d89…`, h264 720×480@30fps, 288 frames — matches report.
- `final-v2/ticket/preview.mp4.render.json` cites 05-linq source 36.366667–37.066667 s; scene sha bb97a1c6; Pillow engine receipt present.
- `shots.py check plan-v4.json --for-production` re-run by me: exit 0, `confirmation_required:false, approved:false, open_work:{}`.
- Skill dir: `git status` shows only pre-existing `M references/sources.md` (mtime 13:39, predates this job) — consistent with builder's disclosure.
- t3 inputs untouched (shas match decide record: film `9b2fc1fb…`, donor `befaf0d9…`).

## DEFECTS / findings
1. **Consistency gap (real, disclosed):** shot 2's transcript still displays the old outgoing text "Neon Pines tickets drop at 10 - grab us two?"; shot 1 now says "Meet at the doors". The two shots contradict each other in the delivered film. Builder flagged it; within literal edit scope but a viewer-visible inconsistency.
2. **Plan-level mutation beyond the "two fields" framing:** `plan-v0` also flips `confirmation→false` and drops the baseline `approval`. Deliberate and disclosed; it is also the sole mechanism by which `--for-production` exits 0 with `approved:false`. Not a defect in execution, but worth noting that the "only X changed" claim applies to shots, not the plan header.
3. **Ticket shot changed more than motion+bindings:** `copy`, `copy_key`, `purpose`, `visual` were also rewritten — all disclosed in the patch table; semantically necessary to repurpose the shot. Documentation nuance only.
4. Minor: motion contains 4 sub-threshold micro-pauses inside the 20–39 window (locals 21/26/31/36) — consistent with eased steps, matches builder's own per-frame data; no issue.

## VERDICT: PASS

Every material claim verified independently: exact copy edit rendered in shot 1; ticket shot performs the donor's photos-under-fixed-heading gesture (heading static ≤0.001 MAE, rail moves 43.16 max, on recipe frames 20–39); clean cuts at all boundaries; unaffected segments bit-identical to reused renders (≤0.32 MAE vs t3 film = t3's own re-encode loss); donor correctly identified as 05-linq @35–38 s; library untouched. The one substantive caveat is the disclosed cross-shot inconsistency (old message text still quoted in shot 2) — flagged, not judged.
