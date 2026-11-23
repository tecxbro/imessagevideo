---
name: pony-demo-deep
description: Create, edit and deliver researched PONY demos by running the complete original imported iMessage demo skills. Preserve their research, assets, full timelines and company review, then apply either Legacy or New presentation through local PONY recording commands, with CRM persistence only when explicitly requested.
---

# PONY Deep authoring

Read the [shared foundation](../pony-demo-creator/references/shared-foundation.md). Resolve the human's presentation and channel; keep Deep selected. Use the complete original imported workflow as the authoring process, with PONY's execution transport and chosen presentation added around it.

Deep means the original iMessage demo workflow. This adapter only maps its execution to PONY; it does not define a separate research process or reduce the original capability instructions.

## Load the complete original workflow

If a matching loaded workflow bundle is already present, use it. Otherwise run `npm run demo -- workflow --mode deep --operation create --presentation <legacy|new> --channel <chosen-channel>` once and read the returned original documents before researching or authoring. The command loads their actual pinned bytes; it does not execute research or launch an agent. Use `--operation edit --scope copy|conversation|assets` for an existing demo and `--operation render` for recording an already authored flow. Add `--domain travel|health|video|other` when company analysis selects that reference. Preserve choices/counts already supplied by the human.

Read the repository copies of [Photon Demo Creator](../photon-demo-creator/SKILL.md) and [Make iMessage Demo](../make-imessage-demo/SKILL.md), including their required HTML workflow, company-analysis, conversation-design and relevant domain references. Follow the originals directly; do not replace them with this adapter's summary or Instant templates. Read [Record iMessage Demo](../record-imessage-demo/SKILL.md) for complete-video and review policy.

Keep all six imported skill folders and their references/metadata/helper unchanged. Use [provenance and PONY command mapping](../../../docs/imessage-skills.md) to resolve standalone commands. Preserve original research depth, official-asset provenance, company preflight, typing/receipt/reaction conventions and visual verification. Retain the original company-only conversation-count default unless the human supplies a count or transcript. Use the human's channel choice rather than silently inheriting the source's iMessage default; check actual channel support before authoring rich features.

## Research, author and preserve

`deep/legacy`, `deep/new`, validation and encoding consume authored JSON. Their success or `mode: deep` metadata does not establish that these instructions were executed, that research is correct, or that playback was visually reviewed. A timing helper may implement an already designed transcript; it cannot replace the original product analysis, proof moment and ending design.

Stay in the current Codex/Claude conversation. Do not start another agent session, the full CRM, a database or a queued worker. Research and author local files, then use the local validate/record commands in the selected recipe. A requested MP4 does not authorize CRM persistence.

1. Follow the original public company research workflow and existing local research/stories. Preserve an already supplied transcript/brief without restarting unrelated research. Use `get_demo_brief` only when the human explicitly requests CRM context; a local company demo needs no CRM record, server or token.
2. Author one complete iOS document per conversation, using supported content for the selected channel. Keep original message/event timestamps, progressive customer drafts, incoming typing, receipt transitions, reactions, media and checkpoints. Keep research/provenance notes outside the strict flow.
3. For newly authored company demos, prepare the original separate `companyReview` and pass it to validation, saving and recording. Keep official avatar sources and evidenced exceptions; never fabricate an exception or flatten a Deep flow into Instant items.
4. Use `write_deep_demo({businessId,story,flow,style,companyReview?,...})` or CLI `save` for requested CRM persistence. Use `get_deep_demo`/CLI `get` to read an existing full flow. Include `demoId` only to replace that business's specified demo; otherwise create a new story. Do not treat a local recording as an implicit CRM save.
5. Execute the selected presentation recipe and the original visual review, then deliver the complete MP4 and relevant source/evidence links. Verify custom sheet/checkout gates and runtime support when those features were explicitly requested; no flow/model field supplies trusted human authorization.

## Select the presentation recipe

- **Deep + Legacy:** read [Legacy](references/legacy.md).
- **Deep + New:** read [New](references/new.md).

For a company list, keep the original count/story/review policy per company, author the required independent source files, then use the existing sequential batch command. A Deep batch job must reference its agent-authored source and required separate review. Never substitute the Instant playbook for unfinished Deep work.
