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

## Render and adapt

```bash
node director/cli.mjs list
node director/cli.mjs plan --brief "Show booking inside a conversation"
node director/cli.mjs scene --motif mini-app-expand --out work/scene.json
node scripts/engines/render.mjs --method gsap --scene work/scene.json --out work/preview.mp4
```

Rendering uses the existing real engines and installed dependencies, not the explorer's playback timer. The offline HTML preview evaluates the same frame-indexed scene SVG for inspection. Its playback timer can drop presentation frames; exported video rendering evaluates each native frame deterministically. The explorer exports source scene and cue JSON, not a pre-rendered final film or an editable Figma file.

Exported event files are target-layer cue hooks for an authored starter. Before using the production audio renderer, normalize them into its canonical film schedule with film ID, actual frame count, rational fps, sample count and final visible-event evidence. The explorer does not mix or generate audio itself.
