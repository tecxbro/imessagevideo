# devin-bot delivery coordination (lead notes)

Base commit: c49482a (main == imv/motion-catalog at branch point). Delivery branch: `devin-bot`. main stays unchanged.

## Team map

| Agent | Worktree | Branch | Owns |
|---|---|---|---|
| observer | ../imv-wt/observer | devin-agent-observer | `observations/`, `handoffs/out/observer/` |
| recreate | ../imv-wt/recreate | devin-agent-recreate | `work/recreation/`, `handoffs/out/recreate/` |
| catalog | ../imv-wt/catalog | devin-agent-catalog | `skill/imessage-motion-recreation/director/motion-catalog/`, `skill/imessage-motion-recreation/director/cli.mjs`, `handoffs/motion-catalog-previews/`, `work/catalog/`, `handoffs/out/catalog/` |
| creative | ../imv-wt/creative | devin-agent-creative | `work/originals/`, `handoffs/out/creative/` |
| sound | ../imv-wt/sound | devin-agent-sound | `work/sound/`, `handoffs/out/sound/` |
| ui | ../imv-wt/ui | devin-agent-ui | `work/ui/`, `handoffs/out/ui/` |
| lead | ../imv-wt/lead | devin-bot | `work/` root, integration, `skill/` edits outside catalog dir |

Shared skill files (SKILL.md, components.mjs, component-contracts.md, directing.md, etc.) are edited ONLY by lead during integration, from agent proposals under `work/<role>/skill-proposals/`.

## Handoff protocol

- Each agent publishes `handoffs/out/<role>/STATUS.md` + topic files in its own worktree.
- Cross-agent reads are direct filesystem reads into sibling worktrees (read-only courtesy).
- observer picks the unfamiliar recreation film → `handoffs/out/observer/unfamiliar-choice.md`.
- creative announces picture-lock → `handoffs/out/creative/STATUS.md`; sound scores it.
- ui publishes gesture evidence → `handoffs/out/ui/gesture-evidence.md` for catalog.

## External research folded into this effort (lead)

Studied heygen-com/hyperframes and serenakeyitan/awesome-ai-clonable-launch-videos. See `work/external-research.md`.

## Integration log

- e86c5e5: sound agent integrated (10 commits) — all owned paths, reviewed claims verified (cue_check/kind_check catch planted defects; 04-poke demo score exported).
- Seed catalog fix: `director/motion-catalog/`, upgraded `cli.mjs`, `explorer-template.html`, `index.html`, `handoffs/motion-catalog-previews/` were uncommitted local work on user's imv/motion-catalog branch — copied into catalog worktree; they become tracked via catalog agent's commits.
- Scenes sparse-added to catalog/observer/creative (~210MB across 5 films; daniel scene is gitignored by design).
- Render env proven: vendored engines at main checkout `skill/.../scripts/engines` + CHROME_PATH=/Applications/Google Chrome.app/Contents/MacOS/Google Chrome; `--method html` renders real frames; `cli.mjs scene --motion` → render works end-to-end.
- LEAD-NOTES.md published to all 6 worktrees (render recipe + seed-state correction + house rules).

## Pending downstream triggers

- creative picture-lock → resume sound agent (agent_id 01a83efa) to score film-01.
- catalog/ui/recreate/creative completions → integrate each after review.
- revised skill integrated → resume observer (agent_id 1defd854) for: blind screening, catalog/UI challenges, baseline-vs-revised 03-photon-mini trial (protocol at observer:observations/trial-protocol.md; checkouts must exclude projects/03-photon-mini-complete-v1/, catalog/, inventory/).
- Final: fresh-session trials of the 3 user asks; install skill via tools/install_skill.py from a devin-bot checkout.
