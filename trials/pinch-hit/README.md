# Pinch Hit

Two original launch-film treatments for a fictional scorekeeping service. The coach has a 9 a.m. game and a short-staffed score table. In a 1:1 iMessage thread, the coach sends `cover 9am`. Pinch Hit asks its opted-in backup, Maya, in a separate thread. The slot stays pending until Maya replies `I can score`. The coach gets the confirmation after acceptance.

`product.mjs` implements the local prototype contract. The renderer reads its message transcript for both treatments. `npm test` exercises consent, the pending state, the actual acceptance, the wrong sender, duplicate events and the exported copy. This demonstration uses local fixtures and authored screen graphics. Live iMessage transport and delivery are outside this prototype. The outgoing blue cue follows [Apple’s iMessage documentation](https://support.apple.com/en-us/105087).

## Picture project

Requires Node.js, npm and FFmpeg. Run from this directory.

```sh
npm ci
npm test
node render.mjs early films/early.mp4
node render.mjs alternate films/alternate.mp4
node render.mjs early /tmp/pinch-hit-frame.png 370
```

`edit.mjs` holds the cut and action frames. `picture.mjs` holds the camera, editable type, transcript composition and pencil choreography. The only baked image is the four-panel still source in `assets/plates.png`; the renderer crops and animates each plate. No stock footage or reference frames were reused. The font stack is Georgia and system UI. Previewed on macOS.

The built-in image generation tool produced the four stills with this prompt:

> Four different production stills for an original short film about a youth baseball scorekeeper in a single exact 2×2 contact sheet. Landscape wide canvas, four equal panels, no gaps, no borders, no lettering. Every panel contains a completely different shot. Midwest municipal little league at 8:58 AM, overcast with shafts of early golden light, muted oxidized blue, forest green, tannin brown, warm rust. Natural photojournalist 35mm color photography, soft visible grain, a quietly observed human scale. Top left: wide near first base from behind the backstop, empty unmistakable battered teal folding chair behind a small wooden table, a scorebook with simple lines and a pencil, lineup of a few child players out of focus in the distance, ball in worn brown glove lying on fence ledge: compose chair at center-right, players to left, environment given room. Top right: medium profile from ground, torso of adult coach in green windbreaker and torso of young player in cream uniform with dark red raglan sleeves holding a glove next to a green wire fence, looking off-screen toward a pregame field, no clear faces, soft background, the two on the left half of frame. Bottom left: overhead kitchen breakfast counter with a bowl of pancake batter tipped as if about to pour, one adult hand, cast-iron pan, bright silver teaspoon with handle angled diagonally, warm amber light on natural maple. Keep spoon and pan toward the left and center and leave counter on right. Bottom right: an overhead at the ball field of an open large warm ivory baseball scorebook on dark old oak table in sunlight, clear clean empty score diamond cells along right page, no prominent written text or markings and NO pencil, dark teal sleeve and wrist resting at extreme bottom edge outside the page. Deliberately understated, film festival short workprint, no type, no logos, no graphic elements, no phones in any image. These are film plate backgrounds cropped per panel.
