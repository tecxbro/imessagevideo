---
name: deep-legacy
description: Create and deliver local Deep + Legacy company demo videos. Use for deep/legacy, /deep/legacy, or Deep Legacy requests. Ask for a missing channel; preserve the imported iMessage skills and keep CRM access opt-in.
---

# Deep + Legacy

1. Select **Deep** authoring and **Legacy** presentation from this invocation. Preserve the company, channel and count already supplied. Ask for any missing company or channel before creating a demo.
2. Run `npm run demo -- workflow --mode deep --operation create --presentation legacy --channel <chosen-channel>` and read the original documents it returns. For an existing edit, use `--operation edit --scope copy|conversation|assets`. Follow [PONY Deep](../pony-demo-deep/SKILL.md), its [Legacy recipe](../pony-demo-deep/references/legacy.md) and their original referenced skills directly. This entry point and the recording command do not perform research themselves.
3. Author and record with local files. Do not start the CRM, read CRM tools, create another Codex/Claude session, queue a worker, or publish/send anything. Use CRM only after an explicit human request.
4. Execute `npm run demo -- deep/legacy <agent-authored-input.json> --channel <chosen-channel> --out <fresh-output>/demo.mp4` with the required separate company review for new company flows. For multiple conversations, use the existing sequential local-source batch command.
5. Inspect the video and required review images, then deliver one complete MP4 per requested conversation using absolute file links. Keep encoding, visual review and any separately requested CRM persistence distinct.
