# What makes it a film, not a presentation — working evidence

Collected while building film-01 ("Offload", 890f @30fps, `exports/first-export.mp4`)
and the brief-02 mutation test (270f). Frame numbers are output frames.

## Choices that pushed toward FILM

1. **Cold open inside an action** (f0–41). The composer is mid-keystroke before
   the viewer knows what product this is. A presentation opens with a title
   card announcing one; a film lets an action pose the question. Same move as
   the DanielTian reference opening mid-thought.

2. **Withheld answer, then a specific answer** (f42–80). The ask goes out at
   f54; the listing card lands at f80 — ~1s of typing dots makes the arrival
   read as *earned*, and the card answers with a real listing, not a category.

3. **The cutaway** (f296–318). The film abandons the protagonist's thread and
   pushes into the buyer's conversation — horizontally, mid-sentence, with
   "I can work with this." still on screen. Presentations never leave the
   demo path; films let the edit travel. This is the single strongest "edited"
   signal in the piece.

4. **Characterization through reply rhythm** (f326–556). Nina's replies arrive
   after typing dots; the agent's counters land with NO dots (f374, f500) —
   speed-as-competence. Dots are humanity, not a loading spinner. Applying
   dots to the agent would have read as the product thinking slowly.

5. **A deliberate quiet pocket** (f244–292). ~1.6s of nothing-new before the
   cutaway. Contrast is what makes the push read as a scene change; back-to-back
   arrivals would read as a feed.

6. **The tap travels** (f656–668). "Take it" presses down inside the card, then
   the chip itself detaches and lands as the outgoing bubble — the user's
   action literally becomes the message. Catalog ref: poke-choice-to-outgoing.
   A presentation cross-fades to the next state; this *carries the object*.

7. **Consequence lands late and loud** (f668→698). The send happens, then a
   30f gap, then SOLD slams over the card. If the stamp had appeared with the
   card (or instantly on send) it would read as a UI state change; the delay
   makes it a verdict. This is the film's only loud accent by design.

8. **Receipts as cascade, not summary** (f698–806). SOLD → shipping label →
   cash pill arrive as separate small beats while the outgoing bubble is still
   on screen — proof accumulating. A one-shot "success state" would be a
   presentation slide.

9. **The endcard is punctuation, not opening** (f808+). Wordmark + one line,
   after the story ends. Typography earned by the film rather than introducing it.

10. **One set, one grammar** (throughout). Portrait frame + iOS chrome persist;
    the camera never moves. Restraint reads as confidence; the reference films
    (Poke, Linq) move the camera only when space itself is the point.

## Choices that pulled toward PRESENTATION (honest)

- **The offer chips are a list** (f208–270). Three items arriving in sequence
  is structurally a bullet list; varied timing softened it but didn't remove it.
  Candidate fix: offers arriving on a slacker rhythm (two at once, one late).
- **Deal card is static during its hold** (f640–656). A live element would add
  film-ness — but inventing motion the product wouldn't do violates
  no-invented-capability, so it stays still. Correct-but-static.
- **No motivated push-in on SOLD** (f698). A 6% scale ease over the payoff hold
  would have enlarged the moment; omitted because static-frame restraint was
  the safer authored choice. Worth trying in a revision.
- **Negotiation content is conventional** (thread B). The cutaway supplies the
  novelty; the chat itself is a normal chat. Acceptable — the point was the
  agent's presence in someone else's conversation.
- **UI-only sound leaves the quiet pocket ambiguous** (f244–292). Without a
  bed, deliberate quiet can read as unfinished. Flagged to the sound agent as
  intent, not a bug — they own the bed.

## Rejected during authorship (and why)

- **Message wall of offers** — scale isn't the promise; one readable
  transaction is. Wall would be breadth-language for a depth-product.
- **Photo→listing morph** — no identity continuity (a bike photo isn't a
  listing entry); morph would be decoration, not grammar.
- **Dots before agent replies** — covered above; rhythm IS the character.
- **Title card open** — presentation grammar; killed in favor of the cold open.

## What the brief-02 test proved about generality

The mutation test (one card changing state in place, clock-chip montage,
proactive agent, minimal scroll) produced a visibly different motion signature
with no schema fights: layer `start/end` windows + per-property keyframes
handled it. The grammar's primitives are arrival-*agnostic* — the friction
found was documentation-level (no named pattern for "persistent object with
states"), see `skill-proposals/`.
