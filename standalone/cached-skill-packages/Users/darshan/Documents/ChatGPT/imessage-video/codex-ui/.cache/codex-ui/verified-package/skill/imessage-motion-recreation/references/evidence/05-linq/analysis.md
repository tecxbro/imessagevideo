# Linq iMessage Apps reference analysis

## Source evidence
- Original: https://www.linkedin.com/posts/elliottpotter_your-users-never-have-to-leave-imessage-again-activity-7477784121293950976-Dlap
- Acquired from LinkedIn's public JSON-LD `VideoObject.contentUrl`, also present as `<video data-sources>`.
- Local: `source.mp4`; 960×720, 4:3, 30 fps, 48.600 seconds. Audio is present. Metadata is in `probe.json`.
- All footage is a graphic/UI composition. Product photos occur inside app screenshots; no live action needs omitting.
- Main contact sheet samples every 2 seconds. `contact-sheet-halfsec-*.jpg` samples 2 fps with labels near the bin centers (0.25,0.75,...). Full-resolution `keyframes/` contains selected moments.

## Visual language
Near-white background; black SF-style UI type; iMessage blue outbound and light gray inbound bubbles; translucent white input field; small soft shadows; large areas of whitespace. UI text appears close to Apple's system sans, but the video carries raster text and does not establish an exact font binary. Do not claim font-exact reproduction without comparing a licensed SF font. Scene transitions frequently use vertical translation and motion blur, scaling into UI screenshots, and rapid detail pans. Much of the source is high-detail app artwork rather than primitive shapes.

## Graphic timeline (seconds, visual inspection at 0.5s steps; refine boundary frame when building)
| Range | Content and motion |
|---|---|
| 0.00–3.50 | Floating centered input row: circular plus left, long white rounded input, blue send circle right. Placeholder iMessage changes to progressively typed `Yo i'm bored, chess battle?`; insertion cursor. |
| 3.50–4.33 | Fast enlarged app drawer scroll: Photos, Apple Cash, Polls, Store, GamePigeon, Threadsby, Star Flights. White rounded panel and icons; strong vertical blur. |
| 4.33–4.93 | GamePigeon 2×3 tile grid (8 BALL, CHESS, FOUR IN A ROW, WORD GAMES, CRAZY 8, CUP PONG). |
| 4.93–6.97 | Rounded chess rich link preview with play circle, `LET'S PLAY CHESS!`; blue message below `Yo i'm bored, chess battle?`. Delivered/Read state, gray `Always down ♟` reply slides in. |
| 6.97–8.57 | Zoom to tall wood chessboard, black/white line-art pieces. White pawn selected with blue glow; black pawn moves. |
| 8.57–10.57 | Blue bubble `hey can you find me a one way flight from Atlanta to San Francisco in July? looking for something cheap`; tiny plane reaction emerges at upper left. |
| 10.57–12.07 | Gray reply `On it! 👀 Found a few options, here's the cheapest one way:` then rich preview showing Golden Gate Bridge, `Cheap flight from ATL to SFO`, `Tap for details`. |
| 12.07–13.90 | Flight Details blue app sheet expands over blurred chat. White flight card ATL → SFO, Frontier, July 2 2026, $199. Camera pans down to Basic/Economy fare cards. |
| 13.90–15.63 | Blue airplane seat-selection screen. White seat boxes over sky; selected 10C; white bottom summary Total $235 and blue Book. |
| 15.63–17.10 | Fade sheet to gray message `Your flight is booked! ✈️ / Frontier Airlines / July 2 | 1 passenger / Aircraft: Airbus A321`. |
| 17.10–19.30 | Blue `i wanna check out some necklaces`; gray `Here's what's hot right now 🔥`; rich `Men's Jewelry / Tap for details`. |
| 19.30–21.55 | Jewelry app opens over blurred chat; 2×2 white product grid, pans/zooms to black Vivienne Westwood pendant necklace. Bottom black Add to Bag button. |
| 21.55–22.85 | Gray `Order confirmed, I'll ping you when tracking's ready 📦` floats and translates away. |
| 22.85–25.33 | Blue `can you order my weekly groceries?`; gray `Sure, it'll be $166.89`; black Apple Cash card `$166.89 Request` with white Pay pill; blue thumbs-up reaction. |
| 25.33–27.67 | Black Apple Cash panel opens below input. Rolling amount digits settle at $166.89 with minus and plus circles. `Request` and `Send` pills. |
| 27.67–28.83 | Gray `Got it, ordering now 🛒`. |
| 28.83–31.37 | Tall chess UI with You/MyAI header. Rapid chess moves. Yellow `YOU WON!!` overlay; colored confetti falls. |
| 31.37–33.17 | Dark Four in a Row app, You/Friday, Red/Yellow player tags; red/yellow circular counters fall into board. |
| 33.17–35.63 | Foodash group-order white sheet. Shake Shack SoHo, names Dakota/Jamie(you)/Dillion/Priya/Carlos/Siobhan and orders. Dillion adds $12; subtotal changes $33→$45. |
| 35.63–38.13 | Boqueria Soho map/business card. Name, 4.6 rating, Directions black pill, image carousel slides storefront→food→interior. |
| 38.13–39.50 | Gray `Oh, and check-in just opened for your July 2 flight to SFO! Gate 37, Seat 10C — tap to get your boarding pass. ✈️`. |
| 39.50–40.63 | Enlarged gradient boarding pass ATL ✈ SFO; passenger Nikki Hanse, Gate37, Seat10C; date 2July2026, boarding2:50pm. |
| 40.63–42.27 | Pull back into moving grid of rounded iPhone mockups with app examples. |
| 42.27–44.60 | Centered Messages icon + `iMessage Apps`; second line `that supercharge your 🤖 agents` reveals with moving blur/opacity. |
| 44.60–45.93 | Centered `What will you build?` on white. |
| 45.93–48.00 | Centered black line-art Linq icon + `linq` wordmark; fades toward white. |
| 48.00–48.60 | White tail. |

## Measurement and reconstruction notes
The first input field, bubbles, Apple Cash card, and title cards are suitable for independent vector recreation across engines. Games, airfare sheets, jewelry, restaurant photos and phone gallery require asset extraction or careful rebuilding. Cropped reference pixels can preserve assets such as photos and logos; full video frames must remain labeled reference images rather than being presented as new editable artwork. Preserve original 4:3 composition; do not stretch to16:9. For close QA compare native960×720 frames at actual frame indices, not contact sheet thumbnails. `scene-detection.log` contains candidate cuts, including fast UI movement false positives; visual ranges above are inspected approximations.
