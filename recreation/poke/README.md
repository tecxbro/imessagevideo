# Poke restaurant selection repair

[Corrected GSAP export](delivery/poke-corrected.mp4) · [Source and correction side by side](delivery/poke-side-by-side.mp4) · [Independent UI stem](delivery/ui.flac)

The original is on the left in the comparison. The soundtrack is the rebuilt mix. The accepted GSAP export remains in the [historical project](../../projects/04-poke-complete-v1/imessage-recreations/deliverables/04-poke/gsap.mp4).

Both the blue circle `p0249` and white checkmark `p0250` under the moving sheet `p0255` used a start of 21.5 seconds. At 30000/1001 fps the first frame at or beyond that time is 645. The source switches from outlined to blue on frame 633, exactly 21.1211 seconds. The staged project changes those two starts. The sheet camera, food artwork, neighboring rows, and clipping stay on their original tracks.

| Decoded event | Original | Accepted GSAP | Corrected GSAP |
| --- | ---: | ---: | ---: |
| Zareen’s selection appears | 633 | 645 (+12) | 633 (0) |
| Zareen’s stays selected through tested frame | 650 | 650 | 650 |
| Friday 7:30 PM becomes selected | 232 | 232 (0) | 232 (0) |
| Nearby Khazana, Darbar and 10:30 PM controls | Unselected | Unselected | Unselected |

The regression reads decoded pixels in consecutive frames. It fails on the old export and passes on the source and correction. [Render evidence](evidence/) includes the timing reports, native scan CSVs and the [text and timing edit](evidence/editability.jpg). In that separate edit, the label reads “Zareen’s Demo” and the check first appears at 638. Both screenshots came from the GSAP checkpoint renderer.

## Recreate the export locally

Install the GSAP project's pinned Node packages and set `CHROME_PATH` to Chromium or Chrome. For audio, use Python with NumPy and the existing synthesis and licensed sound library in the repo. FFmpeg and ffprobe are required. Start at the repository root with a new working directory.

```sh
repo="$PWD"
project="$repo/projects/04-poke-complete-v1/imessage-recreations"
work="$(mktemp -d)"
python3 recreation/poke/prepare.py "$work/scene"
node "$project/engines/render.mjs" --method gsap --scene "$work/scene/scene.json" \
  --out "$work/preview.mp4" --frames-dir "$work/frames"
ffmpeg -v error -n -threads 1 -filter_threads 1 -framerate 30000/1001 \
  -i "$work/frames/%06d.png" -frames:v 1283 -c:v libx264 -threads 2 \
  -vf 'scale=in_range=full:out_range=full:out_color_matrix=bt709,setparams=range=full:color_primaries=bt709:color_trc=bt709:colorspace=bt709' \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range pc \
  -crf 16 -pix_fmt yuv420p -movflags +faststart "$work/picture.mp4"
python3 recreation/poke/render_audio.py "$work/sound" --picture "$work/picture.mp4"
python3 recreation/poke/check_selection.py "$work/sound/poke-corrected.mp4"
node skill/imessage-motion-recreation/scripts/verification/prove_scene_scope.mjs \
  --input "$project/scenes/04-poke/scene.json" --candidate "$work/scene/scene.json" \
  --ranges 633:644 --out "$work/scope.json"
```

Open `$work/scene/scene.json` for the complete editable timeline and assets. Set the appropriate layer's `text`, `start`, or `keyframes`, then rerun the GSAP command with a fresh destination. The input asset hashes are pinned to the project. The historical scene includes declared bounded image assets such as photos, maps, Memoji, service marks, and sampled hardware/artwork. This repair inherits those boundaries. See the [base scene and assets](../../projects/04-poke-complete-v1/imessage-recreations/scenes/04-poke/).

## Verification and remaining differences

- **Decoded picture.** The source and output have 1,283 frames, 1440×1080 and exact 30000/1001 cadence, with matching rational video PTS. “Poke.com” starts the editorial end hold at frame 1215. Codec variation in the source prevents an exact decoded-hash hold measurement. All-frame mean RGB MAE was 3.96269 for the archived GSAP and 4.00115 for this release. The same-machine uncorrected replay was 4.00269. The source has softer labels and a lighter-weight check than the reconstruction. The full film retains inherited geometry and type differences. [Native metrics](evidence/full-film-metrics.json)
- **Scoped change.** Evaluated scene markup matches on all 1,271 frames outside 633–644. The two independent Chromium captures have 849 byte-identical outside frames. The highest outside per-frame mean error was 0.047 on the 0–255 scale. The checkmark ROI changed by over 34 mean RGB levels at onset, with less than 0.001 mean error outside the ROI on that frame. [Markup scope](evidence/markup-scope.json) · [Capture differences](evidence/poke-native-controls.json)
- **Independent sound.** The existing Kenney CC0 click moved from sample 1,033,032 to 1,013,813 at 48 kHz. The muxed AAC matched the click at the new sample, with 0.991 correlation after subtracting the independently authored music bed. The old slot's best correlation was 0.077. Other UI samples outside the two cue spans matched. Final true peak measured −6.73 dBTP. The verdict is sample-based. [Cue and AAC report](evidence/audio.json)
- **First and final.** First complete work used the frozen acceptance export as the known-defect baseline. The fresh same-machine baseline took 105.9 seconds for picture and the corrected capture took 112.8 seconds. The work used a baseline checkpoint, a six-frame diagnostic pass, and a separate two-frame editability pass, plus the two full GSAP captures. The final audio required two additional verification iterations for MP4 edit-list timescale and the click-matching window. No separate reviewer time was recorded for the corrected artifact. This was a known-defect repair.
