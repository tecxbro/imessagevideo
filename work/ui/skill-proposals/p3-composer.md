# P3 — Composer: measured draft→send lifecycle

**Priority 4.** v1 `Composer({copy, active})` is one static field — mic and send coexist,
send sits outside the field, no typed layer or caret. The measured scene disagrees.

## Measured sequence (linq `v19-intro-composer`)

1. Empty: placeholder + mic icon visible; no send control.
2. First typed char (t=0.767): placeholder **and** mic end at the same instant.
3. t=0.800-0.900: send circle appears **inside** the field's right end and fills
   `#c2d2fd→#70a3ff→#007efe` over ~3 frames.
4. Send: field returns to placeholder+mic; outgoing bubble appends to thread bottom;
   "Delivered"→"Read" label appears under it (linq f145-175).
5. Draft→send is a **cut** in all six films — do not invent a flight animation.

## Proposed change to `director/components.mjs`

Replace `Composer` with v2 (components-v2.mjs:184):

```js
Composer({id, x, y, width, height, placeholder='iMessage', typed='', typeStart=0,
          sendT=null, typedSteps=6})
// children: -plus, -field, -placeholder(+ -placeholder-post), -mic(+ -mic-post),
//           -send (fill sweep keyframes + -send-arrow), -typed-N staggered prefixes, -caret
```

`typeStart`/`sendT` stamp every window; `typedSteps` does char-by-char reveal via prefix
layers (measured scenes bake per-glyph layers — prefix texts are the editable equivalent).
Chrome updates: `+` = white circle + shadow with a two-rect glyph (stroked open paths render
as blobs in the html engine — do not use `fill:'none'` paths for glyphs); send circle inside
the field; caret `#0088ff`.

## Proposed change to `component-contracts.md`

Extend the "Composer input, send button…" paragraph:

> The composer is a state machine, not a static field: placeholder+mic end together on the
> first typed char, the send circle appears inside the field right end and fills
> #c2d2fd→#70a3ff→#007efe, and post-send the field returns to placeholder+mic while the
> message is appended to the thread. Pass `typeStart`/`sendT`; append the outgoing
> MessageBubble yourself at `sendT` — the composer does not spawn messages. Send is a cut.
