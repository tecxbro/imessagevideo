# Attachment surfaces in motion

Reviewed November 18, 2026. Use the motion and ownership cues below to identify which surface a shot needs. The original project media paths resolve after `python3 tools/sync_library.py`. [Production source index](../../../FINAL-PRODUCTION.md)

| Surface | What moves | What stays put | How to build it |
| --- | --- | --- | --- |
| Restaurant photo strip | The thumbnails translate left together as different pictures enter the viewport. | The venue title, actions, tabs, and address stay registered during the photo movement. | Give the venue document a fixed photo viewport. Put each editable image inside one translating rail and clip both the rail and the image corners. |
| Native media message | Photos overlap in a collage or share the footprint of a stack. In the observed stack swipe, the front photo changes in place. | The media message keeps its position and the surrounding thread does not reflow during the swipe. | Give the attachment bundle one transcript row. Keep the individual images, their order, and any browsing state inside the bundle. |
| iMessage app card | A compact preview is already visible in the thread. A separate rounded app panel emerges and its body can scroll. | The preview remains in the thread behind the panel during the opening. | Keep preview, conversation, and sheet under the same phone camera. Give the sheet its own clip and keep app readiness and document scroll independent of sheet position. |

## Linq launch footage

The archived original is H.264 at 960 × 720, 30 fps, 1,458 frames, 48.6 seconds, starting at zero. SHA-256 `86e22e698e141c5c2a161977289be1335bb0c0a1dd98769c4c146fcd57bbf2eb`. Frame numbers below are zero-based presentation indices. The film presents edited UI compositions. The exact device, iOS build, and finger contact are unknown. [Original file](../../../projects/05-linq-complete-v1/imessage-recreations/references/05-linq/source.mp4) · [Creator's post](https://www.linkedin.com/posts/elliottpotter_your-users-never-have-to-leave-imessage-again-activity-7477784121293950976-Dlap)

**Restaurant strip.** At frame 1080 (36.00 s), the Boqueria Soho view shows the façade and part of the table photo. By 1095 (36.50 s), the façade is cropped at the left and a food photo is entering at the right. At 1104 (36.80 s), the overhead dish fills most of the viewport. At 1108 (36.93 s), the plated dish is centered and the interior peeks in. At 1112 (37.07 s), the interior is moving in. At 1130 and 1134 (37.67–37.80 s), the last interior is framed close to the right edge and the rail has settled to the precision of this inspection. The Directions button briefly changes shade at 1130 after the main rail travel. Leftward travel is visible. The film does not show the gesture, the release, or a physical touch indicator.

**App card.** At frames 350 and 354 (11.67–11.80 s), the compact flight preview has a bridge photo, a title, and a details affordance. At 355 (11.83 s), the low, translucent Flight Details panel first appears in the inspected sample, with the preview visible behind it. By 359 (11.97 s), the panel is blue and legible and the chat behind it is soft. It settles higher with a visible grabber at 363 and 366 (12.10–12.20 s). By frame 390 (13.00 s), the fare content has advanced within the foreground region. The label suggests a tap to open. A finger or tap marker is not visible in this opening.

For another anchored preview, Photon Mini Apps frames 545–555 (18.17–18.50 s) show an Uber Eats card growing beneath the reply in the Team Lunch thread. The card is readable at 600 (20.00 s), its face darkens at 607 (20.23 s), and it is bright again by 614 (20.47 s). This supplies a card-local press cue. The app action and camera movement are separate timing tracks when adapting it. [Original file](../../../projects/03-photon-mini-complete-v1/imessage-recreations/references/03-photon-mini/source.mp4) · [Creator's post](https://x.com/daniel_tian1/status/2067327329161064688)

## Native media grouping

Apple's WWDC21 footage shows a notched iPhone in the iOS 15 preview. The gesture is filmed on a phone held in hand. Exact model and OS build are unknown. Times use the Apple Developer player timeline.

| Player time | Visible evidence |
| --- | --- |
| 13:43.42 | Three photos overlap vertically in different positions in one incoming collage. A save affordance sits alongside it. |
| 13:46.73 | A different incoming message is labeled **10 Photos**. One large photo faces forward, with rounded back cards peeking out at the right. The count and save affordance are outside the image. |
| 13:49.20–13:50.50 | On the phone in hand, the finger crosses the face of the in-thread stack leftward relative to the screen. The front image changes while nearby messages remain in place. |
| 13:51.00–13:51.93 | The finger contacts near the upper-left edge of the stack and a two-column photo grid opens. The fingertip partly occludes the control during contact. |

[Apple WWDC21 keynote](https://developer.apple.com/videos/play/wwdc2021/101/?time=823) · [Apple iOS 15 feature notes](https://www.apple.com/jo/ios/ios-15-preview/features/#messages)

Apple's iOS 27 iPhone guide documents 2–3 media items received together as a collage and 4+ as a stack. Its browsing instructions describe tapping to open and swiping through the stack. The older keynote also demonstrates a swipe directly in the thread. Treat these as versioned behavior. A four-item send, arrival timing, exact four-item geometry, and the device/build for a controlled three-versus-four trial remain unmeasured here. [Apple iPhone User Guide for iOS 27](https://support.apple.com/guide/iphone/share-content-iphb66cfeaad/27/ios/27)

Keiki's **Rich cards** renders slides to PNGs and groups them into one media message. The docs specify a swipeable stack at four or more cards on iMessage. Keiki's **iMessage Apps** delivers an app card that opens an HTTPS page through the Keiki Vault extension or a configured customer extension. The Linq motion illustrates the preview-to-sheet composition; Keiki's documentation establishes the product behavior. [Keiki Rich cards](https://onkeiki.com/docs/cards#channel-behavior) · [Keiki iMessage Apps](https://onkeiki.com/docs/imessage-apps#what-the-recipient-sees)

The separate iMessage demo project's measured sheet study calls out host reflow before opening, a content readiness transition, compact content during collapse, composer restoration, and continued dismissal. Treat these as distinct events when authoring a sheet shot. The documented blank/loading frames belong to that capture. [Sheet-motion skill](https://github.com/tecxbro/imessagedemo/blob/main/.agents/skills/recreate-imessage-sheet-motion/SKILL.md)

## Inspection coverage

- Linq decoded 1,458 frames. Inspected 18 half-size full-frame samples at 350, 354, 355, 357, 359, 363, 366, 390, 1080, 1090, 1095, 1100, 1104, 1108, 1112, 1120, 1130, and 1134.
- Photon Mini Apps decoded 1,260 frames. Inspected eight quarter-size full-frame samples at 545, 548, 551, 555, 566, 600, 607, and 614. Original SHA-256 `886405a53b2ce053749c17cb37b3f4870f09db0c6079dbcf3b3ffa9dbba859c9`.
- WWDC21 decoded 720 frames from Apple HLS segments 137–140 in the 1080p AVC rendition at 30000/1001 fps (24.024 seconds starting at player time 816.816 s). Inspected 24 overview tiles sampled at 1 fps and 14 detailed crops at clip-relative frame indices 198, 297, 357, 365, 371, 378, 386, 396, 410, 425, 440, 453, 460, and 469. The concatenated init and four source segments have SHA-256 `e94216725a70218e27fab7f4acf255b684fd8fba4acc5474ef669daeaea421de`.
- Six contact sheets were exported to temporary inspection storage. These checks cover sampled picture states only. Audio and exact transition curves were outside the scope.
