"""Write Linq's reviewable final-source evidence without inventing a perfection score."""
from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;R=D.parent.parent
scene=R/'outputs/05-linq/final-v19/scene.json';want=hashlib.sha256(scene.read_bytes()).hexdigest()
scan=json.loads((R/'verification/timeline-scans/05-linq-v19-pc709/scan.json').read_text())
report=json.loads((R/'verification/final/05-linq/source-gsap-v19-pc709/report.json').read_text())
summary=report['summary'];g=summary['global'];f=summary['foreground_union']
parityp=R/'verification/05-final-v19-primary-parity.json'
parity=json.loads(parityp.read_text())if parityp.exists()else None
statuses=[]
for method in ['gsap','remotion','html','pillow','motion-canvas']:
    p=R/f'outputs/05-linq/{method}.mp4.render.json'
    if p.exists():
        q=json.loads(p.read_text());current=q.get('sceneSHA256')==want
        statuses.append(f"| {method} | {'V19' if current else 'Earlier revision; see sidecar'} | {q.get('encoding',{}).get('profile','Not final PC709 encoded')} |")
text=f'''# Linq fidelity and editability status

The immutable authored input is `../../outputs/05-linq/final-v19/scene.json`, SHA256 `{want}`. It contains 1,458 graphic frames at 960×720 and 30 fps, lasting 48.6 seconds. All active changes are measured at native frame indices; original reference videos and complete source-frame sequences are not render layers.

The hash-bound, full-range BT.709 source-versus-GSAP scan measures every aligned native frame. Mean RGB MAE is **{scan['mean_native_mae']:.6f}/255**; maximum is **{scan['maximum_native_mae']:.6f}/255**. V18 under the same profile measured 1.377528 mean; V17 measured 1.496807; the earlier broad V9 scan measured 14.478 and exposed missing states and transitions. These are pixel errors, not a percentage of visual perfection. Read `../../verification/timeline-scans/05-linq-v19-pc709/scan.json`.

The 24 separated worst-frame report has global MAE {g['mae']:.6f}, foreground MAE {f['mae']:.6f}, and mean luma SSIM {g['mean_ssim_luma']:.6f}/{f['mean_ssim_luma']:.6f}. This deliberately difficult sample set is distinct from the timeline mean. Native source/candidate/difference triptychs and the visual gate are in `../../verification/final/05-linq/source-gsap-v19-pc709/`. All 24 are visually inspected before propagation to other methods.

V19 restores the first composer's actual glyph/control births, 23 independent typed glyphs, closing camera and measured native body shadows. Cash input has its actual independent exit and blinking caret. A single original 13×53 caret detail preserves its authentic soft color fringe; native position and opacity carry the blink. The Cash pulse uses an editable native backing ellipse, circle with measured gray/stroke/radius/position, and one original static 40×40 plus-alpha detail. The 59 cropped control diagnostics are not runtime assets. The white pawn remains on f2 through 227, moves 228–234 and settles 235; selected-cell/undo artwork and the pawn remain independent. Amount, original payment panel camera and other row content are preserved.

The full 1,458-state proof leaves all 1,281 states outside 0–98/226–239/768–831 identical to V18. Cumulative proofs from the actual V17 Remotion and V13 native baselines cover 344 and 649 capture states respectively. The latter contains 646 changed SVG states and three conservative unchanged guards 206–208. All font properties and face bytes remain identical. The final preflight validates 367 image/font assets with zero errors or warnings, and the scene has 2,417 unique IDs.

Outer scene geometry, chat, controls, native original glyph outlines, app/phone cameras, chess pieces, game counters, rolling payment digits, gradients, confetti, title stagger and message status timing remain editable. Bounded rich-app/card interiors and phone artwork retain bitmap internal text and detail with provenance. Original outline copy keeps semantic strings but is edited as vector shapes. V15 board materials are mathematical color/alpha corrections derived from the one original static board and authored backdrop renders; reference pixels calibrate parameters and validate them but are not copied into those textures. Regenerate dependent material after editing internal board/backdrop content. The closing Linq brand mark and wordmark are native original outlines; the former transparent bitmap logo is not referenced.

| Method | Sidecar revision at this report | Encoding profile |
| --- | --- | --- |
{chr(10).join(statuses)}

Each actual sidecar, rather than this static table, is authoritative as the independently coordinated exports finish. All final masters must name this exact scene hash and `full-range-bt709-v1`.

'''
if parity:
    text+=f"The independent GSAP/Remotion lossless comparison covers all 1,458 frames: mean frame MAE {parity['meanFrameMAE']:.8f}, maximum channel difference {parity['maxChannelDelta']}, {parity['identicalRGBCount']} pixel-identical frames. The observed older cached Remotion 625 truncation is refreshed and verified; its historical cause remains unproven. See `../../verification/05-final-v19-primary-parity.json`. This renderer-parity check is separate from source fidelity.\n\n"
text+='Remaining visible differences include restaurant-photo material/resampling, phone-gallery optics/fade, some intermediate exposure/blur, edge antialiasing/shadows and source compression. A read-only restaurant 1100 registration test explains only about 5% of its photo ROI error, so it is not attributed solely to geometry or antialiasing. Original transfer curves and all optical detail have not been recovered. Exact 1:1 fidelity has not been established; no 100% claim or inferred perfection percentage is made. Read `iteration-notes-v19.md` and the hash-bound source/visual reports for the concrete evidence and limits.\n'
(D/'quality.md').write_text(text)
print(D/'quality.md')
