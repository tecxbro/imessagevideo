# Fresh assembly · Ferry lunch

Mina and a friend coordinate lunch as the friend returns on the ferry. The conversation, its participants, booking details and event times are fictional. The author used the public conversation and browser text measurement APIs, with the included photographs as scene inputs.

[Watch the exported MP4](../../../../../previews/codex-ui/fresh.mp4) · [Inspect the decoded frames](../../../../../previews/codex-ui/fresh-frames.jpg)

## Beats

| Seconds | Visible interaction |
| --- | --- |
| 0–2.23 | Mina’s meeting-place photos start in a four-image stack. A leftward review advances one image while the camera settles. |
| 2.23–4.38 | Mina sends a message followed by a separate rail of lunch photos. Two lateral swipes reveal the later dishes. |
| 4.38–8.17 | The sender types a request with a skin-tone and ZWJ emoji cluster, then sends it as a wrapped bubble. |
| 8.83–9.70 | A heart appears on the sent request. An inline card then presents the table. |
| 11.50–15.20 | The thread scrolls toward older messages and back to the card as the camera drifts. |

The inline stack gesture and placement of the restaurant-style rail are authored. The [attachment evidence](../ATTACHMENT-EVIDENCE.md) records the Linq rail inside a venue page and the evidence limits around native iOS presentations. The in-thread app card is a fictional booking preview.

## Export review

All 456 frames of the silent 960 × 540, 30 fps H.264 preview decoded. The initial assembly exposed a leading fragment in the long, horizontally scrolling draft. The final render uses the component's multiline draft and a shorter first message. At frames 245–246, the whole two-line request, including 👩🏽‍🍳, moves from the composer into the thread and the idle placeholder returns. Frames 254–269 show the heart appearing on the request. Frames 344–367 show the heart staying on the bubble as the viewport scrolls and clips the card beneath the composer. The photo stack and venue-style rail use different motion at 1.53 and 3.53 seconds, respectively.

## Rebuild

From the repository root, with FFmpeg, the skill engine dependencies and Chromium installed:

```sh
skill=skill/imessage-motion-recreation
out="$(mktemp -d)"
export CHROME_PATH="/path/to/chromium"
node "$skill/director/ui-trial/fresh/ferry-lunch.mjs" "$out/ferry-lunch.scene.json"
node "$skill/scripts/engines/render.mjs" --method html \
  --scene "$out/ferry-lunch.scene.json" --out "$out/ferry-lunch.mp4"
```

The scene JSON refers to local asset paths relative to its own location. Edit the timeline and rebuild the JSON after moving the checkout or output directory.

## Photographs

These 480-pixel-wide files are local scene assets. All came from the [Pexels collection under the Pexels License](https://www.pexels.com/license/) and were retrieved on November 18, 2026. Display crops and fictional chat context are authored.

| Asset | Photographer and original |
| --- | --- |
| `ferry-clock.jpg` | [Cristiane Doffini, Iconic San Francisco Ferry Building Clock Tower](https://www.pexels.com/photo/iconic-san-francisco-ferry-building-clock-tower-29489422/) |
| `market-hall.jpg` | [Behnaz Keivan, Vibrant Ferry Building Marketplace in San Francisco](https://www.pexels.com/photo/vibrant-ferry-building-marketplace-in-san-francisco-40474837/) |
| `pier.jpg` | [Robert So, Aerial View of San Francisco Ferry Building and Bay](https://www.pexels.com/photo/aerial-view-of-san-francisco-ferry-building-and-bay-29618565/) |
| `approach.jpg` | [RITESH SINGH, Ferry Terminal of San Francisco in Rain](https://www.pexels.com/photo/ferry-terminal-of-san-francisco-in-rain-15955217/) |
| `fish-tacos.jpg` | [Rodrigo Ortega, Delicious Fish Taco with Colorful Garnish](https://www.pexels.com/photo/delicious-fish-taco-with-colorful-garnish-29906095/) |
| `grilled-cheese.jpg` | [Griffin Wooldridge, Delicious Grilled Cheese Sandwich on Plate](https://www.pexels.com/photo/delicious-grilled-cheese-sandwich-on-plate-30346820/) |
| `oysters.jpg` | [Rachel Claire, Delicious oysters served in restaurant](https://www.pexels.com/photo/delicious-oysters-served-in-restaurant-5491014/) |
