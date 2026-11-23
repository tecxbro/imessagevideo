# What this skill contains

Start with `../SKILL.md`. The previous version was primarily a measured reconstruction manual, shared scene schema, real renderers, verification scripts and detailed failure/audio evidence. The upgrade preserves those files and adds a visual design/director layer.

| Layer | Actual files | What an agent learns or can do |
|---|---|---|
| Entry and task routing | `../SKILL.md` | Choose exact-reference, original-direction or component-port workflow |
| Director judgment | `directing.md`, `decisions.mjs`, `brief-schema.json`, example shot plan | Select a motif by purpose, compare tradeoffs, plan causal beats and validation |
| Design grammar | `design-grammar.md` | Attention hierarchy, typography, actor identity, camera, clipping, material and reading holds |
| Measured source studies | `catalogue.json`, `source-studies/*.json` | 14 studies with exact frames, actual canonical IDs/literal keys, anatomy, choose/avoid rules, sound hooks and caveats |
| Visual evidence | `atlas/*.jpg` | 84 paired source/rebuild teaching frames, six phases per study; images must actually be opened |
| Components | `components.mjs`, `component-contracts.md`, `visuals/component-anatomy.png` | Nine editable neutral builders with parameter APIs and explicit asset boundaries |
| Motion code | `motions.mjs`, `examples/scenes/*.json` | Nine new adaptable starters, using the same scene format as production renderers |
| Exposed UI | `index.html` | Offline play/pause, native-frame scrubbing, duration/copy/color edits, routing suggestions, scene/cue/SVG export and source filmstrips |
| Frame analysis | `analysis/*/frames.csv`, `scan.json`, `analysis/index.json` | Historical native-pixel comparison of all7,499 aligned output frames, including residual error and source mapping |
| Existing rendering and sound | `../scripts/`, `../references/ui-audio/` | Real Remotion/GSAP/HTML/Pillow/Motion Canvas adapters, comparison utilities and UI-first audio workflow/source/licenses |
| Validation and process | `test_toolkit.mjs`, `validation.json`, `upgrade-steps.md` | Reusable behavioral checks and the observed failures/corrections of this upgrade |

## Use it without code

Extract the whole skill folder, then double-click `director/index.html`. The built file contains its own script, style and catalogue; images remain relative beside it. It does not fetch an AI service, depend on a web server or autoplay. A hosted copy can be linked from the public motion gallery.

Choose a starter, scrub the timeline, change the exposed fields and inspect the related source/rebuild filmstrips. Open the component anatomy board and measured JSON for deeper detail. Export a scene to render with an actual engine. Brief suggestions follow an explicit word-matching rubric; the director/agent supplies the judgment.

## Use it from code

```bash
node director/cli.mjs list
node director/cli.mjs plan --brief "Show a booking mini app inside a conversation"
node director/cli.mjs scene --motif mini-app-expand --out work/scene.json
node director/cli.mjs frames --motif identity-morph --out work/svg-frames
node --test director/test_toolkit.mjs
```

See component-contracts.md and ../RUNNING.md before video rendering. The visual viewer does not automatically assemble the full shot plan, export video, mix sound or build an editable Figma file.

## Concrete interpretation examples

Photon's message field is taught as ordered independent actors plus parent camera/channel handoffs, not “fly some messages in.” Linq's embedded app separates the host context, a clipped document and a horizontally moving fare rail. Poke's source64–80 changes rounded surface geometry, material and a palm-tree mark, with a separate badge and square handoff81; a generic border-radius tween is insufficient.

For each study the literal frame/key data is reference evidence. Neutral component dimensions and starter curves are new authoring defaults. Replacing text inside a source outline or a bitmap card is new component/artwork work; it is not a free parameter already exposed by that measured source. Original movies, original full canonical scenes/assets, generated audio and proprietary fonts remain in the main project or separate delivery archives.

## Verification scope

The38 toolkit contracts cover108 motif/fps/duration combinations and22,680 evaluated starter frames, including Unicode drafts, empty sends, batched visible typing, causal cue targets, component/camera identity and deterministic exports. Fourteen atlases were extracted by integer native frame selection and their source/accepted movie hashes match the historical scan evidence. Native CSV row counts sum to7,499.

Visual inspection of selected atlas and analytical SVG raster images is separate from browser QA. The managed Sites preview requires the CUA route; that route was unavailable in this session, so no interactive browser result is claimed. Static compiled-script/link checks, geometry/causality tests, package hashes and public byte delivery checks are separate evidence.
