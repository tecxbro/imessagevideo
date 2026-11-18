# P5 — AppCard anatomy + PhotoStrip + card→panel morph

**Priority 6.** v1 AppCard is generic card chrome (title/detail/action on a color field).
Filmed app messages have a specific anatomy and lifecycle.

## Verified anatomy

- Rounded surface with bubble tail (the card IS an incoming message; it can carry the run's
  tail — linq f750 Cash card, tail hook bottom-left y670-680).
- Sender's **app-icon badge overlapping the top-left corner** (GamePigeon chess linq f136-180;
  poll/restaurant cards poke).
- Content/media area clipped to the card bounds; caption line ("Tap for details",
  "LET'S PLAY CHESS!") and/or CTA pill. Apple Cash skin: black card, white "Pay" pill.
- Tap → the card's own surface morphs into a fullscreen app panel (scale/position, NOT a
  push navigation): Flight Details f350-410, Jewelry picker + "Add to Bag" f585-690,
  Cash pay sheet f765-820.
- Multi-image surfaces are an internal carousel: images translate X under fixed chrome,
  clipped to the card (linq f1050-1150 ≈f1091-1111). The docs' "4+ cards = swipeable stack"
  is **unverified** in this library.

## Proposed change to `director/components.mjs`

Replace `AppCard` and add `PhotoStrip` (v2:267, 320):

```js
AppCard({id, x, y, width, mediaHeight, title, caption='Tap for details', cta,
         badge={label,color,ink}, mediaSrc, mediaChildren, tail=true,
         skin='light'|'cash', fontSize})   // meta={w,h}
PhotoStrip({id, x, y, width, height, images:[{src,width}], speed, t0, duration, gap})
// image children keyframe x inside a clip rect — use for carousels/photo strips.
```

Expand: fade/scale the card out while a panel group grows from the card's origin — same
surface id families so editors can keyframe the morph (proof `previews/card.mp4`).

## Proposed change to `component-contracts.md`

Replace the AppCard sentence with:

> AppCard separates surface, app-badge (top-left overlap), clipped media slot, heading,
> caption and optional CTA pill, and can carry the run's bubble tail. The card expands by
> morphing its own surface to a panel — keep shared ids so the morph is editable, do not
> cut to a pushed screen. PhotoStrip scrolls images inside a clip under fixed chrome.
