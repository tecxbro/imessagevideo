# Codex direction trial

## Picture for sound and first viewing

- [Early cut MP4](https://github.com/tecxbro/imessagevideo/blob/3324065c5386952c1db87a77925a5df9c1d81dff/trials/pinch-hit/films/early.mp4) · [download](https://github.com/tecxbro/imessagevideo/raw/3324065c5386952c1db87a77925a5df9c1d81dff/trials/pinch-hit/films/early.mp4)
- Picture commit `3324065c5386952c1db87a77925a5df9c1d81dff`. 1280×720, 24 fps, 576 frames, 24 seconds, silent source.
- [Editable picture](trials/pinch-hit/) · [Alternate cut MP4](https://github.com/tecxbro/imessagevideo/blob/3324065c5386952c1db87a77925a5df9c1d81dff/trials/pinch-hit/films/alternate.mp4), 528 frames, 22 seconds, silent source.

## Sound anchors for the early cut

Zero-based frames, 24 fps. Opening field in frame 0. Fence view 98. Composer starts at 160, actual send at 201. Pending message first appears at 237. Empty chair returns at 267. Confirmation shot at 352 and message at 370. Scorebook at 438, pencil contact at 466 and mark completed at 500. The mark is the outcome. Title joins the last shot at 529.

Frames 267–351 offer an editorial hold test. The delayed answer needs to feel like waiting at a game. Try letting the field fall very quiet after the send, hold the offscreen game sound across the book cut, and let the first score mark carry the end. The title can sit over the continuing ballpark bed. Score the pinned picture above before retiming.

```sh
cd trials/pinch-hit
npm ci
npm test
node render.mjs early films/early.mp4
node render.mjs alternate films/alternate.mp4
```

## Revised picture and timing comparison

- [Revised silent picture](https://github.com/tecxbro/imessagevideo/blob/19d50dc26e4e8e2f2875affdb3b2c7b2ca6861be/trials/pinch-hit/films/final-picture.mp4) and [isolated hold test](https://github.com/tecxbro/imessagevideo/blob/19d50dc26e4e8e2f2875affdb3b2c7b2ca6861be/trials/pinch-hit/films/hold-test.mp4), picture commit `19d50dc26e4e8e2f2875affdb3b2c7b2ca6861be`. Each is silent and runs 576 frames at 24 fps.
- Isolated hold test confirms at f358, cuts to the book at f426, touches the pencil at f454 and finishes the mark at f488. The title remains f529. Raw picture f0–339 matches the early renderer exactly.
- Revised picture anchors, zero-based: field f0, player f78, coach thread f128, send f170, pending f193, empty chair f230, kitchen/backup request f274, Maya types f325–341 and sends f352, matched occupied chair f374, coach confirmation f392, book f469, pencil contact f488 and mark f513, title f536, end f576. The offscreen game can lead the cut to the book, with the mark finishing in a short, unscored space.
- [Blind first view](https://github.com/tecxbro/imessagevideo/blob/262877b84fd153d8f6471a633ab71479cfe32d0d/OBSERVER.md) · [Editorial comparison and exact cut evidence](trials/pinch-hit/README.md#the-two-wagers-and-what-changed) · [Reference study](trials/pinch-hit/EDITORIAL.md).

From the picture project, run `node render.mjs hold-test films/hold-test.mp4` and `node render.mjs final films/final-picture.mp4`.
