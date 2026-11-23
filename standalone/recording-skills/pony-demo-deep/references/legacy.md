# Deep + Legacy

Complete the entire parent Deep workflow using the original imported skills. Keep the human's channel and all authored timeline data. Use `style:"plain"` in a new save envelope. For the same conversation in both presentations, reuse the full flow; no reauthoring is needed.

For a newly authored company demo, keep `review.json` separate and use it throughout:

```sh
npm run --silent demo -- validate <run>/result.json --company-review <run>/review.json
npm run --silent demo -- preview <run>/result.json --mode deep --presentation legacy --channel <channel> --style plain --company-review <run>/review.json
npm run --silent demo -- deep/legacy <run>/result.json --channel <channel> --style plain --company-review <run>/review.json --out <fresh-output>/demo.mp4
```

Keep a preview renderer only while needed and stop it before recording. The recording command owns and closes its renderer; do not start a new Codex/Claude session. Use CLI `save <business-id> <run>/result.json --company-review <run>/review.json` when CRM persistence was requested; it reads the envelope's explicit plain style. Preserve an existing saved style unless a change was requested. Generic/existing-flow cases follow their original review policy.

Inspect the original required moments in the plain frame: identity/avatar, readable copy, composer/typing, relevant receipt transitions and rich events, natural scrolling, proof and full ending. Return the complete MP4 as **Deep / Legacy / chosen channel**. Do not replace the full-flow workflow with simplified edits.
