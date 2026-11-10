A consistent Canvas kerning policy removes the two measured subtitle-width differences in this bounded probe. Production files are unchanged.

At exact Poke frames 932 and 958, `fontKerning = "normal"` makes the two subtitle runs and their Email/Calendar headers pixel-identical to the SVG reference. `auto` reproduces the current subtitle error: about 3.31 local pixels of extra advance, becoming the observed 3–4 screen pixels. `none` is worse. The matching headers remain unchanged.

SVG and Canvas both report `fontKerning: auto` and `textRendering: auto`, but their default shaping differs here. The probe holds `textRendering` at auto and changes only kerning. Font family, size, weight, letter spacing, RMS shaping, and actual transforms are recorded in `probe.json`.

| Frame | Auto MAE | Normal MAE | None MAE |
|---|---:|---:|---:|
|932|.494721|0|.514377|
|958|.498793|0|.516179|

This is a causal result for two actual poses and two copy runs, with headers as controls. It does not certify a global policy. No scene, renderer, video, or native cache was edited.
