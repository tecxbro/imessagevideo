# Reference study — what the six films actually do (frame evidence)

Method: contact sheets at 1fps + scene-detect passes (thresholds 0.25 and 0.08) +
dense frame tiles around every detected cut cluster. Sources:
`projects/*/imessage-recreations/references/*/source.mp4`. Tiles in
`work/originals/reference-study/`.

## Structural archetypes

| film | len | res/fps | real cuts (0.08) | structure |
|---|---|---|---|---|
| 01-photonhq | 21.8s | 1920×1080 30 | ~4 | sizzle montage: title → platform icons → stat-labelled walls → logo mark |
| 02-danieltian | 45.3s | 1920×1080 30 | ~2 (plus a 7-"cut" wipe cluster at 12.07–12.27s) | single-take narrative: one continuous 33s conversation scene |
| 03-photon-mini | 42.0s | 1920×1080 30 | ~15 | phone-on-white demo w/ verbal refrain ("Now your agent can send X") |
| 04-poke | 42.8s | 1440×1080 29.97 | ~14 | screen-recording realism: one linear task shown through real tappable UI states |
| 05-linq | 48.6s | 960×720 30 | ~90 | rapid vignette montage with cross-vignette callbacks |
| 06-gallery (Rene) | 55.5s | 1920×1080 30 | ~14 | brand film: act structure, display type as event, one live-photo moment |

## What makes you want the next shot

**Objects are carried across every transition.** Almost no clean hard cuts inside
the product sections; something physically travels:

- 02 @ ~12.1s: the "Checking what I know about Photon" summary card is punched
  through by a giant magnifier-glyph wipe (`f02/cluster-12s.jpg` — the "("
  graphic sweeps the whole frame) and lands on a *small search field that types
  live* "Se… Searc… Searching the Agent Phone Book". The wipe *is* the cut.
- 02 @ ~13–20s (`f02/flow-12-20s.jpg`): search pill → scrolling wall of phone
  numbers → rows highlight and are picked out → stack into a list with +
  buttons → checkmarks → the agent icons *fall out of the list* as colored dots
  and gather into a cluster that becomes the "Team Offsite, Oct 10" group
  header. Four object-carries chained: query→wall→selection→avatars→group.
- 05 @ ~4–8s (`f05/montage-4-8s.jpg`): app drawer → Games grid → "LET'S PLAY
  CHESS!" invite card sends → reply "Always down ♟" arrives → the *same* chess
  card expands into a full-screen board and pieces start moving. The message
  card becomes the product surface.
- 06 @ ~14–16s (`f06/flow-12-22s.jpg`): a lock-screen notification banner
  ("Heads up: your landlord emailed…") slides *into* the phone and becomes a
  chat message in the Rene thread — same text, new context. Carry across a
  context change, not just a layout change.
- 04: calendar card inside the chat → full "Pick a Time" sheet; restaurant row
  selection → maps.apple.com link card.

**Interruption beats scripted flow.** 02 @ ~26s: mid-delegation, Resy asks
"Budget?" — a sub-question the user must answer ("~$100 per person") before the
payoff cascade. 04 @ ~11s: "where are you rn?" interrupts the task and forces a
keyboard + location-share beat. These are the moments that read as
*conversation*, not a deck.

**Callbacks close loops opened earlier.** 05 books "Cheap flight ATL→SFO" at
~14s, then at ~42s "check-in just opened … Seat 10C — tap to get your boarding
pass" and the ATL→SFO boarding-pass card lands (`f05/flow-36-46s.jpg`). 06:
"It's official: United signed their striker … You called this back in June,
btw." Both films plant and pay off.

**Type is an event, not a section header.** 06's "Tracks what you love" fills
the frame word-by-word *while a chat bubble floats into it*; "Watches your
💬 inbox" sets the Messages icon inside the sentence. 03's refrain "Now your
agent can send 🍕/🎮/▦" works because it's a chorus — identical syntax, new
noun — not a bullet list.

**The camera is always choosing a reading target.** Every film alternates:
full-bleed crop close-up ↔ framed phone ↔ wall/field of many items. Even the
"walls" (01's email stack, 02's phone-number field, 05's phone grid) resolve
into one highlighted element — a pile is never left a pile.

## When the product becomes understandable

| film | moment | what lands it |
|---|---|---|
| 01 | ~4–8s | "Your agent is everywhere" + iMessage/WhatsApp/Telegram/SMS stack |
| 02 | ~6–12s | offsite request typed → "Checking what I know… 9 people, 880 Harrison St, loves sushi" — the agent's *knowledge card*, before the word "agent" explains anything |
| 03 | ~6–10s | first mini-app card materializes inside the chat |
| 04 | ~8s | tappable time chips inside a "Dinner with Sarah" card |
| 05 | ~5s | first game invite sent from the app drawer |
| 06 | ~14s | "Watches your inbox" + landlord notification→chat carry — the latest, earned by a teaser open |

None of the six explains the product with its tagline first. Comprehension
always lands on a *concrete object doing a concrete job* (a card, a chip, a
picker). The promise line lands after or on top of the evidence.

## Holds, rhythm, and the "presentation" trap

- 02 sustains ONE continuous scene for ~33s without a cut — the editing is
  *inside* the frame: arrivals, the Budget? interruption, scrolling caused by
  new content pushing up, the camera reframing as the stack grows. A long take
  stays filmic when the content itself keeps changing the frame.
- 05 averages <1s per shot in montage runs but still reads because each shot
  ends on an understood state (sent card, filled chip, landed board) before
  cutting — it cuts on *completion*, not on a timer.
- Reading holds: cards with long copy ("…3 similar units in your building are
  listed lower. Want me to write a pushback?") hold 3–4s; one-word beats
  ("On us.", "Budget?", "LETS GOOOO") hold ~1–1.5s.
- Act breaks are rare and loud: 06's single white→black hard cut at ~35s is the
  only full-frame tonal flip in all six films — it works because there's
  exactly one.
- Where the films flirt with "presentation": 03's phone-on-white parade and
  01's stat-labelled walls are the most deck-like stretches; both are rescued
  by physical behavior (pizza-emoji particles spilling out of the menu in 03;
  wall tiles drifting/settling in 01) and by staying short.

## Frame/chrome authenticity

04 sells "captured, not rendered": real status bar (9:41), unread badges,
keyboard with a send button, system blur behind sheets, 4:3 960×720-ish crop.
03/02 use clean outlined phone mockups on white. 05 shoots nearly full-frame
UI crops (960×720) — chrome optional, content fills. Lesson: chrome is a
*choice per shot*; mixing crop-full-bleed and framed-device within one film is
normal and is itself an editing tool.

## Sound

All six carry a continuous music bed + discrete UI event sounds (the skill's
`ui-cues/canonical-*.json` documents them: typing per observed glyph batch,
send whooshes, panel whooshes, taps; no sounds on title reveals or AI text).
Long silence: only at the very end of 02/03/06 (logo tail). Sound continuity is
part of why single-take scenes hold — the audio bed bridges what the eye would
otherwise read as "still a slide".

## Checklist distilled for my own films

1. Carry an object across every transition (message→card→surface→avatar).
2. Plant at least one interruption where the agent asks the user something.
3. Plant early, pay off late (callback).
4. Let the camera crop/reframe to a single reading target; never show a pile.
5. One act break max; make it loud.
6. Score type as an event inside the action, not as dividers.
7. Hold long-copy cards ≥3s; keep one-word beats ~1s.
8. Chrome (status bar/keyboard) is a per-shot choice that sells "captured".
9. Sound leads or co-lands with the object carry — send whoosh on the send
   *frame*, typing keys on real glyph frames, keep deliberate silence.
