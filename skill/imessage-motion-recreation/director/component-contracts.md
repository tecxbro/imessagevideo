# Component kit and editable boundaries

`components.mjs` provides the Conversation builder and the low-level builders used by the nine original starter studies in `motions.mjs`. Each returns ordinary scene-contract layers with stable child IDs.

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

Low-level MessageBubble sizing is explicit. Supply suitable manual line breaks and measure production copy at the intended font size. Use Conversation for a thread that should reflow when copy changes.

## Compose a moving thread

```js
import { CameraRig, Conversation } from './components.mjs';

const phone = Conversation({
  id: 'studio',
  x: 285, y: 24, width: 390, height: 492,
  title: 'Zuri',
  self: 'me',
  people: [{ id: 'zuri', name: 'Zuri', initials: 'Z', fill: '#d8e6ee' }],
  messages: [
    { id: 'arrival', person: 'zuri', copy: 'Meet by the back stairs. 🎞️',
      reaction: { at: .9, emoji: '❤️' } },
    { id: 'reply', person: 'me', at: 2, send: true },
  ],
  draft: [{ at: 1.2, copy: 'On' }, { at: 1.6, copy: 'On my way' }],
  scroll: [{ at: 2.7, offset: 0 }, { at: 3.4, offset: 35 }],
});

const zoom = [{ t: 0, value: .96 }, { t: 4, value: 1.04, ease: 'easeInOut' }];
const scene = {
  width: 960, height: 540, fps: 30, duration: 4, background: '#e3e9e7',
  layers: [CameraRig({ children: [phone], keyframes: { scaleX: zoom, scaleY: zoom } })],
};
```

- Give each participant and message a unique simple ID. `person` matches a participant ID or `self`. Existing messages use `at: 0`. Messages at the same timestamp retain input order. A participant can supply name, initials, fill or profile `image: { src, alt }`.
- Copy wraps by words and then grapheme clusters. Each multiline bubble grows in height and later rows reflow. The default width estimates target the bundled fallback. Pass `measureText(copy, fontSize)` returning a width in scene pixels for production typography. Inspect the result on the render host, including emoji fallback.
- `draft` is a series of complete draft strings at output times. The visual composer shows one clipped line and follows the end of a long draft. It displays the last line of a multiline draft. `send: true` emits a local message and clears the draft on the same frame. Omit message `copy` to send the authored draft. Use a later draft key for new typing.
- A reaction belongs to a message ID. Set its own `at` on or after the parent arrival and supply an emoji. The row reserves space above the bubble and carries the reaction through transcript and camera motion.
- The transcript follows new arrivals. `scroll` adds an authored offset in local pixels, positive toward older messages. Use an explicit zero key at the desired scroll onset and again to return to the latest messages. Choose offsets that keep the intended rows in frame. The fixed header and composer share the same phone transform.
- `CameraRig` wraps the phone and carries camera tracks in stage units. Leave the transcript clip on the transcript and the outer clip on the phone screen. With multiple phones, pass unique conversation and camera IDs.

All times are output seconds. Put the full visible action and reading hold within the scene duration. The renderer samples authored events on the output frame grid.

### Choose the media surface

Use one explicit `attachment.type` per row. A row can include copy as well as media. All media options accept `width` and `height` in scene pixels. The thread caps the width to its content column. Image `src` can be a path relative to the generated scene JSON or an embedded image data URL. Keep asset provenance beside the authoring file.

| Surface | Configuration | Motion |
|---|---|---|
| Single photo | `photo-attachment` with `image: { src, alt }` and optional `fit` of `cover` or `contain` | One still photo in the row. Cover crops to fill its box. Contain preserves the full frame. |
| Native-style collage | `attachment-collage` with `images: [{ src, alt }, …]` | Fixed arrangement for two or three images |
| Native-style stack | `attachment-stack` with `images: [{ src, alt }, …]` and optional `swipes: [{ at, index, duration }]` | Each authored swipe settles on a zero-based front image |
| Photo strip | `photo-strip` with `images: [{ src, alt }, …]` and `position: [{ t, value }]` | Moves the rail in pixels inside a fixed viewport. Mount PhotoStrip inside app content when recreating the restaurant reference. |
| App card | `app-card` with `title`, `detail`, `action`, `color` and optional `image: { src, alt }` | Card preview with independent artwork and action layers. Use BottomSheet separately for app presentation choreography. |

Import `PhotoAttachment`, `AttachmentCollage`, `AttachmentStack`, `PhotoStrip` and `AppCard` directly for standalone composition. The builders emit authored film layers. See [Attachment surfaces in motion](attachment-evidence.md) for footage, documented collection sizes, observed interactions and the limits of the evidence.

## Run the example

From the skill directory, with the pinned renderer dependencies installed as described in [Running](../RUNNING.md):

```bash
node director/examples/conversation-motion.mjs /tmp/blue-awning.json
node scripts/engines/render.mjs --method gsap --scene /tmp/blue-awning.json --out /tmp/blue-awning.mp4
node --test director/test_toolkit.mjs director/test_conversation_motion.mjs
```

Append `--compact` to the scene command to shorten the message above the reacted row without editing layout or timeline code. Inspect both builds around the send and the moving scroll. The regression checks reflow, reaction parenting, send-frame state, nested clips and the media actors.

## State transitions

Composer input, send button, message body and reply are different actors. Preserve their causal boundaries. An outgoing message is not an independent duplicate of input left behind. UI typing in a newly authored starter is permitted because that starter actually creates human input states; it is not evidence for extra typing in a source film.

AppCard separates surface, artwork, heading, detail and action child IDs. BottomSheet owns its clip. PhoneFrame clips screen content under the chrome. CameraRig moves the parent without rewriting local UI geometry. Identity morphs keep surface, internal mark and material tracks separate; exact Poke needs measured palm-tree silhouette states.

The neutral PhoneFrame models a conversation viewport. Avatar uses initials by default. AppCard artwork is an editable color field or a caller-supplied raster. Source photographs, hardware reflections, maps and image-based card interiors have separate asset contracts.

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
