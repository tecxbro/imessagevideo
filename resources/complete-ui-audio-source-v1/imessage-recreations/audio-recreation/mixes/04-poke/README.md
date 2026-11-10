# 04-poke: new audio mix

`full_mix.flac` is the lossless 48 kHz stereo PCM24 master. `music.flac` and `sfx.flac` are matching stems, with the same final gain and fade; their sum matches within independent 24-bit quantization. Matching M4A files are compact listening copies. The three listening files share an additional 0.000 dB codec-headroom adjustment; SFX is never independently loudness-normalized.

Inputs: newly generated text-only AI music and original procedural synthesis only. No reference soundtrack samples were read by the mixer. The optional cue sheet contributes timing/context metadata, not audio. This recipe chooses 18 quiet accents and does not expand typing/scroll categories into beat patterns.

Exact picture span: 2054853 samples at 48 kHz (42.809437500 seconds). Integrated loudness / true peak of the actual FLAC master: -16.0 LUFS / -4.04 dBTP. Music duck depth never exceeds 1.00 dB.

Reproduce: `python audio-recreation/scripts/render_mix.py --id 04-poke --config audio-recreation/mixes/04-poke/mix-config.snapshot.json` from the project root. `mix-report.json` pins every input, code/recipe hash, selected event, gain, sample count and measured export; the exact mixer source is retained as `render_mix.source.py.txt`. The mixer runs FFmpeg loudnorm measurements and uses a common static gain; it reports any true-peak-limited deviation from the -16 LUFS target.
