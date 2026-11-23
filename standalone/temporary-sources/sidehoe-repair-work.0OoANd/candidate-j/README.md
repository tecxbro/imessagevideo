# Sidehoe editable project

Requires Python 3.11+, Pillow, NumPy, and FFmpeg with libx264. Run the following commands from the project directory.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
PYTHON=.venv/bin/python ./export.sh exports /tmp/sidehoe-png
```

`scene.json` holds copy, independently drawn portrait parameters, palette, zero-based events, camera and cursor keyframes, appointment time slots, and score notes. y points downward. Stage geometry is 1000 × 1000, doubled on encode. Frame 0 starts at zero and 25 fps is exact. Tracks linearly interpolate between absolute frame indices. The Pillow stage redraws each frame from its absolute index. Change a string or track entry and render with `render.py --cache … --frames START:END` for a partial preview. `export.sh … --reuse-cache` re-encodes an already complete cache.

`render.py` draws the UI, plates and choreography. `artwork.py` provides independently authored app tiles, badges, inline pictograms and portrait placements. The selected generated heads are individual transparent PNGs under `assets/portraits`. Their color disks, scale, positions, masks and animation remain editable. `sound.py` synthesizes editable stereo score and Foley separately, plus the mix and the frame-to-audio-sample event map. The bundled source, font and head sprites are the render inputs.

- Font. Inter variable font by Rasmus Andersson and contributors, SIL Open Font License 1.1. `assets/Inter-OFL.txt` contains the license. [Upstream font directory](https://github.com/google/fonts/tree/main/ofl/inter)
- Other visuals. Independently authored Pillow geometry for the hardware, interface and brand mark. Generated portrait sprites are guided by the supplied character reference. The reference film and evidence are separate from this project.
- Audio. Original synthesizer score and procedural Foley from `sound.py`. Event timing follows the observed visual beats. No audio samples are loaded.

The revised follow-up cursor uses `followContact.yesRect`, a plate y offset track in stage units, and frame offsets from the `follow.yes-contact` event. The cursor's final approach and hold are relative to the Yes control in phone coordinates.

The detached reply and suggestion have separate stage-coordinate tracks. The calendar marker and right grid edge are independent tracks. The two title washes use editable field tracks with center, falloff, shear and RGB amount for each light. `scene.json` records both measured timing landmarks and authored interpolation.
