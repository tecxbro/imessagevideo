# Component kit and editable boundaries

`components.mjs` provides nine neutral, parameterized builders: MessageBubble, Composer, AppIcon, AppCard, BottomSheet, PhoneFrame, ActionButton, Avatar and CameraRig. Each returns ordinary scene-contract layers with stable child IDs. `motions.mjs` composes them into nine editable starter studies. It is runnable code, not pseudocode.

The source studies are a separate layer of evidence. They point into frozen measured scenes in the full project. Some measured motion is sampled native poses or shutter/material layers rather than a clean reusable function. The source scene and static rich-card imagery are not all embedded in this compact skill. A portable starter uses fresh generic artwork; substituting a brand logo, measured palm path, face or card screenshot requires the original asset and provenance.

## Practical API

```js
import {MessageBubble, Composer, CameraRig} from './components.mjs';
const bubble = MessageBubble({
  id: 'request', x: 140, y: 260, width: 272, height: 72,
  side: 'outgoing', copy: 'A table for two?', fill: '#1688fa'
});
bubble.keyframes = {
  y: [{t: 0, value: 340}, {t: .3, value: 260, ease: 'easeOut'}],
  opacity: [{t: 0, value: 0}, {t: .1, value: 1}]
};
const camera = CameraRig({id: 'camera', children: [bubble],
  keyframes: {scaleX: [{t:0,value:1},{t:1,value:1.1}],
              scaleY: [{t:0,value:1},{t:1,value:1.1}]}});
```

Text is editable; sizing is explicit. The kit does not measure arbitrary fonts or auto-fit every string. Supply suitable manual line breaks, measure production copy, and resize the component when needed. Text overflow is a design error, not a reason to silently shrink all typography. Keep clip bounds and parent transforms explicit.

## State transitions

Composer input, send button, message body and reply are different actors. Preserve their causal boundaries. An outgoing message is not an independent duplicate of input left behind. UI typing in a newly authored starter is permitted because that starter actually creates human input states; it is not evidence for extra typing in a source film.

AppCard separates surface, artwork, heading, detail and action child IDs. BottomSheet owns its clip. PhoneFrame clips screen content under the chrome. CameraRig moves the parent without rewriting local UI geometry. Identity morphs keep surface, internal mark and material tracks separate; exact Poke needs measured palm-tree silhouette states.

The neutral Avatar uses initials. The neutral PhoneFrame is a conversation viewport, not an exact iPhone hardware model. AppCard artwork is a simple editable color field. Source photographs, hardware reflections, maps and image-based card interiors have separate asset contracts and are not magically reproduced by these builders.

## Moving conversations

Import the conversation builder and standalone media surfaces from [`conversation.mjs`](conversation.mjs). They return layers in the existing scene contract. Use [Lantern](ui-trial/demo.mjs) for a reflow, send, scroll and camera test, and [Ferry lunch](ui-trial/fresh/README.md) for a full assembly with local images.

```js
import {buildConversation, PhotoStrip, NativePhotoCollage,
  NativeAttachmentStack, InlineAppCard} from './conversation.mjs';

const context = document.createElement('canvas').getContext('2d');
const {scene, events} = buildConversation({
  id: 'reservations',
  duration: 6,
  phone: {width: 320, height: 500},
  participant: {name: 'Nora Reyes', initials: 'NR'},
  messages: [
    {id: 'welcome', side: 'incoming', text: 'The evening workshop still has seats.'},
    {id: 'request', side: 'outgoing', text: 'Could you hold two by the window? ✨',
      typingFrom: 0.6, at: 2.6, reaction: {at: 3.1, type: 'heart'}},
    {id: 'reply', side: 'incoming', text: 'You’re all set for seven.', at: 3.8},
  ],
  measureText(value, {fontFamily, fontSize, fontWeight}) {
    context.font = `${fontWeight} ${fontSize}px ${fontFamily}`;
    return context.measureText(value).width;
  },
});
```

- **People and layout.** `participant.avatar` takes a local image path relative to the generated scene. The header uses supplied initials or derives them from the name. The measurer must use the export font, including emoji fallbacks. Wait for any custom fonts before measuring. The [Node build helper](ui-trial/measure-text.mjs) uses installed fonts in Chromium. It accepts the same JSON-safe options and supplies the measurer.
- **Message clock.** `at` defaults to zero for existing messages. `typingFrom` starts an outgoing draft and `at` sends it. Use unique simple IDs, `side` of `incoming` or `outgoing`, and text, an attachment or both. An optional `edit: {at, text}` changes a row after arrival. The composer shows the latest two measured lines, types complete graphemes, and clears on the first native frame at or after the send time. Incoming messages arrive whole. Events are visible action hooks for cue review.
- **Ownership.** The `<message-id>-tapback` stays under `<message-id>`. The screen clips the phone, and the transcript viewport clips the scroll group. Use `scroll: [{at, offset, duration}]` for choreography. A positive pixel offset moves toward older content from the latest scroll position and clamps to the available transcript. `camera: {x, y, originX, originY, keyframes}` takes scene-contract keyframes in output seconds and moves the whole phone. Composer, transcript and camera retain independent controls.
- **Check motion.** Inspect consecutive decoded frames around a wrap, send and scroll while the camera acts. A single frame can miss a stale draft or a reaction that slips during reflow. See [the evidence](ui-trial/ATTACHMENT-EVIDENCE.md) and [the regression](ui-trial/test-conversation.mjs).

| Attachment `kind` | Builder | Editable inputs |
| --- | --- | --- |
| `photo-strip` | `PhotoStrip` | `images: [{src}]`, `swipes: [{at, duration}]`, optional `width` and `height`. Only its clipped horizontal rail moves. It can sit in a venue document or a message row. |
| `native-collage` | `NativePhotoCollage` | Two or three `images` in a grouped preview. |
| `native-stack` | `NativeAttachmentStack` | Four or more `images` in a grouped preview, optional authored `swipes`. The inline motion is illustrative. Apple's documented interaction opens the stack before swiping. |
| `app-card` | `InlineAppCard` | `title`, optional `detail`, `action`, `image: {src}`, `width` and `height`. The inline preview stays on its message. Use a separate bottom-origin sheet timeline when showing an open app. |

Put local artwork paths in the generated scene's coordinate system for file resolution. HTML/SVG and GSAP use the same scene and asset paths. A conversation includes an illustrative phone shell and authored timing. For a matched recreation, establish the actual host, device, OS, gesture and frame evidence separately.

## Render and adapt

```bash
node director/cli.mjs list
node director/cli.mjs plan --brief "Show booking inside a conversation"
node director/cli.mjs scene --motif mini-app-expand --out work/scene.json
node scripts/engines/render.mjs --method gsap --scene work/scene.json --out work/preview.mp4
```

Rendering uses the existing real engines and installed dependencies, not the explorer's playback timer. The offline HTML preview evaluates the same frame-indexed scene SVG for inspection. Its playback timer can drop presentation frames; exported video rendering evaluates each native frame deterministically. The explorer exports source scene and cue JSON, not a pre-rendered final film or an editable Figma file.

Exported event files are target-layer cue hooks for an authored starter. Before using the production audio renderer, normalize them into its canonical film schedule with film ID, actual frame count, rational fps, sample count and final visible-event evidence. The explorer does not mix or generate audio itself.
