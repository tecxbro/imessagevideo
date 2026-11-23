---
name: pony-demo-instant
description: Create and deliver demos using the exact CRM Instant research and generation pipeline without starting the CRM. Use bounded HTML extraction, the shared industry playbook and automatic pacing, with either Legacy or New presentation.
---

# PONY Instant authoring

Read the [shared foundation](../pony-demo-creator/references/shared-foundation.md). Resolve the human's presentation and channel; ask only for missing choices. Keep Instant selected unless the human authorizes a change.

Default to one conversation per company unless the human supplied a count. Deep retains the original three-conversation company default. Stay in the current agent conversation; do not launch another Codex/Claude session.

## Reuse the imported foundation

**Instant here means CRM Instant. Deep here means the original iMessage demo workflow.** Do not independently research or write a new Instant story in the agent conversation. Use the same reader, playbook, pacing and validation as CRM `make_demo`; only the local input/output and persistence boundary differ.

Consult [Make iMessage Demo](../make-imessage-demo/SKILL.md) and current capabilities/contracts when choosing content. Preserve customer/outgoing and business/incoming direction, supplied copy, supported channel semantics and asset provenance. Read [Record iMessage Demo](../record-imessage-demo/SKILL.md) for complete-video and visual-review requirements; use the selected PONY recipe for its commands.

Research is the CRM's bounded HTTP HTML extraction: homepage plus at most five internal pages, `browser:"never"`, `timeoutMs:9000`, `llm:false`. No Playwright/browser research, Firecrawl, external search, model analysis or extra agent research pass for Instant. A JS shell or failed website read uses the same CRM fallback; do not silently upgrade research to Deep. Playwright remains permitted for preview, visual checks and MP4 recording.

## Author and edit locally

1. Use the human's company name and official URL; resolve only the company identity if ambiguous. Write a minimal local brief as in [the automatic Instant example](../../../docs/examples/local-instant-auto.json). Do not supply `story`, `lines` or an agent-composed `profile` for an ordinary Instant request.
2. Run `npm run demo -- instant <brief.json> --presentation <legacy|new> --channel <chosen-channel> --out <fresh-result.json>`. It performs the shared CRM HTML read, playbook selection, pacing and validation. The saved result includes the profile used. Local generation needs no CRM, database, token, model service or new agent session.
3. Reuse `profile` only when an actual existing cached profile was supplied, equivalent to the CRM cache. Preserve it rather than enriching it; do not access the CRM to obtain one without an explicit request. `variant` is the local equivalent of the CRM's previous-demo count (default zero). For the same business context, cached/extracted profile, variant and channel, the conversation matches CRM Instant; Legacy/New changes only framing.
4. Edit the local brief/script and regenerate into a fresh result when requested. Preserve the chosen channel/presentation. Keep a full local flow unchanged when only recording it; never flatten Deep into Instant.
5. Execute the chosen presentation recipe, inspect the video and deliver the MP4. Both modes retain their existing supported-channel checks. Instant's generator still requires 4–8 bubbles and 9–32 seconds; report a failed validation instead of inventing a replacement story. For batches, prepare one minimal brief or saved result per job.

Explicitly supplied/requested custom copy may use `story` and `lines`, matching CRM `write_demo`; [the custom-copy example](../../../docs/examples/local-instant.json) documents that existing path. Do not choose it instead of `make_demo` generation for a company-only Instant request. Exact rich events or custom experiences follow the human's requested mode and actual capabilities; ask before switching to Deep.

## Optional CRM operations

Only after an explicit human request, use `get_demo_brief`, `make_demo`, `write_demo`, `get_demo` or `edit_demo` through the selected MCP endpoint. Preserve their live schemas and existing choices; inspect them before calling. CRM edits can import photos through Blob and support simplified photo/voice-note visuals. A local demo request never requires a CRM business, token or lookup. Use [agent control](../../../docs/agent-demo-authoring.md) for the separately authorized CRM path.

## Select the presentation recipe

- **Instant + Legacy:** read [Legacy](references/legacy.md).
- **Instant + New:** read [New](references/new.md).

For company lists, apply the resolved choices per company, prepare the existing batch manifest and record sequentially. Every default job references a local brief or full Instant result. A CRM business is allowed only in an explicitly authorized `--crm` batch. Keep one result/video per requested conversation; do not replace a video deliverable with a saved link.
