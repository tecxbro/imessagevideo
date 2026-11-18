# P4 — Conversation details: TypingIndicator, sender chrome, DeliveryStatus

**Priorities 5, 7, 8.** Cheap components, high credibility return; all missing in v1.

## Proposed additions to `director/components.mjs`

```js
TypingIndicator({id, x, y, fontSize, t0, cycles})
// gray pill + 3 dots rising in sequence (~0.15s stagger, ~0.9s loop).
// Sits at incoming position; in group chat align beside the sender avatar.
// Evidence: danieltian ~f185-230, photon-mini.

// on MessageBubble:
senderName   // gray label ABOVE the bubble (left-aligned with bubble edge)
senderAvatar // small circle at bubble-left, aligned to the last row's bottom
// Every group incoming message carries both (gallery "Cabin trip" f60-200;
// danieltian f950+ "Airbnb"/"Lyft"/"Resy" name labels). Reserve a
// fontSize*2.3 left gutter for the avatar.

DeliveryStatus({id, y, anchorX, copy='Delivered', fontSize, start})
// small gray right-aligned label under the LAST outgoing bubble;
// upgrades Delivered→"Read h:mm" (linq f145-175).
```

## Proposed change to `component-contracts.md`

Append to the anatomy paragraph:

> Group conversations carry sender chrome — a small avatar at the incoming bubble's left
> and a gray sender-name label above it; omitting both reads as a 1:1 chat pasted into a
> group story. A typing indicator (gray pill, three sequentially-bouncing dots) occupies the
> incoming slot before a reply arrives. "Delivered"/"Read h:mm" sits right-aligned under the
> last outgoing bubble only.
