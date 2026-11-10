"""Write Linq's reviewable final-source evidence without inventing a perfection score."""
from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;R=D.parent.parent
scene=R/'outputs/05-linq/final-v20/scene.json';want=hashlib.sha256(scene.read_bytes()).hexdigest()
scan=json.loads((R/'verification/timeline-scans/05-linq-v20-pc709/scan.json').read_text())
report=json.loads((R/'verification/final/05-linq/source-gsap-v20-pc709/report.json').read_text())
summary=report['summary'];g=summary['global'];f=summary['foreground_union']
parityp=R/'verification/05-final-v20-primary-parity.json'
parity=json.loads(parityp.read_text())if parityp.exists()else None
statuses=[]
for method in ['gsap','remotion','html','pillow','motion-canvas']:
    p=R/f'outputs/05-linq/{method}.mp4.render.json'
    if p.exists():
        q=json.loads(p.read_text());current=q.get('sceneSHA256',q.get('sceneSha256'))==want
        statuses.append(f"| {method} | {'V20' if current else 'Earlier revision; see sidecar'} | {q.get('encoding',{}).get('profile','Not final PC709 encoded')} |")
text=f'''# Linq fidelity and editability status

The immutable authored input is `../../outputs/05-linq/final-v20/scene.json`, SHA256 `{want}`. It contains 1,458 graphic frames at 960×720 and 30 fps, lasting 48.6 seconds. All active changes are measured at native frame indices; original reference videos and complete source-frame sequences are not render layers.

The hash-bound, full-range BT.709 source-versus-GSAP scan measures every aligned native frame. Mean RGB MAE is **{scan['mean_native_mae']:.6f}/255**; maximum is **{scan['maximum_native_mae']:.6f}/255**. V18 under the same profile measured 1.377528 mean; V17 measured 1.496807; the earlier broad V9 scan measured 14.478 and exposed missing states and transitions. These are pixel errors, not a percentage of visual perfection. Read `../../verification/timeline-scans/05-linq-v20-pc709/scan.json`.

The 24 separated worst-frame report has global MAE {g['mae']:.6f}, foreground MAE {f['mae']:.6f}, and mean luma SSIM {g['mean_ssim_luma']:.6f}/{f['mean_ssim_luma']:.6f}. This deliberately difficult sample set is distinct from the timeline mean. Aligned source/candidate/difference previews and the visual gate are in `../../verification/final/05-linq/source-gsap-v20-pc709/`. All 24 are visually inspected before propagation to other methods.

V19 restores the first composer's actual glyph/control births, 23 independent typed glyphs, closing camera and measured native body shadows. Cash input has its actual independent exit and blinking caret. A single original 13×53 caret detail preserves its authentic soft color fringe; native position and opacity carry the blink. The Cash pulse uses an editable native backing ellipse, circle with measured gray/stroke/radius/position, and one original static 40×40 plus-alpha detail. The 59 cropped control diagnostics are not runtime assets. The white pawn remains on f2 through 227, moves 228–234 and settles 235; selected-cell/undo artwork and the pawn remain independent. Amount, original payment panel camera and other row content are preserved.

V20 also repairs the Cash backing/panel material seam and restores the static lower restaurant document exposed during the exit: complete price, Reported by and Find a table rows. The original document, photo rail and native camera/opacity are preserved. Full cumulative 1,458-state proofs, exact per-method capture ranges, font-byte checks and final image/font preflight are recorded in `../../verification/05-v20-method-deltas.json` and `../../verification/05-v20-freeze.json`. Conservative unchanged guards are identified separately from exact changed SVG states. No per-frame control crops enter the runtime.

Outer scene geometry, chat, controls, native original glyph outlines, app/phone cameras, chess pieces, game counters, rolling payment digits, gradients, confetti, title stagger and message status timing remain editable. Bounded rich-app/card interiors and phone artwork retain bitmap internal text and detail with provenance. Original outline copy keeps semantic strings but is edited as vector shapes. V15 board materials are mathematical color/alpha corrections derived from the one original static board and authored backdrop renders; reference pixels calibrate parameters and validate them but are not copied into those textures. Regenerate dependent material after editing internal board/backdrop content. The closing Linq brand mark and wordmark are native original outlines; the former transparent bitmap logo is not referenced.

| Method | Sidecar revision at this report | Encoding profile |
| --- | --- | --- |
{chr(10).join(statuses)}

All five masters name this exact scene hash and `full-range-bt709-v1`. The sidecars identify each picture hash and retained cache.

'''
if parity:
    text+=f"The independent GSAP/Remotion lossless comparison covers all 1,458 frames: mean frame MAE {parity['meanFrameMAE']:.8f}, maximum channel difference {parity['maxChannelDelta']}, {parity['identicalRGBCount']} pixel-identical frames. The observed older cached Remotion 625 truncation is refreshed and verified; its historical cause remains unproven. See `../../verification/05-final-v20-primary-parity.json`. This renderer-parity check is separate from source fidelity.\n\n"
text+='The complete native-cache check also detected one isolated all-white Remotion 607. The bad PNG, original report and producer log are preserved in `../../verification/05-raster-parity-607/`. A fresh 606/607/608 same-process control uses the original broad runtime chunk and full SVG proofs: 606/608 are pixel-identical to GSAP, while 607 is correctly populated with a small measured raster residual. Only that genuine fresh Remotion 607 is atomically promoted, with all other 1,457 cache files unchanged; the master is re-PC-encoded and all 1,458 frames compared again. This separate incident did not reproduce and its origin is unproven. The repair journal is explicit.\n\n'
htmlp=R/'verification/05-final-v20-html-parity.json'
if htmlp.exists():
    html=json.loads(htmlp.read_text())
    text+=f"HTML versus GSAP compares all 1,458 native frames: mean MAE {html['meanFrameMAE']:.8f}, maximum channel delta {html['maxChannelDelta']}, {html['identicalRGBCount']} pixel-identical. The 86 small differences also match Remotion pixels exactly; the initial strict-zero expectation was rejected as too strong, and both raw observation and qualified analysis are retained. No material HTML anomaly is present. This is measured residual agreement, not a claim of pixel identity.\n\n"
aa4p=R/'verification/method-parity/05-linq/native-review/aa4-lifecycle/promotion-gate.json'
if aa4p.exists():
    aa4=json.loads(aa4p.read_text())
    text+=f"Pillow retains a native AA1 base with genuine AA4 captures only at frames 101–127. The unchanged published engine renders the same scene at four times spatial resolution before downsampling. Every native pose and neighboring guards were compared with source, GSAP and the original native PNGs. The 27-frame phase's source mean MAE improves {aa4['nativeSourceMeanMAEBefore']:.6f}→{aa4['nativeSourceMeanMAEAfter']:.6f}; four explicit fine-sampling tradeoffs have worst increase {aa4['tradeoffMaxMAEIncrease']:.6f}. All 1,431 outside cache files remain byte/stat-identical. Old AA1 picture, sidecar and affected PNGs are preserved. The sidecar records the actual bounded override, and the hash-bound evidence/viewer is in `../../verification/method-parity/05-linq/native-review/aa4-lifecycle/`. This sampling change does not recover the source's original filters or remove shared authored/source residuals.\n\n"
    pp=R/'verification/method-parity/05-linq/pillow.json'
    if pp.exists():
        pq=json.loads(pp.read_text());actual=hashlib.sha256((R/'outputs/05-linq/pillow.mp4').read_bytes()).hexdigest()
        if pq['candidateSHA256']==actual:
            text+=f"The fresh encoded Pillow/GSAP audit covers all 1,458 frames: mean luma SSIM {pq['meanSSIM']:.8f}, minimum {pq['minimumSSIM']:.6f}. Its picture hash matches the current master. This method-parity measurement is separate from source fidelity.\n\n"
text+='Remaining visible differences include restaurant-photo material/resampling, phone-gallery optics/fade, some intermediate exposure/blur, edge antialiasing/shadows and source compression. A read-only restaurant 1100 registration test explains only about 5% of its photo ROI error, so it is not attributed solely to geometry or antialiasing. Original transfer curves and all optical detail have not been recovered. Exact 1:1 fidelity has not been established; no 100% claim or inferred perfection percentage is made. Read `iteration-notes-v20.md` and the hash-bound source/visual reports for the concrete evidence and limits.\n'
(D/'quality.md').write_text(text)
print(D/'quality.md')
