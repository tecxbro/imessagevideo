# CC0 UI effects and real single-key recordings

This is a separate **licensed library bank**, not the project's original procedural synthesis bank. No reference-film sound samples are used. Selection uses source filenames, recording descriptions and signal checks; no human or model listening audition is claimed.

`manifest.json` pins the two archives, licenses/source pages, original member hashes, prepared hashes, processing and signal statistics. `download-collection.json` records the public download flows and archive capture. Original ZIPs remain in `archives/`; extracted sources and licenses remain in `sources/` and `licenses/`. No keyboard typing loops or preview bed were extracted or used.

The prepared bank contains25 Kenney UI candidates and12 real single-key variants. All are stereo48kHz PCM24 WAV, peak-normalized to−6dBFS, with silent endpoints, light attack de-clicking, smooth releases and DC removal. `validation.json` records actual export/API safety checks. `audition.mp3` plays every asset sequentially at−6dB relative to the prepared bank; `audition-index.csv` provides its times and labels. This is a listening aid, not a claim that it has been auditioned.

## Sources and distinction

| Source | Evidence | Asset kind |
| --- | --- | --- |
| [Kenney Interface Sounds](https://kenney.nl/assets/interface-sounds) | Original archive `License.txt` explicitly CC0, plus captured official page | Licensed UI effects. Their acoustic/synthetic production origin is not stated. |
| [unicaegames Keyboard Soundpack1](https://opengameart.org/content/keyboard-soundpack-1-typing-and-single-keystrokes) | Author listing explicitly CC0; included readme confirms free use | Actual Single Keys recordings, according to the author: Cherry KC1000, Shure SM7B, Izotope Neutron2. No physical key identity is assigned to numbered variants. |

Primary short UI IDs: `kenney_click_001`, `kenney_click_002`, `kenney_click_003`, `kenney_tick_001`, `kenney_tick_002`, `kenney_select_001`, `kenney_select_002`. Other click variants are available. Switch/toggle sounds can contain multiple transients; do not automatically use them as one tight tap.

Actual keyboard pool: `key_001`, `key_003`, `key_005`, `key_008`, `key_011`, `key_014`, `key_017`, `key_020`, `key_023`, `key_026`, `key_029`, `key_032`. Choose variants deterministically for actual visible typing events; do not turn every title or incoming AI response into keyboard sounds.

`drop`, `pluck`, `scroll`, `open/close`, `maximize/minimize`, glass and confirmation IDs are secondary candidates based on their supplied names. They are not certified as particular iMessage sends, arrivals or swipes. The existing separate `synthesis` bank remains an explicitly generated fallback for a custom message bubble or airy whoosh.

## API

```python
import sys
sys.path.insert(0, "/workspace/imessage-recreations/audio-recreation/scripts")
from library_bank import SAMPLE_RATE, render_asset, attack_peak_sample, write_wav

clip = render_asset("key_001", pitch=1.02, gain_db=-12, pan=-0.10)
peak_offset = attack_peak_sample(clip)
# To align its dominant early transient with an event at frame f / fps:
# clip_start = round(f / fps * SAMPLE_RATE) - peak_offset
write_wav("/path/to/key.wav", clip)
```

Returns NumPy `float32[samples,2]` at48kHz. Pitch0.5–2 uses bandlimited varispeed, so duration also changes. Pan−1–1 is left to right. The rendered result is jointly aligned to the−6dBFS bank peak after pitch/pan, then `gain_db` is applied; default−12dB gives about−18dBFS peak. Clipping requests are rejected. Same inputs produce identical samples; no randomness is introduced.

`attack_peak_sample` finds the dominant peak in the first80ms after significant activity. It is an explicit reproducible alignment proxy, not proof of which physical key-down/up action produced the sound. Manifest statistics also retain each global peak time, so a rising or double-transient candidate is distinguishable from a short click.

## CLI and reproduction

```sh
python audio-recreation/scripts/library_bank.py list --tag keyboard
python audio-recreation/scripts/library_bank.py render kenney_click_001 /tmp/click.wav --gain-db -14 --pan .1
python audio-recreation/scripts/library_bank.py validate
python audio-recreation/scripts/library_bank.py prepare
# Reacquire through the ordinary public free download flows if needed:
python audio-recreation/scripts/library_bank.py fetch
```

Requires NumPy, SciPy and FFmpeg. The manifest pins actual tool versions and preparation-code SHA. Preparation safely extracts regular files only, rejects traversal/symlink/special entries and bounds the entry count and expanded bytes. Raw archives preserve the unmodified source; prepared files disclose trim/processing separately. `steps.md` records the download and release-tail diagnosis.
