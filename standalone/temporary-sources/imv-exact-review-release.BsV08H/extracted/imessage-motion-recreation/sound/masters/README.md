# Silent-master sound comparison

The example is a stand-in for the Recreation handoff. It scores a 200-frame excerpt of the restored Poke Pillow master, including the restaurant sheet, the choice of Zareen’s, and the arrival of its selection card. Source frames 514 through 713 keep their native 30000/1001 cadence in the excerpt. The excerpt starts at frame zero and lasts 1001/150 seconds.

| Decoded picture event | Excerpt frame | Master frame | Selected sound |
|---|---:|---:|---|
| Title of the restaurant sheet first appears | 61 | 575 | In treatment 01 a sound with a soft breath and resonant body prepares the visual change, with peak impact 12 ms early. |
| Third-row blue check first fills | 131 | 645 | In both treatments one short touch marks the viewer’s decision, with peak impact 18 ms after the frame. |
| Selection card first enters from below | 173 | 687 | In treatment 01 a descending pair of short resonances marks the handoff, with first peak impact 12 ms after the frame. |

Treatment 01 adds quiet pitched atmosphere from the map to the reading hold. The atmosphere fades before the choice, and the sheet closure plays in silence. An alternative with only the physical choice helps evaluate whether the list and result carry their own emphasis. Treatment 02 gives both passages to silence. The touch asset and gain are equal across treatments.

The score distinguishes three samples for each effect. The WAV starts at the rendered placement. The onset marker comes from the first 5 ms RMS window to exceed 20% of its peak. The impact marker is the center of the strongest first-hit 5 ms RMS window. These markers are measurements of the authored waveform. Human listening and a preference between the treatments are pending.

## Rebuild and verify

From the checkout root, install the sound requirements and use FFmpeg and ffprobe on PATH.

```bash
S=skill/imessage-motion-recreation/sound
V=review/imv-v3/sound/masters
python3 "$S/masters/synthesize.py" /tmp/poke-sound-assets
for treatment in 01 02; do
  plan="$S/masters/treatment-$treatment.json"
  out="/tmp/poke-treatment-$treatment"
  python3 "$S/sound.py" mix "$plan" "$V/poke-picture.mp4" "$out"
  python3 "$S/sound.py" verify "$plan" "$V/poke-picture.mp4" "$out/mix.mp4" "$out/manifest.json"
done
```

The plans use the checked-in one-shots for exact source identity. The scratch synth command regenerates those assets for editing. The mixer writes full-length dialogue, music, atmosphere and effects stems, a float WAV master, a muxed MP4 and a manifest with the exact picture, plan, source and output hashes. The review retains the non-empty stems.

To derive the silent excerpt again after restoring the library with `python3 tools/sync_library.py`, run:

```bash
source=resources/silent-picture-masters-v1/imessage-recreations/outputs/04-poke/pillow.mp4
ffmpeg -v error -threads 4 -i "$source" -an \
  -vf 'trim=start_frame=514:end_frame=714,setpts=PTS-STARTPTS' \
  -r 30000/1001 -fps_mode cfr -c:v libx264 -preset fast -crf 15 \
  -pix_fmt yuv420p -threads 4 -movflags +faststart /tmp/poke-picture.mp4
```

Frame numbers come from the encoded review excerpt. Its first and last native presentation timestamps are 0 and 199199/30000 seconds. The final frame is displayed for one more frame interval.

## Source inventory

`inventory.py` probes the original references, accepted reconstruction exports and silent masters for all six films. It also probes the prepared independent effects and the historical Poke soundtrack files in the restored audio archive. The manifest describes the intended media role. ffprobe records stream topology, codec and timing. The Linq original has a data stream in addition to picture and its reference soundtrack.

```bash
python3 skill/imessage-motion-recreation/sound/masters/inventory.py > /tmp/library-inventory.json
```

All four audible assets in the comparison use `synthesize.py` with fixed seeds and a 48 kHz stereo clock. The sample content is original oscillators, modal decays and band-limited noise. The template crops come from the decoded review picture. The old Poke audio and independent CC0 packs served as source inventory. The CC0 pack credits and exact license records are in [the legacy license notes](../../references/ui-audio/audio-recreation/library/LICENSES.md).

## Five renderer check

With the existing renderer dependencies, use the Python for Pillow/CairoSVG with the sound requirements installed. Honor the browser and fonts used by the renderer setup.

```bash
python3 skill/imessage-motion-recreation/sound/masters/check_renderers.py /tmp/imv-sound-renderers
```

The runner invokes each production renderer, makes an MP4, and resolves the first frame when the amber rectangle reaches a narrow pixel ROI. It requires frame 12 and sample 24000 on all five. The verification reads each final mux and checks the original touch cue’s measured alignment at a deliberate 12 ms lag.

## Motion handoff check

Use the original Motion branch picture from commit `de04deb3071ccd9c674f95a4267e2843ed4e3bf0` in the checkout or an extracted review folder.

```bash
python3 skill/imessage-motion-recreation/sound/sound.py resolve \
  skill/imessage-motion-recreation/sound/masters/motion-handoff.landmarks.json \
  /path/to/conversation-handoff.mp4
```

The original Motion review file SHA-256 is `2f32163de606611fa425e88c997c9b42ea33e6fe7ef345c55f90150baf92df24`. The blue outgoing bubble appears at frame 32/sample 51200. The gray incoming bubble appears at frame 51/sample 81600. Both come from decoded transitions at 30/1.

## Clone iMessage UI handoff check

Use the exact Clone iMessage UI review movie from commit `9beea91a43c0b24fb7a2061ea54071d426f621c6`.

```bash
python3 skill/imessage-motion-recreation/sound/sound.py resolve \
  skill/imessage-motion-recreation/sound/masters/ui-handoff.landmarks.json \
  /path/to/station-pillow.mp4
```

The review movie is 402×874 and 136 frames at 24/1. It fully decoded as one silent picture stream and matched SHA-256 `692004a46cf233198b2ebfc19b583a37a3f5c0057eb9e40fcb9b0dd070a8381b`. The decoded crops identify the first visible `station.send` at frame 12/sample 24000, `station.reply` at 44/88000, and `station.love` at 64/128000.
