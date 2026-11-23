# BUILDER-REPORT — t3: "two friends getting concert tickets"

Skill under test: `/Users/darshan/Documents/video-analysis/imessagevideo-dl/skill/imessage-video` (read-only, unmodified)
Python: `/Users/darshan/Documents/video-analysis/.venv/bin/python` (Pillow 13, numpy; +fonttools, +CairoSVG installed during setup — see Defects)
Library: `/Users/darshan/Documents/video-analysis/iv-test/library` (persistent; unchanged by this job — no learned entries authored)
Workdir: `/Users/darshan/Documents/video-analysis/iv-test/jobs/t3`

## Conversation log

### Beat 0 — entry (blank brief, no --video)

```
cd SKILL_DIR
…/python scripts/decide.py "Make an iMessage video about two friends getting concert tickets." \
  --workdir …/jobs/t3 --library …/library
```

Returned: `intent: "direct"`, `scope: "film"`, `next: "clarify_missing_brief"`,
workflow `establish_brief → search_library_for_each_shot → show_shots_with_motion_previews_and_code → review_direction_with_user → choose_one_renderer → prove_hardest_shot → render_approved_cut`,
guidance: "Use known answers first. Ask only about a missing story decision. With a vague brief and no reference, offer the choice to supply one once; an empty answer or no reference proceeds to the director and saved library." → correctly asked for missing brief details / offered to accept a reference.

### Beat 1 — user: "No reference — just make it. Two friends chatting about getting concert tickets."

- Re-ran `decide.py` with the literal reply first → `intent: "clarify"` ("make it" has no film/video noun; see Defects note 1). Re-ran with the brief plus `--intent direct --brief-ready` (the prescribed flag for context-clear meaning) → `next: "draft_shots_from_library"`.
- `recipes.py suggest "friend browses concert ticket options while the chat heading stays fixed"` → `action: "missing"` (ambiguous wording). Rephrased to describe moving vs fixed layers — `suggest "slide ticket option cards horizontally on a rail while the screen header stays fixed"` → `action: "retrieve"`, top match **`photos-under-fixed-heading`** (header stays pinned, photo rail slides; `photoCount` 2–12, editable `heading/detail/photos/direction`). Justification: the shot needs browsing under fixed context; the catalog note says to prefer it over stack-dismissal styles for "keep the header fixed as the rows move."
- Other picks: `conversation-handoff` (opening exchange; editable heading/copy/reply/detail), `reaction-attach` (celebration tapback; heading/copy/reply/action), `tear-perforated-ticket` (payoff — the secured ticket with detachable stub; heading/title/detail/action). `selection-confirm` rejected for payoff: `heading` is NOT editable — header renders hard-coded "Alpine field notes" (see Defects note 3).
- Authored 4 ticket-option cards (592×394, matches the 296×197 rail slot at 2×) with Pillow: `assets/ticket-{ga-floor,lower-bowl,balcony,vip-pit}.png` via `assets/make_cards.py`.
- Wrote `brief.json` (mode director, fps 30, confirmation true, 4 shots × 72 frames: `ask`, `browse`, `celebrate`, `ticket`).
- `shots.py create brief.json v1.json` → plan created.
- `shots.py render-shot v1.json <id> proof-<id>` ×4 → all 4 real previews, each 720×480 @30fps, 72 frames. (`ask`/`celebrate` initially failed on missing fontTools/CairoSVG — installed per engine requirements.txt, then succeeded.)
- Extracted `board-<id>.png` stills via `ffmpeg -vf select=eq(n,36)`; attached `{preview, code, board}` per shot via 4 `revise` calls → `v1-final.json`.
- `shots.py pitch v1-final.json --out pitch-v1.md` → pitch embeds each shot's board, project preview, scene code, the library motion example and its implementation. Header shows "**Director** · 30 fps · **awaiting confirmation**". Plan revision `45c906b58e0b1b2450e3c349aaa911c38428f7c03b6845f9ec521ebf7fcbc12b`.
- `check v1-final.json` → `confirmation_required: true, approved: false, open_work: {}`, exit 0. `check --for-production` → exit 1 (fails before approval, as required). Deliverable held at pitch awaiting approval.

### Beat 2 — user: "Actually, for the browsing shot — don't show browsing ticket options. Show which message I'm replying to instead."

- Per SKILL.md ("'Actually, show which message I'm answering' calls for `swipe-to-quote`") and catalog inspection, `swipe-to-quote` is the exact gesture: only the chosen bubble follows the drag, an arrow appears behind it, the row returns and a quote opens above the composer; other rows/header/composer fixed. No better catalog fit — `long-press-actions` shows a menu, not a reply target.
- Checked the recipe's layers: `copy` = the gray incoming bubble swiped/quoted; `reply` = earlier blue outgoing message; `title` = draft label. Revised `browse` (kept id + 72 frames):
  - purpose → "Show exactly which message is being answered before the reply sends."
  - motion → `{kind: seed, id: swipe-to-quote}`; copy "YES. Get us in!" (Maya's message being answered), bindings `{heading: "Maya", reply: "Neon Pines tickets drop at 10 - grab us two?", title: "Replying to Maya"}`.
- `revise v1-final.json browse browse-revise.json v2.json` → `derived_from {revision: 45c906b5…, changed_shot: browse}`; stale board/preview/code auto-cleared on content change.
- `render-shot v2.json browse proof-quote` → fresh playable preview (frame 40 shows the bubble mid-swipe with the reply arrow). Extracted `board-quote.png`; re-attached media → `v2-final.json` (its derived_from records intermediate rev `a2f32008…`).
- `pitch v2-final.json --out pitch-v2.md` → `browse` section now shows "Swipe one message to quote it", playable `proof-quote/preview.mp4`, new bindings; other three shots preserved byte-identical. New plan revision `70b1910780e9d2dcdfc5f5a44b5408b8c6beb1d6e1c58900076b2453840fb8c5` (≠ v1 `45c906b5…` — revision changed as required).

### Beat 3 — user: "Looks good — make it."

- `shots.py approve v2-final.json 70b1910780e9d2dcdfc5f5a44b5408b8c6beb1d6e1c58900076b2453840fb8c5 approved.json --response "Looks good — make it."` — approved against the revision printed in pitch-v2.md; `approved.json` stores `{revision, response}`.
- `check approved.json --for-production` → `approved: true, open_work: {}`, **exit 0**.
- `render-shot approved.json <id> final-shots/<id>` ×4 → per-shot bundles (preview.mp4 + scene.json + content.json + render receipt).
- Concat (all sources already 720×480 h264 @30fps, 72 frames — no scale/pad needed):
  `ffmpeg -f concat -safe 0 -i concat.txt -c:v libx264 -pix_fmt yuv420p -r 30 film.mp4`
- `film.mp4`: h264, 720×480, 30fps, **288 frames**, 9.6 s. Spot-checked frames 36/108/180/252 — correct shot order and content (handoff → swipe-to-quote → reaction → ticket tear).

## Plan diff v1-final → v2-final

| shot | v1 | v2 |
|---|---|---|
| ask | conversation-handoff (unchanged) | same |
| **browse** | photos-under-fixed-heading; copy "Ticket options"→`heading`; bindings {detail, direction:left, photos×4} | **swipe-to-quote**; copy "YES. Get us in!"→`copy`; bindings {heading:"Maya", reply, title:"Replying to Maya"}; new purpose/visual; new preview/code/board |
| celebrate | reaction-attach (unchanged) | same |
| ticket | tear-perforated-ticket (unchanged) | same |

## Artifacts

- Briefs/plans: `brief.json`, `v1.json`, `v1-b/c/d.json` (media-attach chain), `v1-final.json`, `browse-revise.json`, `v2.json`, `v2-final.json`, `approved.json`
- Pitches: `pitch-v1.md` (rev `45c906b5…`), `pitch-v2.md` (rev `70b19107…`)
- Previews+scenes: `proof-{ask,browse,celebrate,ticket,quote}/` (preview.mp4, scene.json, content.json, *.render.json; browse proof also has assets/), `final-shots/{ask,browse,celebrate,ticket}/`
- Boards: `board-{ask,browse,celebrate,quote,ticket}.png`; film check stills `check-frame-{36,108,180,252}.png`
- Authored assets: `assets/ticket-*.png`, `assets/make_cards.py`; concat list `concat.txt`
- Deliverable: `film.mp4` (720×480, 30fps, 288f, 9.6s)

## Pass/fail notes

- PASS: blank-brief decide asks for brief details/offers reference; `--brief-ready` proceeds to director workflow.
- PASS: 4-shot plan with stable ids; browsing shot used `photos-under-fixed-heading` after a suggest-first check; authored photo bindings.
- PASS: real render-shot previews attached as preview/code/board; pitch shows playable choices + library example + implementation.
- PASS: pre-approval state "awaiting confirmation"; `check --for-production` exit 1 before approval, 0 after.
- PASS: goal change → swipe-to-quote via revise; revision hash changed; other shots preserved; fresh proof rendered.
- PASS: approval recorded only after the simulated user's reply, at the pitch's printed revision; film assembled in order at uniform fps/size.
- Deviation: none forced; `--intent direct` used once for the context-clear reply (skill-prescribed).

## Skill defects / issues found

1. **decide.py literal-reply parse (minor)**: the user reply "No reference — just make it. Two friends chatting about getting concert tickets." alone returns `intent: clarify` — "make it" lacks a film/video noun for `DIRECT`. Prescribed workaround (`--intent direct` for context-clear meanings) works; arguably a missed chance to accept conversational "make it" phrasing. Not a blocker.
2. **Missing Python deps on a minimal Pillow env (environment, documented)**: `render_pillow.py` needs `fontTools` (line 293, `path` bounds) and `CairoSVG`/`Inkscape` (line 321, vector fills). Conversation-pack scenes (bubble tails) fail without them; both are in `assets/seed/runtime/scripts/engines/requirements.txt`. Errors are explicit and remediable; installed `fonttools 4.68.0`, `cairosvg 2.9.1` into the venv.
3. **`selection-confirm` template copy leak**: `heading-copy` and card detail are not editable — header renders "Alpine field notes" regardless of bindings (verified by materializing with custom content). Rejected it for the payoff for this reason; worth flagging as a catalog fidelity limit for story-critical header text.
4. **Cosmetic**: on a failed render-shot, stderr shows ffmpeg "Error opening output …/tmpXXX/bundle/preview.encoding-N.mp4" lines from the cleaned-up temp dir while a sibling render proceeds — noise, no functional effect.
5. **Note**: `write_new` hard-links outputs and `render-shot` requires a fresh output dir — artifacts are immutable by design; reused names fail loudly (good), and each revise/attach step produced a new plan file (chain kept: v1 → v1-b…d → v1-final → v2 → v2-final → approved).
6. **Shared-checkout caveat (not caused by this run)**: `git status` shows `M skill/imessage-video/references/sources.md` (mtime 13:39, +5-line "Binding limits" paragraph). This builder issued no writes to the skill dir — all writes went to `jobs/t3`, `/tmp` and the venv — so the dirty file predates or is concurrent with this run. No other skill files were touched.
