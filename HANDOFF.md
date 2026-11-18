# Codex UI trial

For `film-trials/codex-catalog` and `film-trials/codex-direction`. The [branch](https://github.com/tecxbro/imessagevideo/tree/film-trials/codex-ui) includes both trials from base `c49482aec7b8ed0b840f97c61a5e5b860c4077b6`. Lantern and Ferry Lunch are pinned to [`815b1e68f9cf674a24f37cc1f20383577ceb8289`](https://github.com/tecxbro/imessagevideo/commit/815b1e68f9cf674a24f37cc1f20383577ceb8289). Blue Awning and Saturday Plant Swap are pinned to [`e9ed384324580dacb94a622324526df8eba936f2`](https://github.com/tecxbro/imessagevideo/commit/e9ed384324580dacb94a622324526df8eba936f2).

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

Run `python3 tools/sync_library.py` with the tracked archive parts present to materialize the full reference library. For a side-by-side layout control, build Lantern again with `--short`. It keeps the original short row and shares the same send, scroll and camera clock. To reproduce the legacy failure, export the existing `conversation-handoff` motif with `--copy 'Could you hold two window seats for the evening lantern workshop? ✨'` and inspect frames 37, 52, 62 and 90.

## Compose a phone inside an existing scene

```js
import {
  Conversation, CameraRig, PhotoAttachment, AttachmentCollage,
  AttachmentStack, PhotoStrip, AppCard, BottomSheet,
} from './skill/imessage-motion-recreation/director/components.mjs';
```

`Conversation(options)` returns a phone layer. Supply named people, stable message IDs, complete draft states, reactions and scroll cues. Put the layer under `CameraRig` and add it to a scene. The [layer contract](skill/imessage-motion-recreation/director/component-contracts.md#compose-a-moving-thread) covers the authored clock, text measurement, asset paths and media options. The [attachment comparison](skill/imessage-motion-recreation/director/attachment-evidence.md) has Linq, Photon and Apple footage checkpoints. Apple's iOS 15 presentation shows a three-photo collage and a ten-photo stack with a visible in-thread swipe. Apple's iOS 27 guide documents the four-item threshold. The exact device/build and a matched four-item gesture remain unmeasured.

| Preview | Review points |
| --- | --- |
| [Legacy failure](film-trials/codex-ui/previews/legacy-repro.mp4) | Three manually broken lines overflow the composer by frame 77 and the sent bubble by frame 96. The blue send arrow remains after clearing. |
| [Blue Awning](film-trials/codex-ui/previews/blue-awning.mp4) | Heart visible by frame 31. The full draft and send arrow are visible at 77. The composer is idle at 78 and the outgoing row is readable at 90. At 146 the heart still sits on Noor's message as the transcript scrolls inside the moving phone. |
| [Saturday Plant Swap](film-trials/codex-ui/previews/fresh-assembly.mp4) | A fresh agent imported two APIs and supplied new people, copy, emoji, photos and camera keys. Check frames 98–101 for send, 129 and 176 for photos, and 229 for the reaction. [Trial notes and photo provenance](skill/imessage-motion-recreation/director/examples/fresh-ui/README.md) |

These three H.264 files fully decode at 960 × 540 and 30 fps, with 180, 225 and 270 frames respectively. The layer trial uses authored camera and attachment motion, a neutral phone shell and a one-line composer. Rerender with the intended font and review any edit to text, camera or clip geometry.

Run from the repository root with the same renderer setup above:

```sh
skill=skill/imessage-motion-recreation
ui_out="$(mktemp -d)"
node "$skill/director/examples/conversation-motion.mjs" "$ui_out/blue-awning.json"
node "$skill/scripts/engines/render.mjs" --method gsap \
  --scene "$ui_out/blue-awning.json" --out "$ui_out/blue-awning.mp4"
node "$skill/director/examples/fresh-ui/scene.mjs" > "$ui_out/plant-swap.json"
node "$skill/scripts/engines/render.mjs" --method gsap \
  --scene "$ui_out/plant-swap.json" --out "$ui_out/plant-swap.mp4"
node --test "$skill/director/test_toolkit.mjs" \
  "$skill/director/test_conversation_motion.mjs" "$skill/director/ui-trial/test-conversation.mjs"
```

Append `--compact` when generating Blue Awning to shorten the preceding row while retaining the reaction, composer, scroll and camera cues. The [regression](skill/imessage-motion-recreation/director/test_conversation_motion.mjs) checks both copy lengths, reaction ancestry, the exact send frame, multiline draft clipping and the five media surfaces.

## Observer feedback

Read [`OBSERVER.md` at `262877b`](https://github.com/tecxbro/imessagevideo/blob/262877b84fd153d8f6471a633ab71479cfe32d0d/OBSERVER.md). The cold viewer understood the Pinch Hit job only after the first reply and had to infer who was responding and who took over the scorebook. For direction's next conversation, show the job in the request and label the participating contact through the outcome. That note reviewed the Pinch Hit picture export. The UI fixtures were reviewed independently.
