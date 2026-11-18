# Attachment surfaces — doc claims vs verified footage

Sources compared: https://onkeiki.com/docs/cards and https://onkeiki.com/docs/imessage-apps
(fetched 2026 — claims treated as hypotheses, footage is truth).

## Doc claims

- cards doc: `render_cards` delivers N slides as ONE media message; "4+ cards render as a
  swipeable stack on iMessage" (photo-stack style); optional `caption`; `fallback_text` sent
  when media can't carry. Cards are rendered PNGs, 690x920 template.
- imessage-apps doc: `send_widget`/`presentation{type:"app"}` delivers an iMessage APP card —
  an interactive message that opens an HTTPS page in the Vault/extension app; direct
  conversations only (no groups); optional caption/subcaption.

## Verified in footage

- **Arrival**: an app message arrives as a rounded card in the thread, inline with bubbles.
  It carries the sender's APP ICON as a circular badge overlapping the **top-left** corner
  (GamePigeon chess card, 05-linq f136-180; the poll card and restaurant cards in 04-poke
  share the pattern). A short caption line under the content ("Tap for details", "LET'S PLAY
  CHESS!") acts as the CTA.
- **Expand**: tapping the card morphs it into a fullscreen app panel — same surface grows to
  cover the thread (Flight Details with seat map + Back + bottom "Back" bar, 05-linq f350-410;
  Jewelry grid picker + black "Add to Bag" bar f585-690; Apple Cash "−$166.89 + Request/Send"
  pay sheet f765-820). It is NOT a push navigation; the card's own surface expands.
- **Clip**: card content is clipped to the card's rounded rect. The restaurant card's photo
  strip proves it: photos translate X (leftward, ~continuous) UNDER fixed chrome — title,
  "Directions" pill and Overview/Reserve/Menu/Reviews tabs stay put; only the image row moves
  and only inside its own bounds (05-linq f1050-1150 ≈ frames 1091-1111 in the brief,
  `linq-strip-sheet.png`). Strip ≈ a carousel inside the card, not iOS's photo-message stack.
- **Badge anchoring**: the app-icon badge and any tapback badge ride the card's transform —
  verified for the tapback during thread scroll (behavior-evidence Q1); the icon badge is
  drawn inside the card group in the measured scene (`v10-cash-reply` children).
- **Collage vs stack**: no film shows the docs' "4+ cards as a swipeable stack" (iOS photo
  stack). Linq's multi-image surface is a single card with an internal scrolling strip.
  Doc claim remains plausible for iOS photo albums but is UNVERIFIED in this library.
- **Composer "+" sheet**: the + button opens a vertical app list (Photos, Apple Cash, Polls,
  Store, then scroll → GamePigeon, Threadsby, Star Flights…) that becomes the Games grid
  (05-linq f95-135, `linq-send-sheet.png`). This is the iOS 17+ app drawer, distinct from a
  bottom sheet modal — it replaces the keyboard area.

## Doc claims NOT observable in footage (mark honestly)

- 4+ slide "swipeable stack" rendering — not present in any of the six films.
- Group-conversation restriction — group chats DO carry app cards in footage (danieltian
  group thread has cards labeled Airbnb/Resy) — but that's the films' authored framing;
  the doc restriction is about Keiki's delivery transport, a different layer. Don't overrule.
- `live` flag / Vault token mechanics — transport detail, invisible in film.

## Component implications (v2)

- `AppCard` needs: appBadge circle anchored top-left overlapping edge, media/banner slot
  (clipped), title, caption row, optional CTA pill, and a `tap`→`expanded` state pair so
  filmmakers can morph card→panel (scale/position tracks on the SAME layer ids).
- `PhotoStrip`: image children translate x inside a `clip` rect; chrome siblings above it.
- `TapbackBadge`: parent it inside the bubble/card group so any scroll/transform carries it.
- `Composer`: `+` affordance opens an app-list overlay (separate `AppDrawer` builder).
