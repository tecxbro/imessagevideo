# Director workflow: brief to an evidence-backed shot plan

## Select the task mode first

1. **Exact reference recreation:** The supplied movie determines composition and timing. Catalogue recipes help decompose it; they do not replace measured source motion. Read the reconstruction playbook and source-frame evidence.
2. **New video in the studied visual language:** Select a small number of motifs by story purpose, then adapt copy, components, layout, timing and sound to a new product. Label the result as newly directed work.
3. **Component extraction/port:** Establish the editable boundary, asset dependencies and source-to-target design tokens. A static screenshot cannot become an editable design merely by being placed in a frame.

The explainable `decisions.mjs` keyword router is a navigation aid. It returns matched terms, suggested motifs and risks. It is not an aesthetic evaluator or an LLM running inside the HTML explorer. The agent still directs the film.

## Turn a prompt into decisions

Extract product, audience, promise, real user action, evidence of success, required copy, runtime, aspect ratio, brand constraints and available assets. Read supplied or connected context before requesting anything missing. Make reversible defaults when reasonable; do not invent product capabilities, transactions or unsupported UI states.

Choose one main promise, then a causal arc. For example, a dinner assistant can be: typed request → send → useful options → mini-app reservation action → confirmation. A message wall is appropriate if scale is the promise; it may distract when one reservation is the story. A morph is earned when identity changes context; it is not a mandatory transition between every shot.

Open at least the chosen source/rebuild filmstrip, its recipe metadata and the relevant component anatomy. Record which frame files were inspected. Explain the chosen motif in terms of audience understanding, then name the strongest rejected alternative and its tradeoff. Keep this rationale short and concrete.

Write a shot plan before generating production frames. The plan contains:

- Beat goal and exact copy.
- Component instances and stable IDs, with editable/raster boundaries.
- Start/end state and intended attention target.
- Native-frame phase boundaries, parent/camera motion, clipping and reading holds.
- Sound anchors for genuine UI actions, with music optional.
- Chosen measured study or explicitly authored starter; unsupported assumptions and asset gaps.
- Validation gate: the visible evidence that would establish success.

Use `brief-schema.json` and `examples/dinner-shot-plan.json` as a structured starting point. The example is new choreography, not a claim about the source videos.

## Work through three reviews

**Design review:** Check a few stills at delivered size. Verify copy/line wrapping, optical alignment, component scale, tails/radii, matte, asset identity and action legibility. Do not fix a camera/layout error by polishing a misplaced image.

**Motion review:** Check start, anticipation, action, arrival, settle, hold and transition. Inspect every native frame numerically for an exact recreation, then review separated error peaks and foreground differences. Do not infer whole-sequence accuracy from six attractive stills. Confirm transformed children/parent camera stay coherent and the same actor survives the transition.

**Sound review:** Start with UI only. Type only for observed human input; do not sound title reveals, AI response text or caret blinks. Keep actual pauses and silence. Check attack/onset alignment and codec headroom, then add quiet optional music.

For each failure log the observed defect, evidence, cause or bounded hypothesis, changed variable and next check. Retain successful artifacts and scoped outside-range proofs. Numerical metrics diagnose differences, not a percentage of perfection.

## Deliver something an agent can reuse

Deliver the shot plan, scene JSON, component configuration, source/asset provenance, sound cues, native-frame analysis, accepted renders and visual comparison. The standalone explorer exports a starter scene that the existing Remotion/GSAP/HTML/Pillow/Motion Canvas adapters can consume. Figma export/editability remains subject to an actual tested Figma capability; the previous session did not validate its Motion API. Never promise automatic Figma output from this HTML viewer.

Frame-analysis data and atlas files must state their scope. Existing six-film CSVs cover7,499 native aligned output frames. The small atlas shows selected instructional phases, not every video frame. Per-frame scene trajectories describe evaluated scene states; only source/candidate pixel comparison measures their visual agreement.
