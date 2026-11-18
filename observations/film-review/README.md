# Six source films — observer film review

Contact sheets (`*-contact-A.jpg` = ~20 frames spanning the whole film;
`*-contact-B.jpg` = ~20 frames over the first ~22 s at denser grain) plus
full-res frames for `03-photon-mini` hard sections. All extracted with
ffmpeg `select`/`fps`+`tile` filters on the local `source.mp4` files.

| Film | WxH | fps | frames | length | character |
|---|---|---|---|---|---|
| 01-photonhq | 1920x1080 | 30 | 655 | 21.8 s | Cross-channel reach montage |
| 02-danieltian | 1920x1080 | 30 | 1360 | 45.3 s | Multi-agent group-chat story |
| 03-photon-mini | 1920x1080 | 30 | 1260 | 42.0 s | Mini-apps inside iMessage |
| 04-poke | 1440x1080 | 29.97 | 1283 | 42.8 s | iMessage assistant (KNOWN-DEFECT training case — excluded) |
| 05-linq | 960x720 | 30 | 1458 | 48.6 s | iMessage-app showcase, many interiors |
| 06-gallery (Rene) | 1920x1080 | 30 | 1664 | 55.5 s | Mixed live-action + motion; longest |

## 01-photonhq — "Introducing Photon 2.0"
Title card → blue cursor/pill button ("with just one click") → channel icon
column (iMessage/WhatsApp/Telegram/SMS/Email) → "free for everyone" → giant
scrolling message walls: green SMS threads, email threads with brand logos
(Airbnb, Disney+), dark-mode voice-minute rows with avatars, iMessage walls,
WhatsApp/Telegram walls → "Even 10DLC registration ✓" → `photon.codes/beta`
→ quotation-mark logo.

Hardest: extreme bubble density — dozens of distinct-copy bubbles per wall,
plus non-iMessage surfaces (email clients, dark call UI, green SMS) so the
iMessage components cover only part of it. Shortest film but very high
unique-element count. Least iMessage-native of the set.

## 02-danieltian — "Agent to Agent in iMessage Group Chats"
Title → phone chrome w/ Muse conversation → "Checking what I know about
Photon…" checklist → "the Agent Phone Book" (scrolling phone-number columns)
→ colored agent-avatar clusters converging into a "Team Offsite, Oct 10"
group → @mention routing (@Airbnb/@Lyft/@Resy) → Airbnb rich card ("Lake view
Cabin in Tahoe Vista") → budget negotiation → booking confirmations →
three taglines → URL.

Hardest: avatar-cluster convergence choreography, phone-book column scroll,
multi-act pacing over 45 s. Best teaching coverage (3 studies, 567 curated
frames) but longest pure-motion narrative.

## 03-photon-mini — "API for Mini Apps in iMessage"  ← CHOSEN UNFAMILIAR FILM
Title → iPhone "Agent" chat (Dynamic Island chrome) → "Draft an email to
Alice" task + working state → Mail draft bubble → "Dinner This Week" doc card
→ Team Lunch group chat (Memoji header) → "Can someone order lunch for us?"
→ Uber Eats mini-app card → full-sheet Uber Eats menu (f680: food photos,
prices, Memoji pickers, cart badge) → "Jump Jump" 3D game mini-app card
(f800) → world-release finale (f760: pizza/ramen/Order! bubbles floating in
world space around the phone) → mini-app mosaic grid (~20 tiles) →
"agentic apps"/"mini apps" taglines → `tryphoton.ai` → Photon logo.

Hardest: (a) Uber Eats menu interior — photographic food thumbs + per-item
Memoji overlays; (b) world-release — many props at varied scale/rotation
detached into canvas space (study mini.world_release covers 730–799);
(c) detailed iPhone chrome + group header; (d) the ~20-tile end mosaic with
distinct mini-app interiors; (e) Jump Jump game artwork.
Tractable: title cards, conversation motion, send flight, sheet expand.

## 04-poke — excluded (documented training case)
Poke icon morph → Messages list → "Dinner with Sarah" time-picker → emoji
cuisine list → map pin → restaurant list → voice-memo waveform → capability
toggles → app-icon grid → Poke.com. Contains the documented 12-frame
selection-timing defect (src633 vs GSAP645).

## 05-linq — "iMessage Apps that supercharge your agents"
Games grid (8 Ball/Chess/Four in a Row/Word Games/Crazy 8/Cup Pong) → chess
board → "Yo i'm bored, chess ba" composer → ATL→SFO flight card ($199,
Basic/Economy) → airplane seat-map picker → jewelry store → grocery order →
Apple Cash $166.89 request + dark keypad → chess vs MyAI → Connect Four →
Shake Shack group order → Boqueria Soho restaurant card → boarding-pass
alert → three-phone montage → tagline → linq logo.

Hardest: SEVEN+ distinct polished app interiors — the highest interior
diversity of the set. Only 960x720 (coarser ground truth). Arguably the
hardest non-pathological film.

## 06-gallery (Rene) — "The best contact in your phone"
Cabin-trip group chat → title cards with inline emoji ("Watches your 📨
inbox", "Tracks what you l❤️ve") → circular contact-photo collage → landlord
email digest card → sports alert ("United signed their striker") →
"LETS GOOOO" → LIVE-ACTION segments (three women at table; ~181 source frames
intentionally omitted from the accepted scene) → "Does the work for you" →
"Lives where you already text" (iMessage/Telegram/WhatsApp) → "rene.co" + QR.

Pathological for a timed recreation trial: live-action handling, longest
runtime, and non-1:1 source↔output mapping in the ground truth itself.
