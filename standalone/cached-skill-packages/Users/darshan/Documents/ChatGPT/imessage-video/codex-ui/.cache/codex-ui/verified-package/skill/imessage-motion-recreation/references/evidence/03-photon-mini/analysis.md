# Photon Mini Apps API — acquisition analysis

This is the historical coarse acquisition inventory. Several transition times were corrected through native-frame measurement during reconstruction; use `README-recreation.md`, `recreation-status.json`, and the frozen-scene change logs for the final implementation and current verification status.

Acquired original official highest-resolution MP4. Video is 1920×1080, 30 fps, 1260 frames / 42.000 s. Container/audio extend to about 42.167 s. This is entirely graphic animation; no live action is excluded.

## Visual system

- Flat near-white background (check native frames before final color matching), black sans-serif text consistent with Apple/SF family; typography cannot be positively identified from pixels alone.
- Polished black/silver iPhone with Dynamic Island, soft dark edge reflections and fine hardware highlights. Camera uses continuous pan/zoom on the device and its displayed interface; many screen details are too small to reproduce accurately from overview sheets and need native-frame crops.
- iMessage incoming bubbles pale neutral gray with left tails; outgoing bubbles cyan/blue vertical gradient with right tails. Native Apple emoji/Memoji in avatars. The screens are app mocks and not live action.
- Phone composition generally centered on white, variable crop/scale. UI uses realistic text, menu sheets, small icons, hairline dividers, gradients and image previews.
- Recreating only the phone rectangle would miss the source's large camera scale changes, screen crop, hardware geometry, layered sheets, Memoji motion and rich preview details.

## Timeline evidence

The numbered diagnostic frames are extracted at 1 fps and labeled by sampling index; use them for coarse shot structure only. Final motion timing must be measured at 30 fps around each transition. `scene-cuts.json` supplies automatic cut candidates, not authoritative semantic cuts.

| Approx range (seconds) | Observed graphics / copy |
|---|---|
| 0–1.6 | Two centered black title lines: “Introducing API for” then App Store icon + “Mini Apps in” + Messages icon + “iMessage”. Text reveals progressively. |
| 1.6–3 | Phone grows/slides into centered composition; Agent robot avatar and name visible. |
| 3–4.7 | Blue outgoing message “Draft an email to Alice about our dinner.”; incoming typing dots then “Working on it.” Camera slowly enlarges device. |
| 5–6.8 | Mail rich preview bubble arrives: sky-blue card with little paper-plane badge, email thumbnail, gray title/footer “Mail” / “To: Alice”. |
| 6.8–10 | Modal sheet “Dinner This Week” expands over darkened phone; close button, cyan round send arrow, recipient Alice, sender ryan@photon.codes, subject, body. Body starts “Hi Alice, Just wanted to check if we're still on for dinner this week. I'm free Thursday or Friday evening. Let me know what works best for you. Looking forward to catching up. Best, Ryan”. Text selection changes Thursday/Friday to Saturday/Sunday (native frames needed to transcribe exact final edit). |
| 10–11.6 | Rapid push into the cyan send arrow near upper right, then zooms back to full phone. |
| 11.6–13.7 | Sheet closes; mail bubble plus “Sent.” and “I'll let you know when she replies.” incoming bubbles. |
| 13.7–15.5 | Enlarged group Memoji cluster sweeps into frame, shrinks to chat header titled “Team Lunch”. |
| 15.5–18 | Phone group conversation: Alice “Can someone order lunch for us?”; Bob “Vegetarian for me.”; blue user “Something light.” |
| 18–20.7 | Agent message “Taking everyone's preferences into account, I found a few good options.” and Uber Eats rich preview for Lanespan Pizza & Pub (Emeryville). |
| 20.7–23.4 | Uber Eats sheet rises; list with photos and prices: Grilled Chicken Rice Bowl $15.4, Roasted Veggie Grain Bowl $13.2, Chicken Caesar Salad $17.9, Turkey Avocado Wrap $19.3, Falafel Pita Pocket $16.4, Tomato Soup & Side Salad $19.4. Memoji avatars hover by selections; cart count increases. |
| 23.4–26.6 | Phone shrinks to center, chat visible, floating food emoji and small “Order!” bubbles fly around it. |
| 26.6–29.7 | Rapid app demo montage on small centered phone: Jump Jump game, Uber Driver, other app screens (native frames needed for sub-second cuts), Today’s Health, Manus “What can I do for you?”. |
| 29.7–31.7 | Rich preview card grid fills viewport and drifts. Cards include Check-in flight, Apartment in New York, DoorDash Order, Starbucks Pickup, Marriott Stay, Zoom Meeting, OpenTable Reservation, Mail, Jump Jump, Spectrum mini Apps, Coding Agent, Your spending in August, Blue Bottle order, Uber Ride. |
| 31.7–36.5 | Centered kinetic text “Now your agent can send” followed by changing icon + category: agentic apps, generative UIs, games, sign-in requests, live screen sharing, live delivery tracking, menus, dashboards, finally mini apps. Prior/future categories are faded pale gray above/below the active black line; active category scrolls vertically with blur. |
| 36.5–39.6 | Centered end CTA “Available today at tryphoton.ai”; URL light cyan-blue, rest bold black. |
| 39.6–42 | Black Photon logo mark and wordmark centered on white, hold to end. |

## Reproduction accuracy gates

1. Keep natural 1920×1080 / 30 fps and frame count 1260; avoid extending video to container audio duration accidentally.
2. Establish exact layout at rest using native source frames, then reproduce phone and camera transforms separately from UI state changes.
3. Use asset crops only for genuine raster contents (Memoji, food photos, real app thumbnails); rebuild editable type, bubbles, outlines, sheets and native icons where possible.
4. Validate native frame comparisons at start/mid/settle for each transition; generic screenshots or contact sheets are insufficient for a 1:1 claim.
5. This acquisition document is a shot inventory, not a fidelity certificate. The complete recreated outputs and current measured limitations are documented in `README-recreation.md` and `recreation-status.json`.
