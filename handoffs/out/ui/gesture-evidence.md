# Gesture & behavior evidence — verified for the catalog agent

Frame numbers = source frames (linq/danieltian/gallery/photon 30 fps; poke 30000/1001).
Full citations: `work/ui/behavior-evidence.md`, `work/ui/attachments-evidence.md`.
Crops/sheets: `work/ui/frames/`.

## Verified (motion, multiple frames or measured scene data)

| Behavior | Evidence | Usable for |
|---|---|---|
| Tapback badge is glued to its message through scroll; your reaction lands on an incoming bubble's top-right corner | `05-linq` f722-728 pop-in (~0.25s spring), f750 anatomy, f758-765 rides scroll with Cash card; `04-poke` f384-392, f410-430 | `tapback` param on `MessageBubble`/`AppCard`; pop-in = scale keyframes on badge group |
| Draft→send: placeholder+mic die together on first typed char; send circle appears inside field right end and fills #c2d2fd→#70a3ff→#007efe over ~3f; after send field returns to placeholder+mic, bubble appends + thread scrolls, "Delivered"→"Read" under last outgoing | `05-linq` scene `v19-intro-composer` timed layers (t=0.767/0.800-0.900); linq f145-175; `04-poke` f384 | `Composer(typed,typeStart,sendT)` + appended `MessageBubble` at `sendT`; `DeliveryStatus` |
| Phone-space vs world-space: screen content rigidly attached to hardware through camera transforms; titles/emoji props stay world-space | `06-gallery` f330-480; `04-poke` scene `v15-selected-card-camera`, hardware+screenmask split | `DeviceFrame` clipped `-screen` group + `CameraRig` on the outer group only |
| App card = rounded surface + app-icon badge overlapping top-left corner + content + caption CTA; tap morphs card surface into fullscreen app panel (not push nav) | `05-linq` f136-180 (GamePigeon chess), f350-410 (Flight Details), f585-690 (Jewelry+Add to Bag), f765-820 (Cash pay sheet); `04-poke` poll/restaurant cards | `AppCard` + paired expand panel (scale/fade on same surface) |
| Card content clips to card bounds: photo strip translates X under fixed chrome | `05-linq` f1050-1150 (≈f1091-1111), `linq-strip-sheet.png` | `PhotoStrip` inside clip; chrome as siblings |
| Typing indicator: gray pill, 3 sequential-bounce dots, incoming position (rides avatar in group) | `01-danieltian` ~f185-230; `03-photon-mini` | `TypingIndicator` |
| Composer `+` opens iOS17 app list (Photos, Apple Cash, Polls, Store → scroll → Games grid) replacing keyboard area | `05-linq` f95-135, `linq-send-sheet.png` | `AppDrawer` |
| Tail on last bubble of a same-side run only; card can carry the tail; radius ≈ fontSize×1.05-1.15, not h/2 | `05-linq` f750 pixel scan: outgoing body w356 h120 r~38 tail drop ~14px @ x830-847; incoming w384 h66 r~31 | `MessageBubble tail`, `AppCard tail` |
| Group chat: sender avatar at bubble-left + gray name above bubble | `06-gallery` f60-200 "Cabin trip"; `01-danieltian` f950+ agent names | `senderName`/`senderAvatar` |
| Voice message: play circle + ~44 white bars (w4-5, r2-2.5, h18-72) + duration + transcript | `04-poke` `p0310-wave-*` | `VoiceMessage` |

## Inferred or gapped (honest)

- Other-party tapback side (top-left mirror): **inferred** — no other-party reaction on film.
- Tapback retention over multi-screen scroll: **unverified** — observed scroll ≈1 bubble height before exit.
- Draft→send mid-flight bubble: **cut in every film** — no frames of the bubble leaving the field.
- Onkeiki "4+ cards = swipeable stack": **unverified** in this library — only the card-internal carousel exists on film.
- Onkeiki group-delivery restriction: contradicted by authored film framing (group threads carry cards) but is a transport-layer claim — do not overrule.
- Typing-dot timing: cadence stylized, not sampled.
