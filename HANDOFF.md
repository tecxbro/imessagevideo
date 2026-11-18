# Codex UI trial

For `film-trials/codex-catalog` and `film-trials/codex-direction`. Tested implementation and preview commit [`815b1e68f9cf674a24f37cc1f20383577ceb8289`](https://github.com/tecxbro/imessagevideo/commit/815b1e68f9cf674a24f37cc1f20383577ceb8289), based on `c49482aec7b8ed0b840f97c61a5e5b860c4077b6`. The [branch](https://github.com/tecxbro/imessagevideo/tree/film-trials/codex-ui) also carries this handoff.

## Import and edit

```js
import {
  buildConversation, PhotoStrip, NativePhotoCollage,
  NativeAttachmentStack, InlineAppCard,
} from './skill/imessage-motion-recreation/director/conversation.mjs';
import {buildWithBrowserText} from './skill/imessage-motion-recreation/director/ui-trial/measure-text.mjs';
```

Use `buildConversation(options)` with a synchronous export-font measurer, or `await buildWithBrowserText(options)` for installed fonts in Chromium. Both return `{scene, events}`. Set participant identity, message IDs, copy, attachment assets, event times, scroll and camera in the same authored options. Read the [component contract](skill/imessage-motion-recreation/director/component-contracts.md#moving-conversations) for accepted fields and [attachment evidence](skill/imessage-motion-recreation/director/ui-trial/ATTACHMENT-EVIDENCE.md) for source checkpoints and uncertainties.

- **Catalog.** Index the standalone media builders and the conversation builder separately. Use the Linq rail for app-local picture movement, grouped previews for Messages attachments, and the Photon sample for inline preview followed by separate sheet motion. Include the exported frame sequences and authored clocks in the entries. The documented collage and stack count boundary lacks a matched device/OS/gesture recording here.
- **Direction.** Start with [the fresh scene source](skill/imessage-motion-recreation/director/ui-trial/fresh/ferry-lunch.mjs). Keep the message IDs on the rows and drive the camera on the phone's parent. Hold an identifiable contact and action-specific request through send. Recheck the draft, arrival, Tapback and viewport together after swapping the copy or crop.

The [HyperFrames registry](https://github.com/heygen-com/hyperframes/blob/main/skills/hyperframes-registry/SKILL.md) informed the reusable component entry points and example. The [Launch Video Clone skill](https://github.com/per-simmons/launch-video-clone/blob/main/SKILL.md) informed review by moving beats and retaining the failure that drove the fix. The Serena collection indexes the same Poke reference used in the footage comparison. [Serena dataset](https://github.com/serenakeyitan/awesome-ai-clonable-launch-videos#poke-imessage-ai-assistant).

## Review the moving picture

| Preview | Checkpoints in decoded output |
| --- | --- |
| [Legacy baseline frames](previews/codex-ui/baseline-motion.jpg) | n37 and n52 show long copy under the send control. n62 and n90 show clipped bubble text and a still-active send control after clearing. |
| [Lantern MP4](previews/codex-ui/lantern.mp4) · [frames](previews/codex-ui/lantern-frames.jpg) | Heart at n20, prior row rewraps at n34, full draft at n134, composer idle and outgoing entry at n135. At n181–199 the scroll and camera both move. |
| [Fresh Ferry Lunch MP4](previews/codex-ui/fresh.mp4) · [frames](previews/codex-ui/fresh-frames.jpg) | Changing people, copy, photographs and emoji required only options and assets. Inspect the stack at n46, rail at n106, draft and send at n245–246, heart at n269 and card crop at n344–367. |

Both silent H.264 outputs fully decoded. Lantern was 270 frames at 620 × 650. Ferry Lunch was 456 frames at 960 × 540. Both used 30 fps. Independent HTML rerenders matched the preview bytes. A GSAP pass also showed the Lantern send and idle transition at n135. The browser regression checks row spacing, exact-frame transfer, and clip hit testing under a moving transform, including a control with the viewport clip removed. The renderer and regression were exercised in Chromium on macOS. Verify another renderer separately for a production export.

The phone shell, emoji fallback, stack overlap and inline stack sweep are authored approximations. The app card is a launch preview. For sheet opening and dismissal, review the [separate motion skill](https://github.com/tecxbro/imessagedemo/blob/main/.agents/skills/recreate-imessage-sheet-motion/SKILL.md) and its measured host, sheet and readiness phases. Neither preview proves a native launch or product booking.

## Render and test

From the repository root with Node and FFmpeg installed:

```sh
skill=skill/imessage-motion-recreation
npm ci --prefix "$skill/scripts/engines"
# Use an installed Chromium or Chrome executable. For a new browser install:
npm exec --prefix "$skill/scripts/engines" -- playwright install chromium
export CHROME_PATH="$(node --input-type=module -e 'import {chromiumPath} from "./skill/imessage-motion-recreation/director/ui-trial/measure-text.mjs"; console.log(chromiumPath())')"

out="$(mktemp -d)"
node "$skill/director/ui-trial/demo.mjs" "$out/lantern.json"
node "$skill/scripts/engines/render.mjs" --method html \
  --scene "$out/lantern.json" --out "$out/lantern.mp4"
node "$skill/director/ui-trial/fresh/ferry-lunch.mjs" "$out/ferry-lunch.json"
node "$skill/scripts/engines/render.mjs" --method html \
  --scene "$out/ferry-lunch.json" --out "$out/ferry-lunch.mp4"

node --test "$skill/director/test_toolkit.mjs" "$skill/director/ui-trial/test-conversation.mjs"
```

The two previews use the code and assets in this branch. Run `python3 tools/sync_library.py` with the tracked archive parts present to materialize the full reference library. For a side-by-side layout control, build Lantern again with `--short`. It keeps the original short row and shares the same send, scroll and camera clock. To reproduce the legacy failure, export the existing `conversation-handoff` motif with `--copy 'Could you hold two window seats for the evening lantern workshop? ✨'` and inspect frames 37, 52, 62 and 90.

## Observer feedback

Read [`OBSERVER.md` at `262877b`](https://github.com/tecxbro/imessagevideo/blob/262877b84fd153d8f6471a633ab71479cfe32d0d/OBSERVER.md). The cold viewer understood the Pinch Hit job only after the first reply and had to infer who was responding and who took over the scorebook. For direction's next conversation, show the job in the request and label the participating contact through the outcome. That note reviewed the Pinch Hit picture export. The UI fixtures were reviewed independently.
