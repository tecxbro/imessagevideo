# Attachment and conversation motion evidence

Reviewed 2026-11-18. Frame numbers are zero-based decoded frames from the original clips. I surveyed the six originals at one-second intervals, then decoded individual checkpoints for the shots below. The repository's [production index](../../../../FINAL-PRODUCTION.md) identifies the full source clips and accepted projects.

| Surface | What the evidence shows | Implication for editable motion |
| --- | --- | --- |
| Restaurant photo strip | [Linq original](../../../../projects/05-linq-complete-v1/imessage-recreations/references/05-linq/source.mp4), 960 × 720 at 30 fps. At n1090–1111 (36.33–37.03 s), the Boqueria Soho façade and table photos give way to overhead food, a plated dish and an interior. Title, tabs and address stay in place. The interior approaches its settled pose at n1126–1134 (37.53–37.80 s). | Move one horizontal image rail inside an app-local viewport. Fix the heading, actions, tabs, address and viewport to the venue document. The launch edit shows leftward image travel. Finger contact, precise release, device model and OS are unknown. |
| Native attachment collage or stack | Apple's iPhone guide describes 2–3 photos or videos received together as a collage and 4+ as a stack. It describes tapping to open the stack and then swiping. Keiki delivers rendered rich-card PNGs together as one media message and documents the 4+ stack threshold on iMessage. [Apple Messages user guide](https://support.apple.com/guide/iphone/share-content-iphb66cfeaad/ios), [Keiki rich cards](https://onkeiki.com/docs/cards#channel-behavior). | Own the group on the conversation row. Keep each image editable within the group. The authored collage layout, stack overlap and motion timing are visual approximations. The sources reviewed did not establish a matched three/four-image capture, the actual device/OS, or the visible input sequence for either count. The count rule and tap/swipe path are documented behavior. Native inline paging, arrival timing and measured geometry remain unverified. |
| App card and sheet | [Photon Mini Apps original](../../../../projects/03-photon-mini-complete-v1/imessage-recreations/references/03-photon-mini/source.mp4), 1920 × 1080 at 30 fps. Mail preview at n200, darker pressed-looking card at n205, white composing sheet partway up over the chat at n218, near the top at n225, chat visible again at n359, “Sent.” by n363. Model, OS and exact touch are unknown. Keiki documents HTTPS content opening via its Messages extension. [Keiki iMessage apps](https://onkeiki.com/docs/imessage-apps#what-the-recipient-sees). | Keep the inline preview attached to the row. Move the sheet and clip its content in the phone's coordinate space. Preserve the original thread and its composer so they can return when the sheet leaves. The Mail shot contains app-specific controls and timing. |

The [separate iMessage sheet-motion skill](https://github.com/tecxbro/imessagedemo/blob/main/.agents/skills/recreate-imessage-sheet-motion/SKILL.md) describes a different recorded app. Its source B at 30 fps retains expanded content at n094, shows compact content at n095, restores the composer by n102 and clears the sheet by n123 while the transcript continues. Preserve independent host reflow, sheet geometry and content readiness. Dismissal needs its own choreography. Exact gesture events and spring constants remain unknown.

## Motion checks for the authored conversation

- **Tapback ownership.** In the 1440 × 1080 original at 30000/1001 fps, the “want me to find a spot?” bubble is alone at n390. At n398 the blue thumbs-up overlaps its upper-right corner. At n420–430 the next row appears below. At n450 the thread rises in the viewport. At n460 the reacted bubble and reaction are cropped together. The reusable heart can use the same message-local anchoring and shared transcript clip. Its timing and glyph are authored. The Serena index catalogs this same launch film. [Poke original](../../../../projects/04-poke-complete-v1/imessage-recreations/references/04-poke/source.mp4), [Serena launch-video index](https://github.com/serenakeyitan/awesome-ai-clonable-launch-videos#poke-imessage-ai-assistant).
- **Send state and camera.** In the 1920 × 1080 original at 30 fps, the two-line draft is visible at n148–172. At n177 the field text has cleared as the outgoing bubble appears. The phone moves into frame at n184 and the bubble sits inside its bezel at n193. In the authored fixture, frame both composer and transcript through the send, then check the row again during camera and thread movement. [Photon Agent to Agent original](../../../../projects/02-danieltian-complete-v1/imessage-recreations/references/02-danieltian/source.mp4).

To regenerate the Linq and Photon Mail checkpoints from the checkout root:

```sh
ffmpeg -i projects/05-linq-complete-v1/imessage-recreations/references/05-linq/source.mp4 \
  -vf "select='eq(n,1090)+eq(n,1100)+eq(n,1111)+eq(n,1134)',scale=480:-2,tile=2x2" \
  -frames:v 1 /tmp/imessage-linq-rail.jpg
ffmpeg -i projects/03-photon-mini-complete-v1/imessage-recreations/references/03-photon-mini/source.mp4 \
  -vf "select='eq(n,200)+eq(n,218)+eq(n,225)+eq(n,363)',scale=480:-2,tile=2x2" \
  -frames:v 1 /tmp/imessage-photon-mail.jpg
```
