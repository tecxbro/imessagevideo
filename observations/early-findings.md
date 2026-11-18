# Early findings (Phase 1 reconnaissance)

Date: session start; sibling worktrees all still at base `c49482a`, no
`work/` or `handoffs/out/` content yet — builders are in their read/plan
phase. Findings about the library/skill itself below.

## 1. The "seed motion-catalog with 6 entries" does not exist at base
The brief describes `skill/imessage-motion-recreation/director/motion-catalog/`
with 6 seed entries. `git ls-tree -r HEAD | grep -i motion-catalog` → zero
hits at c49482a. The real existing catalogs are:
`director/catalogue.json` (14 measured studies, v2),
`director/motions.mjs` (9 authored starters), and
`director/source-studies/*.json` (3 rich recipe files).
→ The catalog agent is either expected to create `motion-catalog/` fresh,
or the effort brief mislabels an existing asset. Worth a lead-level check
so the catalog agent doesn't hunt for a phantom seed. (Handed off in
`handoffs/out/observer/`.)

## 2. Sparse checkouts are role-shaped — one possible miss
- recreate: full `projects/04-poke-complete-v1/` + fonts + authored fixtures ✓
- ui: full `05-linq` + `04-poke` projects + fonts ✓
- sound: `complete-ui-audio-source-v1` + later-workflow resources ✓
- catalog: all six `source.mp4` + `all-authored-source-and-fixtures-v1`,
  but **no `projects/*/scenes/*/scene.json`** — if the catalog is meant to
  be *source-backed with measured motion* (like the 14 existing studies,
  which cite canonical layer IDs and literal keys), it likely needs scene
  access or `sync_library.py` output. Flag for the lead.
- creative: no `resources/` at all (no fonts/audio pack) — fine for early
  direction work, needed before render/sound.

## 3. 02-danieltian's scene.json lives in STORAGE.json, not its project
The "Agent to Agent" scene is an oversized restore artifact — an agent
grepping `projects/*/scenes/*/scene.json` will find only 5/6 and may
conclude the sixth was never accepted. `python3 tools/sync_library.py`
is required; unsynced checkouts silently lack it.

## 4. Study coverage is thin outside teaching windows — known but quantified
14 studies cover 1,697 of 7,499 analyzed frames (22.6%). Per-film curated
windows: photonhq 204/655, danieltian 567/1360, mini 254/1260, poke 88/1283,
linq 230/1458, gallery 354/1483. For the chosen transfer test (03-photon-mini)
the three existing studies cover exactly its hardest sections (Uber Eats
sheet, world release) — a good baseline-vs-revised differentiator, since
the catalog agent's new entries would plausibly add this film's uncovered
sections (mosaic end card, email/doc flow, group-chat header).

## 5. Skill quality notes builders should internalize
- The honest-gap audit (`reports/SKILL-CONTENTS-AND-GAPS.md`) ranks the
  missing pieces; #1 is a shot/motion inventory of all six films — the
  catalog effort is the biggest lever on that.
- Documented failure pattern worth repeating to all agents: "a finished
  encoder is not proof of quality" — every builder should self-verify
  renders by decoding frames, not trusting ffmpeg exit codes.
- Starters are authored defaults with disclosed Arial fallback; production
  fonts live under `resources/font-inputs-and-linux-fallbacks-v1/` — agents
  without that sparse path will silently render fallback typography.
- Poke's 12-frame selection defect (src633→GSAP645) is *unfixed ground
  truth*; the recreate agent should treat reproducing-vs-correcting it as
  an explicit decision, not an accident.

## 6. Observation on ground-truth leakage risk
`catalog/index.html` + `inventory/` render every film's accepted MP4s.
For the transfer test these dirs must be stripped from trial checkouts
(or the agent could copy the answer). Already written into the protocol.
