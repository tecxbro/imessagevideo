# Instant + Legacy

Complete the parent Instant workflow using the human's chosen channel. Use `style:"plain"` for local Instant authoring and recording. Keep Instant authoring and the resulting timeline intact; Legacy changes framing only.

Create a fresh run directory before redirecting output. Replace placeholders with the selected business, channel and paths:

```sh
npm run --silent demo -- instant <run>/brief.json --presentation legacy --channel <channel> --style plain --out <run>/result.json
npm run --silent demo -- instant/legacy <run>/result.json --channel <channel> --style plain --out <run>/demo.mp4
```

For ordinary Instant generation, provide a minimal company brief and let the CRM reader/playbook run. Use story and lines only for custom copy explicitly supplied/requested by the human, matching CRM write_demo. For an existing local demo, read the result file and preserve its Instant mode/channel. CRM tools are optional and require an explicit human request. Use the same flags for `preview` or `capture` when reviewing timing.

Inspect the full plain conversation, readable messages, correct identity/channel, proof and settled ending, with no playback controls or scrollbars in the video. Return the actual MP4 as **Instant / Legacy / chosen channel**. Keep CRM saving, rendering and outreach separate.
