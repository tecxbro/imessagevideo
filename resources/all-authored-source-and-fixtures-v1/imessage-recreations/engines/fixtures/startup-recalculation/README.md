# Rejected replay hypothesis and native graph cost

This folder is diagnostic evidence, not a production renderer release. The production runtime remains a11.

Mini V17 native frame833 follows a page with5,758 authored nodes (including5,158 tiny editable material rectangles), despite its own340 active nodes having no native filter or oversized geometry. The unchanged production render eventually completed successfully; no retry was needed. One-frame pruning with the unchanged runtime produces the exact same833PNG as the ten-frame page.

An initial full-timeline-replay hypothesis was rejected after checking exact method boundaries: Renderer.run calls playback.recalculate, but this adapter calls Renderer.renderFrame, whose path is reload/reset/seek0. Removing generator apply calls matched832/833 bytes but was not promoted on an unproved performance claim.

The fixture-only node-budget-probe.mjs preserves every visual field, proves the exact active SVG at each requested time, uses the unchanged native Scene2D runtime, and records page/frame time and actual Chrome heap. It does not mutate any production cache/master/sidecar. The prototype is deliberately not installed into the production adapter.

Node limits cannot subdivide a simultaneous state: source837 alone has2,716 authored nodes and still consumes about1.04GBJS plus1.47GBembedder heap. Smaller340-node states use about143MBJS. Do not claim that byte size alone predicts native rendering cost, or that this experiment eliminates intrinsic shape-graph costs.
