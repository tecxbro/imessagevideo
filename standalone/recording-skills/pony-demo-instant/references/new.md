# Instant + New

Complete the parent Instant workflow using the human's chosen channel. Use `collab` framing after the human selects New; use `brand` if requested. Keep Instant authoring and its paced conversation intact.

Create a fresh run directory. Replace `<new-style>` with the actual selected `collab` or `brand` value, and replace the other placeholders:

```sh
npm run --silent demo -- instant <run>/brief.json --presentation new --channel <channel> --style <new-style> --out <run>/result.json
npm run --silent demo -- instant/new <run>/result.json --channel <channel> --style <new-style> --out <run>/demo.mp4
```

For ordinary Instant generation, provide a minimal company brief and let the CRM reader/playbook run. Use story and lines only for custom copy explicitly supplied/requested by the human, matching CRM write_demo. For an existing local demo, read its result file first and preserve its Instant mode/channel. CRM tools are optional and require an explicit human request. Keep prepared brand assets distinct from assets visibly applied by the renderer. Do not add company-specific CSS.

Inspect the branded intro, conversation/proof, caption/logo placement and complete end card. Preserve readable framing and normal scrolling, and keep controls/scrollbars out of the MP4. Return the video as **Instant / New / chosen channel**, with Collab or Their brand identified when relevant.
