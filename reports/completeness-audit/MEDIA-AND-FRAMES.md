# Final media and frame completeness audit

**The accepted final media is present.** This checkout contains all six retained original references, all thirty completed results, all thirty silent picture masters and all twelve later UI-audio previews. There is no missing final film or truncated accepted timeline among those checked. Under the clarified request—final accepted code/keyframes and final videos—old revisions and raw frame-cache history are not a delivery blocker.

This is a fresh local, read-only audit of checkout commit `874471f` and its restored resources. It makes no independent claim about remote GitHub state; the parent task verifies the push. Only this report and its JSON were written. No production media, scene, manifest or inventory was changed. No network or paid tool was used.

## What was actually checked

- All **118 MP4 paths** were independently hashed and freshly inspected with `ffprobe`: every one has a nonempty video stream. There are **75 unique binary containers**; duplicate copies and soundtrack variants inflate the path count.
- All **36 canonical paths**—six original clips and thirty final results—are covered by full FFmpeg decoding of their **34 unique binary files**, with video **and audio** mapped. The two redundant pairs are PhotonHQ HTML/Remotion and Gallery HTML/Remotion. All decodes completed with no reported errors; every decoded frame count equals the container's declared frame count. This read **43,037 picture frames**. Concurrency was limited to two and each process used one decoding thread.
- All **30 final results** match their accepted scene dimensions, rational frame rate and total native frame count. The **30 silent masters and 12 UI previews** also match their corresponding accepted timeline. All 30 silent masters have no audio stream; all canonical results and UI previews have an audio stream.
- The other **41 unique binary containers**—silent masters, UI previews and test fixtures—received fresh `ffprobe`/size/hash inspection, not a new full decode. Their preserved byte hashes provide integrity evidence; this report does not call a header probe a complete playback test.

The full per-file metadata, SHA256, audio/video streams, decoder outcomes and exact local paths are in [MEDIA-AND-FRAMES.json](MEDIA-AND-FRAMES.json). That JSON also lists every retained raster-image directory and its filenames.

## Video locations and counts

All paths below are relative to the repository root. The canonical example project root is `projects/<example>-complete-v1/imessage-recreations/`.

| Role | MP4 paths | Location |
|---|---:|---|
| Six canonical downloaded references | 6 | `projects/*/imessage-recreations/references/<example>/source.mp4` |
| Five completed formats for each example | 30 | `projects/*/imessage-recreations/deliverables/<example>/{remotion,gsap,html,pillow,motion-canvas}.mp4` |
| Silent picture masters | 30 | `resources/silent-picture-masters-v1/imessage-recreations/outputs/<example>/<method>.mp4` |
| Two later UI-audio variants for each example | 12 | `resources/complete-ui-audio-source-v1/imessage-recreations/audio-recreation/ui-previews/<example>-{ui,recreated}.mp4` |
| Frozen duplicate copy of six references and thirty results | 36 | `resources/frozen-visual-delivery-v1/imessage-recreations/{references,deliverables}/...` |
| Small renderer-test fixture clips | 4 | `resources/all-authored-source-and-fixtures-v1/imessage-recreations/engines/fixtures/{dynamic-path,shadow-opacity}/...` |
| **Total** | **118** | **75 unique file hashes, not 118 different stories** |

The thirty main final MP4s retain the supplied reference soundtracks. Newly sourced/generated UI sound mixes are the separate twelve preview files; those two sets should not be conflated. The originals are the retained downloaded H.264 references, not the creators' uncompressed production masters or original editing applications.

## Actual accepted timelines

The dimensions, frame rates, durations and counts below come from fresh probing. Duration means the video stream's duration; an MP4 container's duration may differ slightly because audio packets end later. All five final methods per example have the listed accepted frame count.

| Example | Canvas | FPS | Original frames / seconds | Final frames / seconds | Five final timelines match scene? |
|---|---|---|---|---|---|
| 01-photonhq | 1920 × 1080 | 30/1 | 655 / 21.833333 | 655 / 21.833333 | Yes |
| 02-danieltian | 1920 × 1080 | 30/1 | 1360 / 45.333333 | 1360 / 45.333333 | Yes |
| 03-photon-mini | 1920 × 1080 | 30/1 | 1260 / 42.000000 | 1260 / 42.000000 | Yes |
| 04-poke | 1440 × 1080 | 30000/1001 | 1283 / 42.809433 | 1283 / 42.809433 | Yes |
| 05-linq | 960 × 720 | 30/1 | 1458 / 48.600000 | 1458 / 48.600000 | Yes |
| 06-gallery | 1920 × 1080 | 30/1 | 1664 / 55.466700 | 1483 / 49.433333 | Yes |

Across the six accepted output timelines there are **7,499 native frames**, or **37,495 picture-frame positions across five formats**. The six originals contain **7,680** picture frames.

The entire difference is the authorized graphic-only edit for Gallery/Rene: original frames **1049–1229 inclusive** (34.9666667–41.0 seconds, 181 frames) are omitted from the reconstruction. Output frame 1049 maps to original frame 1230. The full original remains locally stored. The explicit edit map is [segments.json](../../projects/06-gallery-complete-v1/imessage-recreations/references/06-gallery/segments.json). No other example drops reference frame indices in its stored source scan.

## Numeric frame analysis is complete for its stated purpose

Each canonical CSV in [director/analysis/](../../skill/imessage-motion-recreation/director/analysis/) has one contiguous zero-based row per accepted output frame. The six counts sum to **7,499**, with no missing or duplicate candidate frame indices. Its six columns are `candidate_frame`, `reference_frame`, `candidate_time`, `reference_time`, `mae` and `max_channel_error`.

These are **numeric source-versus-GSAP comparison records**, not 7,499 human-written descriptions of intent, composition, easing or why a director chose a motion. This audit independently verified that each stored source-scan reference hash matches the retained original and its candidate hash matches the retained silent GSAP master.

There are also **24 stored method-parity reports**, comparing the other four formats with GSAP across all their declared frame counts: **29,996 frame comparisons**. Every report's GSAP and candidate movie hashes matches the corresponding retained silent master. These stored comparisons were not recalculated here; they are preserved, correctly bound evidence. Their own notice says they are diagnostic heuristics, not a source-fidelity certificate. The source scan plus method-parity data is materially more extensive than the fourteen teaching recipes, while still being a different kind of analysis.

## Visual explanation coverage

There are **fourteen selected motion studies with 84 source/reconstruction teaching pairs** in [director/catalogue.json](../../skill/imessage-motion-recreation/director/catalogue.json). The corresponding fourteen atlas JPEGs are stored in [director/atlas/](../../skill/imessage-motion-recreation/director/atlas/). Each atlas has six selected phase pairs, downsampled for teaching. One Mini phase occurs in more than one study, so the 84 pairs represent **83 distinct output-frame positions** across the six examples.

The final visual comparison pages preserve **24 downsampled source/reconstruction/difference triptych JPEGs per example**, or 144 selected visual samples in the canonical project set. The frozen delivery contains duplicate copies. These are selected samples across the timeline; the numeric scan covers the full accepted timeline.

| Example | Numeric rows / accepted frames | Selected comparison time positions | Fraction visually sampled in final triptychs | Teaching studies / pairs |
|---|---:|---:|---:|---:|
| 01-photonhq | 655 / 655 | 24 | 3.66% | 2 / 12 |
| 02-danieltian | 1360 / 1360 | 24 | 1.76% | 3 / 18 |
| 03-photon-mini | 1260 / 1260 | 24 | 1.90% | 3 / 18 |
| 04-poke | 1283 / 1283 | 24 | 1.87% | 2 / 12 |
| 05-linq | 1458 / 1458 | 24 | 1.65% | 2 / 12 |
| 06-gallery | 1483 / 1483 | 24 | 1.62% | 2 / 12 |

These percentages describe the selected triptych report images, not frame availability in the actual MP4s. Every accepted frame remains encoded in each completed film. Fourteen recipes are a curated teaching layer; they are not an exhaustive semantic catalogue of every change appearing in all six movies. The per-example `references/<example>/analysis.md`, source-study JSON, timelines and repair logs add explanations, but no audited file establishes human/director annotation of every native frame or a complete account of every historical thought/experiment. That is a remaining teaching-layer expansion if desired, not missing accepted final animation data.

Decoding and matching timeline counts establish media completeness and decodability. The stored source metrics have nonzero error values; neither the checks here nor the number of teaching studies proves 100% visual identity with the references.

## Raster inventory

The checkout contains **10,070 PNG/JPG raster paths**, representing **5,089 unique binary images**, across **87 directories**. The complete directory/file-name inventory and image dimensions are in the JSON report.

| Raster role | File paths | Interpretation |
|---|---:|---|
| Scene render assets, including duplicate frozen copy | 9,214 | 4,607 cropped/component/material images in the six canonical scenes, mirrored in the frozen delivery; these are not complete native frame caches |
| Selected downsampled final comparison triptychs | 288 | 144 canonical samples plus 144 duplicate frozen copies |
| Other selected native/debug evidence | 372 | Targeted samples, difference views, contacts and repair diagnostics; includes duplicate copies |
| Renderer fixture images | 133 | Small controlled tests, not source-film frames |
| Audio-analysis and cue visuals | 17 | Sound analysis/cue aids |
| Downsampled teaching atlases | 28 | Fourteen canonical atlases plus fourteen copies in later workflow source |
| Starter, poster and research visuals | 18 | Additional visual aids |

None of the 4,607 canonical scene-image assets has that example's full canvas dimensions. They are retained ingredients used by the scene, not a disguised complete PNG copy of each original frame. The actual accepted scene/keyframe and asset completeness is addressed by the separate source audit.

## Appendix: optional raw frame-cache history

No complete individually stored native PNG sequence for any full original or completed movie is retained in the expanded checkout. That is consistent with excluding old/transient frame caches under the clarified scope. Some useful native samples do survive:

- Daniel retains 24 native original/candidate PNG pairs with an explicit [frame mapping](../../projects/02-danieltian-complete-v1/imessage-recreations/verification/final/02-danieltian/source-gsap-v19/native-peaks/mapping.json), plus several method-parity decoded samples.
- Linq retains a native 33-frame source/GSAP/AA comparison window for frames 98–130 in [aa4-lifecycle](../../resources/frozen-visual-delivery-v1/imessage-recreations/verification/method-parity/05-linq/native-review/aa4-lifecycle/), plus other targeted probes.
- Mini and Poke retain a smaller number of targeted native/debug captures. Some canvas-sized files are difference/contact views, so image dimensions alone are not proof of a clean source frame.

Historical JSON such as Linq's `production-before-inventory.json` lists hashes/paths for an old full PNG cache. It records that the cache existed during production; the list is not the cache bytes themselves. This distinction prevents treating an old absolute working path as a currently available file.

All retained video frames can be decoded into local PNGs without the internet. For example, after creating an output directory, use FFmpeg's passthrough frame mode and zero-based numbering:

```bash
ffmpeg -i projects/01-photonhq-complete-v1/imessage-recreations/references/01-photonhq/source.mp4 \
  -map 0:v:0 -fps_mode passthrough -start_number 0 /your/output/directory/%06d.png
```

Those PNGs contain the decoded compressed-video pixels. They do not recover the exact pre-encode lossless renderer PNG bytes or the original creator's uncompressed master. Re-rendering the accepted scene may reproduce pre-encode captures when the relevant renderer/font/environment inputs match; it is a separate operation and was not performed in this audit. No new PNG cache or production render was created.

## Unsupported claims to avoid

- “118 different completed creative examples.” There are six stories with format/audio variants, duplicates and four small fixture paths.
- “Every frame is already a separate PNG.” Full frames are encoded in the films; only selected standalone frame images are retained.
- “7,499 human/director explanations.” The 7,499 rows are numeric frame comparisons.
- “Fourteen studies exhaust every motion in these films.” They are curated phase-based teaching recipes.
- “All 118 files received a new full playback/decode test.” All 118 were probed; full decoding covered the 34 unique canonical files and, by byte identity, their duplicated frozen copies.
- “Decoder success proves pixel perfection.” It proves decoding/timeline integrity, not visual identity or semantic editability.

The useful, supported conclusion is that **the accepted final films and their complete native timelines are present and the canonical movies fully decode**. The optional PNG-cache history and exhaustive semantic teaching layer are separate from that final-media completeness.
