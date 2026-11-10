# Poke Apple Messages launch — source analysis

Acquired original official highest-resolution MP4. Video is 1440×1080, 30000/1001 fps (29.970...), 42.809 s. Audio about 42.859 s. Entire video is motion/UI graphics; no live-action segment to omit.

## Visual system

- White 4:3 composition, Apple Messages mock interface and polished black/silver iPhone. Dominant UI type is Apple/SF-like sans serif (font identity unconfirmed from pixels). End wordmark “Poke.com” uses a black display serif.
- Poke avatar is a textured navy rounded-square icon with white palm tree, blue sky/pale sand texture. Initial icon starts circular and morphs to rounded square. Gray verification badge beside “Poke”. Two Memoji contacts Braden and Sydney flank it and fade during camera push.
- Incoming Messages bubbles are pale gray, black type, rounded corners with left tail. Rich app lists use blue accent, thin neutral dividers, gray secondary captions, white sheets and a gray scrim. Outgoing selected cards use right tails. App icons at end are colored and varied, not interchangeable placeholders.
- Camera pushes into individual bubbles/sheets, pulls back to device, and isolates content on whitespace. UI transitions include spring-like settling rather than simple crossfades alone.

## Timeline evidence

Diagnostic sheets sample at 1 fps (labels are sampling indices, not frame-accurate event boundaries). All ranges below are provisional until refined around cuts at native fps. `scene-cuts.json` supplies automatic candidates only.

| Approx seconds | Observed motion / content |
|---|---|
| 0–0.7 | Favorites row Braden, Poke, Sydney emerges from white. |
| 0.7–3.5 | Camera pushes into Poke; icon morphs circle to rounded square, white palm redraws, verification badge appears; surrounding row and inbox fade. |
| 3.5–4.5 | Pull back to iPhone Messages inbox, Poke favorite has gray bubble “sarah wants to grab dinner tmrw”. |
| 4.5–5.9 | Push into isolated message “sarah wants to grab dinner tmrw”; “dinner tmrw” underlined. |
| 5.9–8.7 | Sheet “Dinner with Sarah” / “Pick a Time” rises over dimmed background. Thursday, June 4 options 6:00 PM / 6:45 PM / 7:00 PM, info “There are 4 events scheduled, and the first one starts at 3:00 PM”, “View in Calendar...”. Friday, June 5: 7:30 PM, 10:30 PM. Saturday, June 6: 8:00 PM, 9:15 PM. Camera scrolls to Friday; 7:30 PM selected blue. |
| 8.7–10 | Chat bubbles “locked friday” then “what r u in the mood for?” |
| 10–11.9 | Large selection bubble with blue options and emoji: Mexican, Japanese, Italian, Indian, Chinese, Surprise me. Indian fades on selection. |
| 11.9–14.9 | Checked “Dinner Choice” card, selected Indian bubble, next incoming “want me to find a spot?”; blue thumbs-up reaction pops on upper right; then “where are you rn?” |
| 14.9–16.8 | Camera moves toward composer/keyboard, current location suggestion visible. |
| 16.8–18.8 | Shared Location map card arrives (Palo Alto, CA; Interaction Company marker). Then “found a few solid spots near you”. |
| 18.8–21.9 | Restaurant sheet “Anything catching your eye?” opens over scrim. Rows: Ettan (Italian / Wine · 0.03 mi), Khazana (Indian Restaurant · 0.11 mi), Zareen’s (Indian and Pakistani · 0.16 mi), Darbar (South Indian · 0.28 mi). Third row selected with blue check. |
| 21.9–23.6 | Sheet closes. Gray checked line “anything catching your eye?” then right-tailed Zareen’s selection card “I’ll take it from here.” |
| 23.6–26.7 | Pull back to phone. Map rich card Zareen’s / maps.apple.com arrives, then “only 0.16 mi away from you”. |
| 26.7–28.9 | Push into outgoing gray audio message: play circle, waveform, 0:04, transcript “Please remind me about this dinner 1 hour before.” Then incoming “sure, i’ll remind you on time”. |
| 28.9–35.5 | Transition to floating vertically scrolling feature bubbles: Email — “Send, reply, and forward messages”; Calendar — “View, create, and reschedule events”; Reminders — “Schedule one-time reminders”; Automations — “Create and manage automations”; Image Search & Generation — “Find images and generate new ones”; Web Search & Browse — “Look things up and visit websites”. Blue textured rounded-square white-line icons at right. |
| 35.5–37.7 | Connection bubbles appear: Connect Gmail / gmail.com, Connect Notion / notion.so, Connect Todoist / todoist.com; then “connect all your favorite tools”. |
| 37.7–40.6 | Colored service icon grid expands/drifts, fills composition. Visible logos: Sonos, GitHub, Asana, Strava, Webflow, Canva, Todoist, Notion, Gmail, Linear, Google Calendar, Outlook and others. |
| 40.6–42.8 | Clean hard transition to centered black serif “Poke.com” on white, holds. |

## Reproduction accuracy gates

- Preserve original 4:3 aspect ratio and fractional 29.97 fps; 30fps without explicit time handling can shift endpoint alignment.
- Rebuild editable type, bubbles, menu rows, input controls, waveform and camera; raster crops are appropriate for textured Poke icon, Memoji, real maps/food photos, service logos only.
- Obtain native crops for every rich card and small copy before claiming exactness. Overview sheets do not establish exact sizes, positions, blur, easing or colors.
- Compare both camera framing and internal interface state frame by frame. A sequence that has the same words but different zoom, cadence or line wraps is not 1:1.
- Current analysis is an observed source inventory, not a certification of any recreated result.
