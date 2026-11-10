from pathlib import Path
import json
P=Path(__file__).parent
rows=json.load(open(P/'native-metrics-v3.json'))
changed=[r for r in rows if not r['nativePixelsSame']]
proof=json.load(open(P/'scope-v3.json'));structure=json.load(open(P/'structure-proof-v3.json'))
maximum=max(r['after']for r in changed)
accept=dict(nativeFramesChecked=len(rows),changedNativeFramesChecked=len(changed),allChangedNativeFramesImprove=all(r['after']<r['before']for r in changed),unchangedNativeControls=[r['frame']for r in rows if r['nativePixelsSame']],maxCorrectedNativeMAE=maximum,meanBefore=sum(r['before']for r in changed)/len(changed),meanAfter=sum(r['after']for r in changed)/len(changed),exactChangedRanges=proof['exactChangedRanges'],outsideFramesChecked=proof['checkedFrames']-proof['changedFrames'],allOutsideEvaluatedMarkupIdentical=not proof['changedOutsideCaptureUnion'],gradientsIdentical=structure['gradientsIdentical'],limitations=[f'No100% claim: optical/AA/hardware material remains, maximum corrected nativeMAE{maximum:.4f}','Bitmap card/header/composer internals remain image actors; their camera/scale/opacity/lifetime are editable.','Short food/title exit artwork800–807 is per bounded graphic element; not full-source-screen/frame/video playback.','Unchanged813 game-entry nativeMAE6.1668 remains outside this helper; owner should retain it in full-timeline residual accounting.'])
(P/'acceptance.json').write_text(json.dumps(accept,indent=2))
print(json.dumps(accept,indent=2))
(P/'findings.md').write_text('''# Mini remaining full-scan peak review

Released ID helper: `references/03-photon-mini/apply-remaining-peaks-review.py` with immutable elements in `outputs/03-photon-mini/remaining-peaks-review-03/remaining-peaks-review-elements.json`. Base is immutable final-v14. Exact changed frames310–334,438,800–812; every other1221 native state is identical.

- Mail322: retained correct hardware/send camera, rebuilt the independently projected pane/handle and actually visible subject glyphs. Native7.397→1.142.
- Avatar438: first-title gate, one-frame Alice pose dip, and missing circular cluster aperture. Genuine portrait actors retained; native7.262→2.478.439 remains pixel-identical.
- Chat804: independently spring the Zoom card, restore actual UI internals/sender/Agent/composer, fit physical camera, keep outgoing food/Order graphics through807, and add native tap dim805 onward. Native8.697→1.192;8007.517→.909. Static card/UI internals are bounded image assets with editable camera/lifecycle, not individual editable internal text.

All39 changed native frames improve; six neighboring native controls are pixel-identical. Source-native evidence is separate from encoded scan scores. Prototype comparison revealed an incorrectly contracting second-sender row gap and a missing tap dim; corrected those measured causes before the final dense batch. A proposed OpenCV contour helper was unavailable; reused the existing source-graphic alpha tracer instead of installing a dependency.

No canonical/full MP4/other owner range changed. Remaining source AA/hardware material/optical contours are visible at native size; this is not100% identical. The unchanged813 game-entry MAE6.1668 is explicitly recorded for the parent full-timeline scan.
''')
(P/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Mini peak review</title><style>body{font:16px system-ui;margin:32px;max-width:1200px}img{max-width:100%}a{margin-right:16px}</style><h1>Mini remaining peak review</h1><p>39 changed native frames;1221 outside evaluated states identical. All changed frames improve. Six controls remain pixel-identical. No100% claim.</p><p><a href="acceptance.json">Acceptance</a><a href="native-metrics-v3.json">All45 native comparisons</a><a href="scope-v3.json">1260-frame scope proof</a><a href="structure-proof-v3.json">ID/asset structure proof</a><a href="findings.md">Findings and limitations</a></p><img src="comparison-v3.jpg">''')
