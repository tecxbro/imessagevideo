# Shot pitch

Two friends, Alex and Maya, lock in concert tickets over iMessage: Alex proposes grabbing Neon Pines tickets, the seating options get browsed under one pinned heading, the booking is celebrated in the thread, and the finished ticket is in hand.

**Director** · 30 fps · awaiting confirmation

## ask · frames 0–71

Open the story: Alex proposes grabbing tickets and Maya says yes, establishing both friends and the goal.

Alex's draft types into the composer, flies into the transcript as a blue bubble, and Maya's gray reply arrives after a quiet beat. Header and composer stay fixed.

> Neon Pines tickets drop at 10 - grab us two?

Send an outgoing text and receive a reply Draft characters arrive in the composer, transfer into an outgoing blue bubble, and an incoming gray reply arrives after a pause. The phone, conversation header, composer field and reading area stay in place.

Content settings

```json
{
  "heading": "Maya",
  "reply": "YES. Get us in!",
  "detail": "iMessage - Today"
}
```

![Board](board-ask.png)

[Preview](proof-ask/preview.mp4)

[Code](proof-ask/scene.json)

[Motion example](../../../imessagevideo-dl/skill/imessage-video/assets/seed/previews/conversation-handoff.mp4)

[Implementation](../../../imessagevideo-dl/skill/imessage-video/assets/seed/runtime/motion/packs/handoff.mjs)

## browse · frames 72–143

Show exactly which message is being answered before the reply sends.

Maya's 'YES. Get us in!' bubble follows the swipe; an arrow appears behind it, the row springs back, and a quote draft opens above the composer naming the answered message.

> YES. Get us in!

Swipe one message to quote it Only the chosen bubble follows the drag. An arrow appears behind it, then the row returns and its quote opens above the composer. Other transcript rows, header and reply input position.

Content settings

```json
{
  "heading": "Maya",
  "reply": "Neon Pines tickets drop at 10 - grab us two?",
  "title": "Replying to Maya"
}
```

![Board](board-quote.png)

[Preview](proof-quote/preview.mp4)

[Code](proof-quote/scene.json)

[Motion example](../../../imessagevideo-dl/skill/imessage-video/assets/seed/previews/swipe-to-quote.mp4)

[Implementation](../../../imessagevideo-dl/skill/imessage-video/assets/seed/runtime/motion/packs/conversation.mjs)

## celebrate · frames 144–215

Pay off the booking emotionally: Alex's 'booked' news earns Maya's excited reply and it gets hearted.

Alex's outgoing 'booked' bubble sits above Maya's incoming reply; the Love reaction arcs in and lands on Maya's bubble as a badge while the rest of the transcript stays put.

> You're the BEST!

Attach a chosen reaction to its message The selected reaction follows a curved approach, shrinks into a corner badge and settles as the nearby text row makes room. Message copy, heading and composer. Earlier messages stay put.

Content settings

```json
{
  "heading": "Maya",
  "reply": "Booked - two GA floor tickets",
  "action": "Love"
}
```

![Board](board-celebrate.png)

[Preview](proof-celebrate/preview.mp4)

[Code](proof-celebrate/scene.json)

[Motion example](../../../imessagevideo-dl/skill/imessage-video/assets/seed/previews/reaction-attach.mp4)

[Implementation](../../../imessagevideo-dl/skill/imessage-video/assets/seed/runtime/motion/packs/conversation.mjs)

## ticket · frames 216–287

Close with the secured ticket itself: the stub tears free, so the ticket is real and usable.

A Neon Pines ticket fills the card; its perforated stub tilts along the seam and drops away while the main ticket and backdrop stay pinned.

> The Neon Pines

Separate a ticket along its perforation A perforated seam parts left to right as the stub tilts around the still-joined edge, then drops once detached. The main ticket, its copy and the backdrop stay pinned.

Content settings

```json
{
  "heading": "Maya",
  "detail": "GA Floor - 2 tickets - Fri Jun 12",
  "action": "Open"
}
```

![Board](board-ticket.png)

[Preview](proof-ticket/preview.mp4)

[Code](proof-ticket/scene.json)

[Motion example](../../../imessagevideo-dl/skill/imessage-video/assets/seed/previews/tear-perforated-ticket.mp4)

[Implementation](../../../imessagevideo-dl/skill/imessage-video/assets/seed/runtime/motion/packs/inherited.mjs)


Plan revision `70b1910780e9d2dcdfc5f5a44b5408b8c6beb1d6e1c58900076b2453840fb8c5`
