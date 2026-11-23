# Rene gallery reference analysis

## Source evidence
- Supplied gallery URL: https://launchvideos.gallery/videos/1724779c-9543-4a4e-bd12-bafceb1cc90f
- Page title identifies **Rene — a multiplayer…**, not Photon. Its exact video URL is public in `og:video` and the `<video src>`.
- Local `source.mp4`: 1920×1080,16:9,30fps,55.509333seconds. Audio present; see `probe.json`.
- Initial CDNGET returned403. A browser User-Agent plus the gallery Referer succeeded. This was an ordinary media/header mismatch, not a network-policy restriction. Evidence is saved in `cdn-response.json`.
- Pure graphic ranges: 0.000–34.966667 and41.000–55.509333. Live action is34.966667–41.000. User allows focusing only on graphics, so omit this interval or rebuild only its message overlays over a neutral background.
- Full-resolution selected moments in `keyframes/`;2fps sheets in `contact-sheet-halfsec-*.jpg`.

## Visual system
Near-white background; Apple-style rounded light gray inbound message bubbles and bright cyan/blue outbound bubbles. Black sans display type centered on white, approximate SF/system sans. Rene wordmark switches to a serif face beside a small black line-art head mascot. Phone frame is silver/chrome with black bezel, dynamic island,12:02 status clock. Blurred fades mask the bottom of phone mockups. Black title cards at41–44.4s. Green accent phrase `best contact` in intro. Exact font family and easing functions cannot be proven from encoded pixels alone; fit against selected source frames.

## Graphic timeline (seconds; boundaries between keyframes require frame-level refinement when rebuilding)
| Range | Content and movement |
|---|---|
| 0–1 | Large centered gray iMessage bubble with avatar: Marcus, `We've been talking about this trip since January`; slight zoom/pan begins. |
| 1–3.60 | Camera pulls back to silver iPhone group conversation `Cabin trip 🏕️`. Priya: `Someone just pick a weekend, I'm not the mom of this group`; Dan: `Not me, I organized the last one`; Rene: `Oct17is the first weekend all of you are free`. |
| 3.60–8.00 | Push into lower phone conversation. Rene: `Want me to book the lakeside cabin Dan sent? Before someone “gets busy” again 👀`; Priya: `Ok we gotta commit 😅`; blue `Let's go! Book it`; Rene: `Done. In your calendars 🏕️`. Keyboard appears at bottom. |
| 8.00–10.50 | Phone exits, centered type `Introducing` resolves from blur; small mascot and serif `Rene` reveals to its right. |
| 10.50–12.50 | `The best contact in your phone`, with `best contact` green; second line `with multiplayer mode` appears by~12.2s. |
| 12.50–13.80 | `Watches your inbox`; green Messages icon inserts between your/inbox, pushing text apart. |
| 13.80–15.37 | Bottom half of iPhone lock screen drops in from top. Blue-green wallpaper; translucent Rene notification: `Heads up: Your landlord emailed about the renewal. Rent's going up8%`. |
| 15.37–18.50 | Notification becomes enlarged chat bubbles. `3similar units in your building are listed lower. Want me to write a pushback?`; blue `Yes plz`; full iPhone rises/pulls back, blurred email list fans behind; `It's in your drafts. Friendly but firm. You've got this`. |
| 18.50–20.50 | Centered `Remembers your people` reveals from blur/letter movement. |
| 20.50–22.90 | Circular photographic face avatars burst into a cluster around phrase, with soft shadows and varying scale; translucent Rene notification: `Emma's birthday is Saturday 🎁`. |
| 22.90–27.25 | iPhone rises and shows birthday conversation. `She's been wanting to try film photography — found a Fuji half frame,$189,arrives Friday`; blue `Wait,you remember that?`, `Order it. She's gonna cry`; gray `Done. Gift wrap on 🎁`, `I remember everything 😉`. |
| 27.25–29.60 | Large kinetic type: `Tracks what` → `you` → `love`. Words slide/blur. In love, soccer ball replaces o; black l strokes tip/fall away. |
| 29.60–34.966667 | Soccer ball bounces above/around gray bubble: `It's official: United signed their striker. Announced2min ago 🚨`; blue `LETS GOOOO`; gray `£85M,five years. You called this back in June,btw`. |
| 34.966667–41.000 | Live-action shot of two people on sports bench. Overlay messages and `Rene remembers everything about you`; excluded from pure graphics remit. |
| 41.000–43.35 | Black background, white centered kinetic text `Does the work for you` with small white work/briefcase icon inserted before work. |
| 43.35–44.40 | Black background, white `Lives where you`. |
| 44.40–47.40 | White background, black `already` then `text`; Messages, Telegram, WhatsApp icons pop into gap with soft drop shadows. |
| 47.40–49.10 | Centered mascot + serif Rene logo reveal. |
| 49.10–50.55 | Centered `Just like a friend`. |
| 50.55–51.55 | Centered `Start now`. |
| 51.55–55.509333 | Centered QRcode beside `rene.co` in black; initial opacity settles to solid by52.2s, then holds. |

## Reconstruction strategy
Keep exact1920×1080 geometry and30fps. Intro/title typography, bubbles and soccer ball motion are vector-friendly. Phone body, blue-green wallpaper, Rene mascot, avatar photos, app icons and QRcode can be extracted as genuine static assets and then animated independently; compare crops at native resolution. Avoid reproducing the actual source video with a video layer and labeling it an independent rebuild. An editable rebuild should expose text, bubbles, phone, icons and animation tracks separately. The animation includes motion blur, so frame comparisons must include transition frames as well as settled states.
