# Conversation input and renderer scene

The JSON authoring input is version 1. Required root keys are `version`,
`conversationId`, `title`, `participants`, `localSenderId` and `frameCount`.
Supply `participants` as a map of stable person IDs to display names. IDs
start with a lowercase letter or digit and may include lowercase letters,
digits, dots, dashes, underscores, and colons. Use unique event and message
IDs even across edits and removals.

| Optional root key | Meaning |
| --- | --- |
| `skin` | `film-paper` (default, plum/lavender) or `film-ink` (blue/gray). |
| `service` | Secondary conversation heading, defaults to Messages |
| `display` | `width` (320–1080), `height` (480–1920) and `textSize` (13–24). Defaults to 390×720 and 16 |
| `canvas` | Output `width` and `height` (160–2560), default to the display size. The display centers on the canvas. |
| `inbox` | Ordered list of `{id,title,preview}` for list and search. Defaults to one entry for the active conversation. |
| `fps` | Whole frames per second, defaults to 24 |
| `assets` | Asset ID to still PNG, JPEG or WebP path relative to the input description |
| `initial` | Ordered `messages`, composer `draft` and boolean `focused` |
| `events` | Ordered, frame-addressed conversation and camera actions |
| `cues` | Objects with stable `id`, `eventId` and signed `offsetSamples` at 48 kHz |

An initial or received message has `id`, `senderId` and `text` and/or
`attachmentIds` and/or `card`. It can include `replyTo` with an earlier message ID.
Outgoing messages can start with `receipt` of `Delivered`, `Read` or
`Failed`. Attachment order determines swipe order. EXIF-oriented stills are normalized during compile so all five engines receive the same orientation. Resources are measured at
compile time and paths are written relative to the scene location. Recompile
when relocating the source or changing assets.

Every event has `id`, `kind`, and zero-based `frame` inside the picture. One
conversation action is allowed per frame. Camera events can share a frame with
one action. Set `durationFrames` to override the motion length or set it to
zero for a cut. The action first affects the declared frame. Numeric settling
may continue over subsequent frames. If two events retarget a moving layer,
the later move starts at the prior rendered transform.

| Kind | Payload and persistent result |
| --- | --- |
| `draft` | `text` sets composer copy. Long copy wraps and the visible draft keeps the last three lines. |
| `focus` | `focused` raises or lowers the keyboard and moves the composer. |
| `send` | `message` with a new `id`; defaults to the local sender and current draft text. Clears draft, returns to newest messages and preserves keyboard focus. |
| `receive` | `message` from a remote participant. Clears that participant's typing indicator. |
| `typing` | Remote `senderId` and boolean `active`. |
| `reaction` | `messageId`, `mark` and optional `senderId` (local by default). Empty mark removes that sender's reaction. |
| `scroll` | `offset` in logical pixels back from the newest content, clamped to the scrollable range. |
| `camera` | `scale` and optional `x`, `y` offsets from the centered display. Transforms the whole screen around its center without changing conversation state. |
| `edit` | `messageId`, `text`. Keeps row identity and adds Edited. |
| `unsend` | `messageId`. Removes message from semantic state and shows a removal line. |
| `receipt` | Outgoing `messageId`, `status`. An explicit receipt moves its label to that message. Empty status hides a label already there. A send can leave the previous label in place until the new receipt appears. |
| `overlay` | `surface` of `conversation` (dismiss), `tray` (optional `items` labels), `context` (`messageId`), `media` (`messageId`), `list`, `search` (optional `query`), or `payment-approval` for a requested `payment-mock` message. |
| `media.page` | Attached `messageId` and zero-based `index`. Slides the photo strip within its own clip. |
| `suggestion` | `phase` of `visible`, `pressed` or `hidden`. Supply a `label` on first reveal. Optional `dismissKeyboard` clears composer focus. |
| `search.query` | `query` on the open search surface. Case-insensitive matching uses authored inbox entries. Dismissing to `conversation` resumes the active conversation. |
| `card.update` | `messageId` and replacement `card`. The card remains attached to the same row. |
| `card.vote` | Poll `messageId`, `optionId` and updated integer `votes`. The chosen row highlights and shows the supplied count. |

The generic card supports `app`, `link`, `location`, `audio`, `file` and
`poll`, with a required `title` and optional `detail` and `action` text.
A poll has two to twelve `options`, each with stable `id`, `label` and integer
`votes`, and an optional `selected` ID. The source description owns counts
and copy. A card action label is editable display content. The film simulator
does not execute app actions.

Use `payment-mock` for an explicitly simulated payment. Its editable card
starts with status `requested`. Open `payment-approval` on its message ID
and dismiss it with an `overlay` event targeting the `conversation` surface.
The later `card.update` with status `paid` requires an explicit dismissal
of that card's review. Leave a hold between dismissal and result when both
need to read separately. The card and sheet carry visible mock labels.
The fixture uses local authored data.
[Editable rehearsal](examples/payment-mock.json)

Search retains its last query if you reopen it without an explicit `query`.
The list and search depict one active conversation plus any additional authored
list rows. Model a cut to a different conversation as a separate scene.

## Layer ownership and renderer API

`ui.camera` moves the clipped logical `ui.screen` within the output canvas.
`ui.header`, `ui.composer`, `ui.keyboard`, `ui.suggestion`, `ui.overlay` and
`ui.inbox` live outside `ui.viewport`. Scroll moves `ui.transcript` inside
the viewport clip. `ui.message/<id>` owns its text, receipt, attachment and
reaction. The media rail has separate horizontal movement and clipping.
Message edits keep the parent ID and make a new editable text/shape revision
with a frame-bounded lifetime. Renderer geometry uses the existing
[measured scene format](../scripts/shared/SCHEMA.md). Its `timeline` follows
Observer's v1 picture/audio contract. It projects message IDs, copy, attachment IDs and page, reply targets,
reactions, edit flags, receipts, typing participants, composer focus and
keyboard state, active surface, anchor and applied scroll offset. Rich card
values, search copy and settling transforms live in the authored description
and scene layers. Use Observer resolver a7a70e7 or later for the expanded
state fields.

The built-in components return native groups, shapes, images or text
from [components.py](components.py), [accessories.py](accessories.py),
[inbox.py](inbox.py) and [rich.py](rich.py).
Layout, state updates and sampled transforms are computed once. The SVG,
React, GSAP, native canvas and Pillow runtimes consume that resulting scene.
Fonts and local image assets stay explicit. Rendering can differ in
antialiasing and glyph fallback depending on the engine.
