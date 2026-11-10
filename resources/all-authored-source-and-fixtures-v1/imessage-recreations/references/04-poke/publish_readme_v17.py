"""Write concise final rebuilding/evidence documentation from completed status."""
from pathlib import Path
import json
p=Path(__file__).parent;root=p.parent.parent;d=json.loads((p/'recreation-status.json').read_text())
if d['final_scene_sha256']!='022a546e92cbfe2a759b54ed56c826dfce637ac7db41ab86b7d312496dc54aaa':raise ValueError('Not the completed final V17 status')
qa=d['qa'];parity=qa['engine_parity_summary']['global'];known='\n'.join('- '+v for v in d['known_residuals'])
text=f'''# Poke Apple Messages launch — editable reconstruction

The final rendering input is [`final-v17/scene.json`](../../outputs/04-poke/final-v17/scene.json), SHA256 `{d['final_scene_sha256']}`. The scene contains {d['actual_scene_nodes']} native editable elements, including {d['native_layer_counts']['text']} text layers. It recreates the complete 42.809433-second graphic timeline at the source's 1440×1080 dimensions, 30000/1001 fps and 1,283 frames.

Text, message bubbles, calendars, menus, sheets, controls, keyboards, waveform, clipping and camera motion are native elements. Static artwork is limited to genuine individual photos, maps, Memoji, logos/textures and masked device hardware with transparent screens. No source video or sequence of complete reference frames is an output layer. The canonical folder is self-contained; `asset-manifest.json` records all 92 referenced asset/font hashes and crop provenance files explain the genuine material assets.

## Rebuild

From `/workspace/imessage-recreations`:

```sh
node engines/render.mjs --method remotion --scene outputs/04-poke/final-v17/scene.json --out outputs/04-poke/remotion.mp4
node engines/render.mjs --method gsap --scene outputs/04-poke/final-v17/scene.json --out outputs/04-poke/gsap.mp4
python3 scripts/final_encode.py --state references/04-poke/encoding-state-v17.json --only 04-poke --methods remotion gsap
```

`build_v17.py` reproduces the canonical bytes from immutable V16 and frozen component measurements; `reproduction-v17.json` records that proof. Earlier scenes, outputs and measurement ledgers are history. `final-scene.json` and `recreation-status.json` identify the final input and actual delivered-file evidence. Use the same canonical file/hash across every adapter, without asset rebasing.

## Measured accuracy

All 1,283 aligned native source frames were scanned: mean channel MAE **{qa['mean_native_mae']:.5f}**, maximum **{qa['maximum_native_mae']:.5f}**, on the 0–255 channel scale. Twenty-four separated error peaks were compared at native resolution and visually reviewed. Thirteen encoded Remotion/GSAP checks measured MAE **{parity['mae']:.5f}**, SSIM **{parity['mean_ssim_luma']:.6f}**. These numbers are errors and sampled cross-engine agreement, not a perfection percentage or a 1:1 certification.

Evidence: [`source scan`](../../{qa['timeline_scan']}), [`native peak report`](../../{qa['native_peak_report']}), [`engine parity`](../../{qa['engine_parity_report']}), and [`review`](qa-v17-review.json). Picture export hashes, frame/cadence probes and render times are in `recreation-status.json`. Root production manages source audio and final muxed-file hashes separately.

Remaining visible differences:

{known}

## Process record

`steps-rebuild.md` records each implementation step, diagnosis and rejected retry. `lessons-for-skill.md` extracts the reusable workflow: exact native-frame indexing, independent physical/UI cameras, spatial eight-font ranking followed by browser ink fitting, censored-bound handling, component registration, immutable snapshots and full-timeline peak review. Every further revision should preserve its actual baseline before changing native caches. Do not refit against a changing live cache or apply a newer revision's delta to an older baseline.
'''
(p/'README-recreation.md').write_text(text)
print('Published V17 README')
