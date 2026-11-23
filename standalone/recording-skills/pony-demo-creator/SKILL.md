---
name: pony-demo-creator
description: Build and deliver company demo videos from Codex or Claude. Route Instant or Deep authoring to an explicit Legacy or New recipe, using the imported iMessage demo skills as the foundation with local authoring/recording by default and optional explicitly requested CRM access.
---

# PONY demo skills

Use the imported iMessage demo skills as the foundation. Keep their source files intact. Read [shared foundation](references/shared-foundation.md) for the source responsibilities, human choices and PONY execution mapping.

Instant is the existing CRM Instant workflow, run locally through its shared HTML reader and playbook. Deep is the original imported iMessage demo workflow. These names do not introduce alternative research/generation systems; Legacy/New controls presentation independently.

## Resolve the requested combination

Resolve authoring mode, presentation and channel before creating a demo. Ask one concise question containing every missing choice. Reuse answers already supplied in the conversation; accept common settings for a whole company list or overrides per company. Preserve saved choices for edits unless the human changes them.

| Human choice | Authoring skill | Exact presentation recipe |
| --- | --- | --- |
| Instant + Legacy | [Instant](../pony-demo-instant/SKILL.md) | [Plain messaging video](../pony-demo-instant/references/legacy.md) |
| Instant + New | [Instant](../pony-demo-instant/SKILL.md) | [Branded messaging video](../pony-demo-instant/references/new.md) |
| Deep + Legacy | [Deep](../pony-demo-deep/SKILL.md) | [Full original workflow, plain video](../pony-demo-deep/references/legacy.md) |
| Deep + New | [Deep](../pony-demo-deep/SKILL.md) | [Full original workflow, branded video](../pony-demo-deep/references/new.md) |

Use `$instant-legacy`, `$instant-new`, `$deep-legacy` or `$deep-new` for an explicit combination; Claude exposes the same names with `/`. Interpret `/instant/new`, `/instant/legacy`, `/deep/new` and `/deep/legacy` in a request as those routing choices; these slash-shaped strings are also supported CLI recipe names, not extra native Codex slash commands. Load the selected authoring skill and only the selected recipe. Treat Legacy/New as presentation of the authored conversation; never change authoring mode to change framing. Use the human's chosen iMessage, SMS, WhatsApp, Telegram or Slack channel and check that channel's capabilities. Ask before changing a requested mode or channel to work around a limitation.

## Complete the requested deliverable

Use an already loaded matching workflow bundle, or load the selected instructions once with `npm run demo -- workflow --mode <instant|deep> --operation create --presentation <legacy|new> --channel <chosen-channel>`. Read and execute the returned documents in this conversation. For existing edits, use `--operation edit --scope copy|conversation|assets`; recording an authored flow uses `--operation render`. The loader returns original instructions; a selected mode or an encoded MP4 is not evidence that authoring ran.

Let the Instant command perform the shared CRM HTML read/playbook generation; let the current Codex or Claude conversation run the original research/full-flow workflow for Deep. Then validate, preview, record, inspect and deliver. Never start the full CRM, a database, another agent session or a worker for a demo request. Local Instant authoring uses `npm run demo -- instant`; Deep follows the original imported research/authoring skills. Use PONY MCP or `npm run demo:agent` only for explicitly requested CRM operations. Discover live schemas only after that request; inspect existing tools/code before proposing an extension. Follow the source workflow rather than adding renderer code for an ordinary company demo.

Use `npm run demo` for the demo-only renderer and actual MP4 recording. For several companies/conversations, prepare the explicit per-job choices and source files, then run the existing batch command sequentially. Read [agent control](../../../docs/agent-demo-authoring.md) for payloads and command syntax. Do not ask the human to prepare JSON or operate browser authoring controls.

Deliver one inspected MP4 per conversation unless another output was requested. Return absolute file links with company, use case, mode, presentation and channel. Keep validation, encoding, visual review, CRM persistence, publication and actual provider activity as separate claims. Saving or recording does not authorize outreach or publication.
