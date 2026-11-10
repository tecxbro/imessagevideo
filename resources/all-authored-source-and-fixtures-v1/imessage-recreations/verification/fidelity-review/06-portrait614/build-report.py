from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,html
P=Path(__file__).parent;R=P.parents[2];rows=json.load(open(P/'native-metrics.json'));changed=[r for r in rows if 613<=r['frame']<=615];accept=dict(status='Accepted bounded improvement; optical/material residual remains',changedRanges=[[613,615]],nativeMeanBefore=sum(r['before']for r in changed)/3,nativeMeanAfter=sum(r['after']for r in changed)/3,controlsPixelIdentical=all(r['controlPixelIdentical']for r in rows if r['frame']in[612,616,619]),sceneSha256='e1761af59184bd2a5342be6709a0555387f966e005f7d12628adc4a2a6bfce1f',remaining='614 retains4.960 native full-frame MAE; untouched616 remains6.105. Genuine static-photo detail, blur/UV registration and optical/AA differences remain; no exact-match or AA-only claim.');(P/'acceptance.json').write_text(json.dumps(accept,indent=2))
canvas=Image.new('RGB',(1440,3*296),'#ddd');d=ImageDraw.Draw(canvas)
for row,f in enumerate([613,614,615]):
 r=next(r for r in rows if r['frame']==f)
 for col,(label,file)in enumerate([('Source',P/'source'/f'{f:06}.png'),(f'V20 {r["before"]:.3f}',P/'baseline-v20'/f'{f:06}.png'),(f'Corrected {r["after"]:.3f}',P/'final-gsap'/f'{f/30:.3f}.png')]):
  canvas.paste(Image.open(file).resize((480,270)),(col*480,row*296+26));d.text((col*480+8,row*296+6),f'{f} {label}',fill='black')
canvas.save(P/'comparison.jpg',quality=94)
text='''# Rene birthday portraits613–615

The accepted change improves the actual source mismatch while preserving every outside evaluated source state. It does **not** close the phase to an exact match.

The principal cause was a partial-disc registration error: the clipped actor71 at614 was modeled with center(404,41), diameter289 and53px blur. Visible-quarter source registration instead locates approximately center(402,−20), diameter340 and11px blur. Blindly zeroing blur exposes the wrong geometry and worsens the frame. The large actor79 also used a150×148 static photo enlarged to roughly1700px; a genuine source622 photograph supplies better detail, with normalized alpha preserved and independent native camera/blur/shadow. Other left/right faces had separate measurable camera/blur errors; they remain independent actors.

Measured small RGB contrast corrections are applied to the genuine static photo material, preserving its alpha and identity. No new identity, complete source frame, screen recording, scene texture or motion-frame playback is used. Actor transforms, lifetimes, blur and shadows remain editable; the photographed faces remain raster materials.

Rejected trials: blur0 alone; lowering79 opacity; three alpha/RGB-camera decoupling hypotheses;95/79 draw-order changes;18 procedural directional-blur hypotheses. Each was measured against the full native frame before rejection. A preliminary isolated visibility fit forced actor71 opaque at613; source71 is actually invisible there, so that diagnostic pose/lifecycle was discarded and never merged.

All actual613–615 frames and controls612/616/619 are checked in native GSAP at1920×1080. Source614 cached measurement is pixel-identical to a fresh exact-n614 source decode. Source/native versus encoded differences are reported separately. The corrected scene leaves a visible material/optical residual, especially in the clipped face boundaries and foreground hair. Unchanged616 is not certified exact.

No canonical scene, shared engine, full video or final output writer was changed by this review.
'''
for r in rows:text+=f'\n- Frame{r["frame"]}: native MAE{r["before"]:.6f}→{r["after"]:.6f}; control identical={r["controlPixelIdentical"]}.'
text+='\n\nFrozen input: outputs/06-gallery/portrait614-review-01/scene.json. Helper: references/06-gallery/apply-portrait614-review.py. Immutable elements: outputs/06-gallery/portrait614-review-01/portrait614-review-elements.json. Exact scope/properties: scope.json and structure-proof.json.\n';(P/'findings.md').write_text(text)
links=['acceptance.json','native-metrics.json','scope.json','structure-proof.json','encoding-attribution.json','findings.md','local-fit.json','color-fit.json','direction93-tests.json','depth-tests.json','uv79-tests.json'];body=''.join(f'<li><a href="{x}">{x}</a></li>'for x in links);(P/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Rene613–615 fidelity review</title><style>body{font:16px system-ui;margin:30px;max-width:1500px}img{width:100%}p{max-width:1050px;line-height:1.5}</style><h1>Rene birthday portrait correction613–615</h1><p>Accepted bounded improvement; material/optical differences remain. Source | V20 native | corrected native. No100% claim. All outside1480 evaluated states are retained;612/616/619 native controls are pixel-identical.</p><img src="comparison.jpg"><p>614 native MAE7.859→4.960;6157.001→4.328;6132.937→2.512. Actor camera/blur/material fixes are separate from video encoding. Photographs remain bounded raster materials; native transforms, lifetimes, blur and shadows remain editable.</p><ul>'+body+'</ul>')
print(accept)
