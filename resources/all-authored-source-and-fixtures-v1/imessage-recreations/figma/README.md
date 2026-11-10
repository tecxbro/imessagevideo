# Figma Motion branch

The Figma account-discovery tool did not answer the bounded 25-second diagnostic. No file or export exists from this method. `status.json` preserves the exact limit of the evidence; the failure must not be described as proven disabled Motion or invalid authentication.

`prepare-figma.mjs` prepares native-layer/keyframe JavaScript from the same measured scene JSON used by the local renderers. It is an **unexecuted conversion prototype**, not a verified recreation. It writes a separate audit listing unsupported or uncertain features. It cannot silently remove unsupported properties.

```sh
node figma/prepare-figma.mjs --scene references/01-photonhq/scene.json --out figma/prepared/01-photonhq
```

After the connector responds, first resolve the user's plan, create or select the authorized Design file, create a session, inspect it, and probe `figma.motion.figmaAnimationStyles()` with a read-only `use_figma` call. On a `not a supported API` error, stop the Motion branch once. Do not repeatedly try unsupported API names.

Read `figma-use`, `figma-generate-design`, and `figma-use-motion` before submitting the generated code. Pass their names through `skillNames`; pass the created session UUID. The generated script is deliberately not auto-submitted. It creates new native editable rectangles, ellipses, text, vector paths, image layers and frame containers, and returns every created node ID. A scene with an audit blocker must be fixed before submission.

Animation values are in seconds. Translation keyframes subtract the resting x/y position because Figma translation is additive. Source clockwise rotation is negated for Figma's counterclockwise rotation convention. Layer lifetime becomes a HOLD opacity envelope. Transform pivots require visual validation: the conversion uses a one-pixel unclipped wrapper whose center represents the declared SVG origin. This behavior is unverified in the current session and is a warning in every preparation audit.

Exact font styles must be present in `figma.listAvailableFontsAsync()`; generated code fails if it cannot resolve a declared family/weight. It must not silently swap to an arbitrary font. Browser-embedded local fonts do not automatically become Figma fonts.

Start with a low-resolution, low-fps diagnostic export of a top-level timeline frame. Sample start, transition, and settled frames against the reference, diagnose all visible differences, fix them, then export the full-size final. A resting screenshot cannot validate motion. An editable script or a successful write does not certify 1:1 rendering.
