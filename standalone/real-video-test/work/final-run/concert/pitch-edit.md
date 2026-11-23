# Shot pitch

Jo and Tessa get Afterglow tickets. Show how they decide where to sit and confirm both tickets.

**Director** · 30 fps · awaiting confirmation

## open · frames 0–107

Establish a concrete invitation.

Jo sends a draft into the conversation.

> Tickets for Afterglow?

Send from the composer into history The draft box collapses toward its right edge while the outgoing balloon rises, slightly overshoots, then settles into its transcript slot. The conversation heading, prior reply, and composer field stay fixed. The send control disappears at the trigger.

Content settings

```json
{
  "heading": "Jo + Tessa",
  "reply": "Presale just opened."
}
```

![Board](proof-open/board.png)

[Preview](proof-open/preview.mp4)

[Code](proof-open/scene.json)

[Motion example](../../imessagevideo/skill/imessage-video/assets/seed/previews/draft-send-flight.mp4)

[Implementation](../../imessagevideo/skill/imessage-video/assets/seed/runtime/motion/packs/conversation.mjs)

## choice · frames 108–203

Show the venue options changing while Jo’s meeting message stays visible.

Keep the title and ‘Meet at the doors’ bubble pinned. Swipe the clipped ticket strip to the left with the Linq restaurant-photo timing.

> Meet at the doors

Slide the photos beneath a fixed heading Adjacent photos translate together on one horizontally clipped rail. The heading, viewport, divider and supporting footer stay in place.

Content settings

```json
{
  "heading": "Jo + Tessa",
  "detail": "Afterglow · Friday",
  "photos": [
    "art/ticket-1.png",
    "art/ticket-2.png",
    "art/ticket-3.png",
    "art/ticket-4.png"
  ]
}
```

![Board](proof-donor-edit/board.png)

[Preview](proof-donor-edit/preview.mp4)

[Code](proof-donor-edit/scene.json)

[Photo 1](art/ticket-1.png)

[Photo 2](art/ticket-2.png)

[Photo 3](art/ticket-3.png)

[Photo 4](art/ticket-4.png)

[Motion example](../../imessagevideo/skill/imessage-video/assets/seed/previews/photos-under-fixed-heading.mp4)

[Implementation](../../imessagevideo/skill/imessage-video/assets/seed/runtime/motion/packs/core.mjs)

## payoff · frames 204–311

Confirm that both friends have a ticket.

The confirmation leaves the composer and settles below the plan.

> Got both tickets!

Send from the composer into history The draft box collapses toward its right edge while the outgoing balloon rises, slightly overshoots, then settles into its transcript slot. The conversation heading, prior reply, and composer field stay fixed. The send control disappears at the trigger.

Content settings

```json
{
  "heading": "Jo + Tessa",
  "reply": "Floor works for me."
}
```

![Board](proof-payoff/board.png)

[Preview](proof-payoff/preview.mp4)

[Code](proof-payoff/scene.json)

[Motion example](../../imessagevideo/skill/imessage-video/assets/seed/previews/draft-send-flight.mp4)

[Implementation](../../imessagevideo/skill/imessage-video/assets/seed/runtime/motion/packs/conversation.mjs)


Plan revision `a144fa541fc3b208d4c1a1d04db8f9f571d043ddcd699c7a65fc5bb5c942b16f`
