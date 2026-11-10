# iMessage launch motion recreations

Open [review.html](review.html) to compare each source with its recreation. The page synchronizes playback and includes all completed rendering methods. If your browser restricts local video, run `python3 -m http.server 8765 --bind 0.0.0.0` from this directory and open `http://localhost:8765/review.html`.

The project rebuilds the motion and graphic portions of the six supplied references. Each scene has independent layers, measured timing and camera tracks. Original bounded product artwork, logos, photos and some UI text are declared image assets; other typography uses traced vector outlines with semantic copy. Those pixels and outlines are less editable than live text. No complete reference video or full-frame reference sequence is used as the reconstruction.

| Reference | Picture size | Frame rate | Recreated duration |
|---|---:|---:|---:|
| PhotonHQ | 1920 × 1080 | 30 | 21.833 s |
| Daniel Tian / Photon agents | 1920 × 1080 | 30 | 45.333 s |
| Photon mini apps | 1920 × 1080 | 30 | 42.000 s |
| Poke / Apple Messages | 1440 × 1080 | 30000/1001 | 42.809 s |
| Linq / iMessage apps | 960 × 720 | 30 | 48.600 s |
| Rene / Launch Videos Gallery | 1920 × 1080 | 30 | 49.433 s |

Rene omits the live-action interval from source 34.966667 to 41 seconds, as allowed in the request. Its [time map](references/06-gallery/segments.json) also controls comparison playback and soundtrack cuts.

`outputs/<reference>/<method>.mp4` contains silent graphic masters. `deliverables/<reference>/<method>.mp4` contains the same independently reconstructed picture with the reference soundtrack. Methods are `remotion`, `gsap`, `html`, `pillow`, and `motion-canvas`. Completion sidecars record the exact scene hash, dimensions, frame count and method. A replacement is offered only when its completion sidecar matches the current canonical scene.

The portable archive includes all thirty soundtrack versions and their capture metadata. Silent masters, retained frame caches and older iterations remain in the working project; the included engines can render the canonical scenes again.

Remotion renders genuine React frame indices. GSAP seeks a real timeline before browser capture. HTML/SVG is the separate deterministic web experiment. Pillow draws native frames and FFmpeg encodes them. Motion Canvas uses its own scene-graph renderer. Shared measurements keep their layouts comparable; the engines remain separate implementations. The [renderer instructions](engines/README.md) describe commands and dependencies.

Capture sidecars preserve the engine fingerprints actually used. When a later engine repair has zero effect on a scene, its compatibility audit explains why those existing frames remain valid. A retained capture is never relabeled as a fresh render.

Pillow uses a base sampling factor of 1, with bounded factors 2 or 4 for two difficult transitions. The exact intervals and rebuild sequence are in [render-overrides.json](render-overrides.json). Apply those overrides after a complete base capture when reproducing the retained pictures.

Figma Motion could not be accessed: account discovery did not return, and the browser fallback failed before reaching Figma. No Figma file or export was produced. The [Figma status](figma/status.json) preserves the evidence and labels the local converter as an unexecuted prototype.

Fidelity reports compare every aligned GSAP frame with the source, then inspect separated error peaks with native visual and foreground comparisons. Dense method comparisons check the other four renderers against that measured timeline; renderer agreement and source fidelity are separate checks. Measurements diagnose specific discrepancies; they are not a percentage of perfection. Differences in font interiors, clipping, deformation and fitted motion remain. The scene files and detailed logs identify approximation and asset boundaries.

The reusable [skill](skill/imessage-motion-recreation/SKILL.md) contains the workflow, failure diagnoses, source acquisition notes, rendering tools and verification procedure. [Execution ledger](skill/imessage-motion-recreation/references/execution-ledger.md) indexes the detailed step logs. The installable archive is `imessage-motion-recreation-skill.zip`.

`delivery-manifest.json` and the review page are generated from completed artifacts. Older numbered iterations and diagnostics remain in the working project as evidence; only exact method filenames are offered as completed candidates in the review selector.
