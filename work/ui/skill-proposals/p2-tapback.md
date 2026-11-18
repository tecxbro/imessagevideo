# P2 — TapbackBadge: child-anchored reaction

**Priority 3.** v1 has no tapback. Filmmakers will emit it as a thread sibling and it will
visibly drift on the first scroll/camera move — anchoring is *verified* footage behavior.

## Verified anatomy (for the contract comment)

- Badge = small bubble in the *reactor's* color (blue when you react to an incoming message;
  your badge lands on the incoming bubble's **top-right** corner) containing the emoji, with
  a two-descending-bump tail pointing at the anchor corner.
- Pop-in ≈0.25s spring from a dot at the anchor corner (linq f722-728).
- Rides its message through scroll (linq f758-765; poke f384-392, f410-430).
- "Them" side (top-left) is inferred — flag it.

## Proposed change to `director/components.mjs`

Add `TapbackBadge` (v2:88) and a `tapback:{emoji,from}` param on `MessageBubble`/`AppCard`
that parents the badge inside the message group:

```js
TapbackBadge({id, x, y, size, emoji='👍', from='me'})
// children: -badge (blue circle), -tail-bump-1/2, -emoji (text)
```

Placement rule: badge center sits ON the message corner (`x = w - size*0.15`,
`y = -size*0.25` for from:'me' on an incoming message). Pop-in = scale keyframes
`[{t:0,value:.15},{t:.25,value:1,ease:'spring'}]` with `origin` at the anchor corner.

## Proposed change to `component-contracts.md`

Add to "State transitions":

> A Tapback is a child of the message it reacts to, never a thread sibling — parenting is
> what keeps it attached through scroll and camera transforms (verified linq f758-765).
> `from:'me'` anchors top-right of an incoming message; `from:'them'` mirrors (inferred).
