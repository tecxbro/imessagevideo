# Design knowledge, with evidence

The skill is an instruction package read by an agent. It does not train model weights. Images do not silently become visual knowledge: the agent must open the selected atlas images using an available image tool before directing or porting a motion. The explorer is a local reference and editable starter viewer; it is not a Figma plugin or an AI video-generation service.

## The picture before animation

Set one dominant reading target per beat. Identify the actor (message, app icon, card or control), its parent surface, the screen viewport and the camera. Draw their hierarchy before choosing easing. A useful default is world → camera → phone → clipped screen → content → individual control. A screen mask belongs to the screen; a camera transform belongs above it. Keep required opaque backplanes separate from fading content.

Write exact copy and line breaks before fitting bubble sizes. Separate display typography from native interface typography. Measure real font glyph widths, ink bounds, baselines, leading and tracking in the intended renderer. The starters use Arial as a disclosed fallback; they do not contain Apple fonts, original portraits, brand logos or all rich-card artwork. Obtain and license production assets explicitly. A family name is not proof of a visual match.

Incoming/outgoing sides, bubble tails, internal padding, line spacing, radii, message grouping and sender/avatar relationships form a grammar. Preserve these relationships when rescaling a shot. Do not animate every primitive independently just because the renderer allows it. Grouping controls attention and establishes object identity.

## What the six references teach

**Photon:** An ensemble can communicate breadth. Individual messages need stable identity and order while their parent field and camera move. Match independent card scale and foreground/background overlap. A wall should resolve into a readable target, not become a pile of equally loud elements. Dormant legacy layers are not active motion recipes.

**Mini Apps and Linq:** The conversation establishes context; the embedded app supplies an action. Keep the relationship between host message, app surface, artwork, selected control and returned result. Avoid a large expansion that erases the evidence that the work happens inside Messages. A rasterized card interior is a declared image asset, not a fully editable component.

**Poke:** Preserve object identity across outline, material and palm-tree mark changes. Native source64–80 is a circle-to-rounded-square identity transition, followed by a static app-square handoff81. Its internal silhouette and material change too. A new generic radius tween illustrates only part of that idea; exact reconstruction needs the measured poses and compositing order.

**Rene:** Use message causality, consent and a readable result to motivate movement. An object bridge can connect a word, a graphic object and a product surface. Respect the graphic-only time map; omitting live action changes source/output frame indices. Do not invent composer typing where the reference has no typed input.

These are observations from these films, not universal claims about the brands. The catalogue binds each specific study to frames, layers, source hashes and caveats.

## Describe motion in a useful way

For each shot record:

- **Intent:** what the audience should understand and which evidence proves it.
- **Actors and hierarchy:** stable IDs, parent/clip relationships, local vs camera motion.
- **Start and end states:** position, dimensions, scale, angle, radius, material, content and selection.
- **Phases:** anticipation/input, action, arrival, settle, reading hold and transition. Record absent phases as absent.
- **Trajectory:** rational frame clock; native sampled positions/affines or a declared curve. Record pivot and anchor, overshoot, stagger and what remains fixed.
- **Occlusion and optical behavior:** masks, matte, shadow, blur support, outgoing/incoming artwork and layering.
- **Sound:** audible actions, intentional silence, source of each effect and frame anchor.
- **Evidence and limits:** source frames vs accepted render frames, measured values vs inference, editable vectors/text vs static artwork.

An example such as “messages fly in” is insufficient. Say which message arrives first, from where, relative to which parent, over which frames, what the camera does, what remains readable, and what interaction earns a sound.

## Choose a look, not only an easing preset

Easing follows the action. Direct manipulation, send motion, a camera move and a brand morph have different causal constraints. Do not add a spring or overshoot by habit. Per-frame poses in a measured source do not prove that its author used a particular spring function. SVD/affine decomposition can contain large opposing rotations without the visible card spinning; compose world transforms before interpreting those numbers as direction.

Readability depends on copy, scale and audience, so no universal fixed hold is supplied as a measured rule. A new storyboard must budget enough time to read its longest important line at the delivered size. Test the actual rendered result. Keep decorative sound/motion quieter than causal feedback.
