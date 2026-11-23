# 02-danieltian reference analysis

Actual downloaded source: **1920×1080, 30/1 fps, 1360 frames, 45.333333 seconds video**. Audio and container durations are slightly longer. All inspected scenes are motion graphics, so the full video is in the requested scope.

The original MP4 and raw metadata are preserved. `contact-*.jpg` show every whole second with a timestamp and frame index. `keyframes/` holds selected full-resolution frames. `scenes.json` is an implementation handoff; its initial scene boundaries are approximate, not certified exact cuts.

## Visual breakdown

| Approximate interval | Scene | Observed content and behavior |
|---|---|---|
| 0.00–2.70s | Introducing Agent to Agent / in 🟩 iMessage 🫧 Group Chats | Two centered black lines; iMessage icon and multicolor circles inline. Font appears SF Pro/Inter-like sans; exact family unverified. |
| 2.70–6.10s | Message composer | Plus at left, iMessage placeholder, microphone. Types: muse, my boss wants a team offsite tmr. can u help? Blue circular send arrow right; text fills two lines; send particle burst. |
| 6.10–8.80s | Muse phone demo | Large iPhone enters vertically with Muse avatar/header; sent blue bubble and typing indicator → reply: sure. lemme bring in some friends. |
| 8.80–12.60s | Checking what I know about Photon... | Gray lines progressively reveal: 👥 9 people · 📍880 Harrison St · ❤️Loves sushi; Offsite tomorrow. What do we need?; 🏠 A place to stay; 🚗 Rides; 🍣 Food; Let me find agents who can help... |
| 12.60–14.00s | Searching the Agent Phone Book... | Search capsule center with magnifying glass; type reveal. |
| 14.00–17.30s | Phone book search | Grid of pale phone numbers fills stage, selected numbers black; branded agent capsules emerge (Lyft, Uber Eats, Airbnb, Resy). |
| 17.30–18.70s | Selected agents | Lyft, Airbnb, Resy capsules stacked below search. Plus icons animate into green checks; other phone numbers fade. |
| 18.70–20.70s | Group icon assembly | Lyft, Airbnb, Resy, green Messages orb, blue Muse M gather into compact group avatar; Team Offsite, Oct 10 label below. |
| 20.70–25.00s | Groupchat kickoff | Group header holds while gray Muse bubbles arrive and scroll: hey team, @Justina needs a Photon team offsite. Tomorrow.; @Airbnb find a place in Tahoe for 9; @Lyft 2 XL rides from 880 Harrison St, 9am tomorrow; @Resy find a sushi spot. The team loves sushi |
| 25.00–28.50s | Budget conversation | Red Resy avatar: Budget? Blue user: ~$100 per person. Yellow thumbs-up reaction bounces into place. |
| 28.50–32.70s | Airbnb card and reply | Rich link card with cabin photo and title Lake view Cabin in Tahoe Vista; How about this one?; blue Love it; gray Booked✅. |
| 32.70–34.80s | Bookings confirmed | Lyft: 2 XLs booked. Photon HQ → Airbnb in Tahoe, 9am✅. Resy: Sushi for 9, booked🍣. |
| 34.80–37.60s | Your iMessage agent now has a 📒 phone book. | Centered bold black text; final phone book icon/words reveal. |
| 37.60–41.70s | It brings … into your group chats. | Inline brand capsules rotate through Amazon, eBay, Grok Bot; settles to It brings all the agents into your group chats. |
| 41.70–45.33s | photon.codes/beta | Centered cyan URL holds. |

## Fidelity dependencies

- Typography family is not established by metadata. It resembles SF Pro/Inter; measure glyph widths and use matching licensed fonts rather than assume an exact family.
- Reuse original branded assets where obtainable, then reconstruct editable geometry and timing. Do not pass a reference video through an output container and call it a recreation.
- Full-resolution reference frames and temporal samples are needed for geometry and easing; a one-second contact sheet cannot verify spring curves or transition start frames.
- White stage and native Messages blue/gray/green imagery dominate. Rich-link photo in source 02 is an embedded graphic asset, not live action.

## Measured palette

{
  "background": "#FDFDFD",
  "background_measurement": "Most frequent RGB pixel on multiple full-resolution decoded frames",
  "black_text": "#000000",
  "font_family": "Unverified SF Pro / Inter-like sans-serif",
  "source_dimensions": [
    1920,
    1080
  ],
  "source_fps": 30,
  "message_blue_sample": "#3CA4F9",
  "message_gray_sample": "#E7E6E9",
  "measurement_note": "These are mode values from decoded compressed video, not guaranteed original design tokens."
}

## Timing refinement

Quarter-second contact sheets (`quarter-contact-*.jpg`) were inspected end-to-end. `scenes.json` now contains the refined boundaries and additional branding details; it supersedes the initial table above. Exact per-frame easing remains to be measured. The source first decoded frame is a fully composed title, followed by an intro reset within ~0.1s. Treat that artifact separately from intended reveal motion.
