# Sidehoe editable project

The verified build uses Python 3.15.2, Pillow 13.0.0, NumPy 2.5.5, FFmpeg
with libx264, and macOS Apple Color Emoji. The system emoji font stays
local. Set `SIDEHOE_EMOJI_FONT` to an available compatible font path
when the default macOS path differs. Run from the project directory.

```sh
python3.15 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
PYTHON=.venv/bin/python bash export.sh exports /tmp/sidehoe-png
```

`scene.json` holds copy, independently drawn portrait parameters, palette, zero-based events, camera and cursor keyframes, appointment time slots, and score notes. y points downward. Stage geometry is 1000 × 1000, doubled on encode. Frame 0 starts at zero and 25 fps is exact. Tracks linearly interpolate between absolute frame indices. The Pillow stage redraws each frame from its absolute index. Change a string or track entry and render with `render.py --cache … --frames START:END` for a partial preview. `export.sh … --reuse-cache` re-encodes an already complete cache.

`render.py` draws the UI, plates and choreography. `artwork.py` provides independently authored app tiles, badges, inline pictograms and portrait placements. The selected generated heads are individual transparent PNGs under `assets/portraits`. Their color disks, scale, positions, masks and animation remain editable. `sound.py` synthesizes editable stereo score and Foley separately, plus the mix and the frame-to-audio-sample event map. The bundled source, font and head sprites are the render inputs.

- Font. Inter variable font by Rasmus Andersson and contributors, SIL Open Font License 1.1. `assets/Inter-OFL.txt` contains the license. [Upstream font directory](https://github.com/google/fonts/tree/main/ofl/inter)
- Other visuals. Independently authored Pillow geometry for the hardware, interface and brand mark. Generated portrait sprites are guided by the supplied character reference. The reference film and evidence are separate from this project.
- Audio. Original synthesizer score and procedural Foley from `sound.py`. Event timing follows the observed visual beats. No audio samples are loaded.

The follow-up cursor uses `followPointerStage` from f670 through its
exit. Position, footprint, defocus and opacity are in stage coordinates.
`followYesRegistration` holds the separate control in phone coordinates.
`handsetRailLight` controls the bevel reflection, exit taper and softness.
`calendarTileTreatment` controls the blue tile's stage offset, coverage,
material blend, blur and aspect ratio. Procedural surfaces are in
`treatments.py`. The other motion keys remain editable in `scene.json`.

The reply and suggestion have separate stage-coordinate tracks as the interface detaches. The calendar marker and right grid edge are independent tracks. The portrait disks and app tiles have individual poses. Each closing word has its own visible ink box and opacity. The two title washes use editable field tracks with center, falloff, shear and RGB amount for each light. `scene.json` records the measured landmarks and the interpolation used in the render.

The [calibration report](../README.md) documents the source and final
comparison.
