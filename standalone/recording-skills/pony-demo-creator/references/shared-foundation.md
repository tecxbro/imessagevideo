# Imported foundation and PONY execution

Use the unchanged source skills directly; do not copy an abbreviated replacement into a PONY skill. Keep the two authoring skills and four presentation recipes as adaptations around that foundation.

## Source responsibilities

| Imported source | Use in PONY |
| --- | --- |
| [Photon Demo Creator](../../photon-demo-creator/SKILL.md) and its HTML, company-analysis and conversation-design references | Follow the complete research/story/asset workflow for Deep. Instant uses the existing CRM reader/playbook; consult conversation-design for explicitly requested custom copy. |
| [Make iMessage Demo](../../make-imessage-demo/SKILL.md) | Consult original authoring, capability, timing and visual conventions. For Deep, load the full skill and its required references. Use current PONY contracts and command mapping for execution. |
| [Record iMessage Demo](../../record-imessage-demo/SKILL.md) | Apply complete-video, normal-playback, silent-output and visual-review policy to both modes. Use PONY's recording command for both presentations. |
| [Create iMessage Sheet App](../../create-imessage-sheet-app/SKILL.md), [sheet motion](../../recreate-imessage-sheet-motion/SKILL.md), [Apple Pay](../../recreate-apple-pay/SKILL.md) | Load only when the human's requested feature calls for them. Preserve their explicit-request gates and actual runtime limits. |

Follow [source provenance](../../../../docs/imessage-skills.md) for the pin and command mapping. Original files describe standalone commands as well as authoring policy; PONY adapters map those commands without rewriting the originals. Treat a missing PONY runtime capability as a limitation to resolve, not permission to invent a substitute.

## Distinguish the two authoring workflows

For **Deep**, run the complete imported company workflow: original research depth, default conversation count, asset provenance, full timeline authoring, separate company review and visual verification. Keep all authored timestamps, drafts, receipts, rich events and checkpoints. Use `write_deep_demo` for persistence and full-flow edits.

For **Instant**, run CRM Instant locally: the same bounded HTTP HTML reader (`browser:"never"`, up to five internal pages, 9000 ms, `llm:false`), industry playbook, pacing and validation. Provide company inputs to `npm run demo -- instant`; do not perform independent agent research or author replacement copy. Reuse an actual supplied cached profile, as the CRM does, or let the reader fetch it. Custom copy is an explicit `write_demo`-equivalent override, never the default for a company-only request. CRM persistence remains opt-in. If the user requires exact rich events/timing that Instant cannot express, explain the limit and ask whether to use Deep; do not silently switch.

For either mode, keep customer messages outgoing and business replies incoming, preserve exact supplied copy, and use supported content on the chosen channel. Do not import Spectrum provisioning, real-send handlers, mandatory mini-app endings or payment operations into a render-only request.

## Apply presentation independently

Use `plain` for Legacy. Use `collab` for New unless `brand` was requested. Pass style explicitly to creation and recording; pass the chosen channel explicitly. Keep the same authored flow when changing presentation. If both presentations are requested, reuse that conversation and record both; do not redo research or create duplicate CRM rows merely for an export.

For an existing local demo, read its mode/channel/style before editing. Read a CRM-saved demo only when CRM access was explicitly requested. Change stored presentation with `set_demo_style` only when requested; a local render command does not update the CRM. Do not retime or flatten a Deep flow to fit a presentation. Do not invent CSS, component dimensions or flow fields to imitate a missing capability.

## Execute and inspect

Keep a separate source/result file per conversation and a fresh output directory. Keep assets under `public/demo-assets/<company>/` and existing local HTML under `public/demo-apps/`. Resolve assets on the actual renderer host. For newly authored Deep company flows, pass the same separate `companyReview` to validation, saving and rendering; do not bury it in the strict flow schema or invent an exception.

Use [agent control](../../../../docs/agent-demo-authoring.md) for MCP/CLI authentication, full schemas, preview/capture/record and batch syntax. Never print personal tokens or assume another team's endpoint is this fork. Local Instant authoring, Deep authoring and recording need no CRM connection. Do not start `dev`/`start`, a database or another Codex/Claude session. CRM-backed generation/saving needs explicit human authorization plus the selected endpoint and token. No separate model service or autonomous worker is launched by these commands.

Before delivery, inspect the opening, proof and ending, readable text, selected channel, identity/assets, scrolling and relevant transitions. Check Play, Pause and Replay/return to opening when timing is affected. For New, include the branded intro, conversation and end card; for Legacy, include the full conversation frame. Keep controls and scrollbars out of the MP4. `visuallyReviewed:false` in an encoding receipt does not mean this review happened. Return one complete uploadable MP4 per conversation and state material limits.
