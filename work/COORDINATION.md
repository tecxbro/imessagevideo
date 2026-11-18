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
