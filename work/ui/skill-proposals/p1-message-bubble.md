# P1 — MessageBubble: auto-wrap, auto-height, measured tail

**Priority 1+2 on the damage list.** v1 takes `width`,`height` explicitly and traces a guessed
tail — every copy change forces manual refit and the tail shape is the fastest fake tell.

## Proposed change to `director/components.mjs`

Replace `MessageBubble` with the v2 builder (`work/ui/components/components-v2.mjs:107`):

```js
MessageBubble({id, x, y, side='outgoing', copy, fontSize=17, maxWidth=0.62*sceneWidth,
               tail=true, tapback=null, senderName=null, senderAvatar=null, fill})
// returns group; meta = {w, h, lines} for stacking
```

- `copy` is word-wrapped by `wrapText()` against a canvas-measured SF Pro width table
  (`work/ui/components/textmetrics.mjs`, embedded so the builder is offline-safe);
  height = `lines * fontSize*1.2 + fontSize*1.3` (verified padding ≈12px v, 18-20px h).
- Body+tail = one generated `path` (`bubbleBodyPath`, v2:41): continuous-corner rect whose
  anchor-side corner becomes the measured comma hook — tail stays inside body x-extent,
  ~14px drop on a 120px bubble (linq f750 pixel scan: body y56-172, tail tip y~186, x830-847).
  Mirrored for incoming/outgoing. **Do not keep v1's `Q`-kick tail** — it exits the body edge.
- `tail` defaults true; callers set `tail:false` on all but the last message of a same-side
  run (verified linq f750: "Sure, it'll be $166.89" tail-less because the Cash card follows).
- Corner radius = `min(h/2, fontSize*1.15)` — measured r≈0.33h on 2-line, ≈0.5h on 1-line.

## Proposed change to `component-contracts.md`

Replace the "Text is editable; sizing is explicit…" paragraph (line 24) with:

> Text is editable and now measured: MessageBubble word-wraps copy with an embedded SF Pro
> width table (canvas-derived, offline fallback estimator) and derives its own height.
> Overflow above `maxWidth` wraps, never silently shrinks; a string that cannot fit even one
> word throws. Read `bubble.meta.w/h` to stack siblings — do not hardcode thread y-positions.
> For pixel-exact production match set explicit `fontSize`/`maxWidth` and re-render.

## Compat

`width`/`height` params are accepted but ignored-with-warning (or map to `maxWidth`) —
pick one policy; v2 chooses ignore + `meta` readback.
