# 05-linq: new audio mix

`full_mix.flac` is the lossless 48 kHz stereo PCM24 master. `music.flac` and `sfx.flac` are matching stems, sharing the same final gain, fade and any linked master peak control; their sum matches within independent 24-bit quantization. Matching M4A files are compact listening copies. The three listening files share an additional 0.000 dB codec-headroom adjustment; SFX is never independently loudness-normalized.

Inputs: newly generated text-only AI music and original procedural synthesis only. No reference soundtrack samples were read by the mixer. The optional cue sheet contributes timing/context metadata, not audio. This recipe chooses 23 quiet accents and does not expand typing/scroll categories into beat patterns.

Exact picture span: 2332800 samples at 48 kHz (48.600000000 seconds). Integrated loudness / true peak of the actual FLAC master: -16.63 LUFS / -2.2 dBTP. Music duck depth never exceeds 1.20 dB.

Reproduce: `python audio-recreation/scripts/render_mix.py --id 05-linq --config audio-recreation/mixes/05-linq/mix-config.snapshot.json` from the project root. `mix-report.json` pins every input, code/recipe hash, selected event, gain, sample count and measured export; the exact mixer source is retained as `render_mix.source.py.txt`. FFmpeg loudnorm selects the common gain. Linked oversampled master peak control applied: **True**. It is used only when static peak-safe normalization misses the target by more than1LU, and applies the same detector/gain to music, SFX and their sum. The report records its exact filter, alignment and additivity checks.
