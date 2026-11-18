# Codex sound handoff

## Watch first

- [Pinch Hit final mix](https://github.com/tecxbro/imessagevideo/blob/d900149ef451b3c9583c11fc878155f370fbf445/sound-trial/pinch/final/mix.mp4) · [MP4 download](https://github.com/tecxbro/imessagevideo/raw/d900149ef451b3c9583c11fc878155f370fbf445/sound-trial/pinch/final/mix.mp4)
- [Timing trial A](https://github.com/tecxbro/imessagevideo/blob/d900149ef451b3c9583c11fc878155f370fbf445/sound-trial/pinch/early/mix.mp4) · [Timing trial B](https://github.com/tecxbro/imessagevideo/blob/d900149ef451b3c9583c11fc878155f370fbf445/sound-trial/pinch/hold-test/mix.mp4)
- [Poke V04](https://github.com/tecxbro/imessagevideo/blob/d900149ef451b3c9583c11fc878155f370fbf445/sound-trial/auditions/V04.mp4) · [Poke V17](https://github.com/tecxbro/imessagevideo/blob/d900149ef451b3c9583c11fc878155f370fbf445/sound-trial/auditions/V17.mp4)

For the cold view, describe where the wait starts to drag, what cues the change in situation, and when the pencil mark feels finished. For the Poke pair, describe how the chooser, selection and Maps reveal feel in each. Record playback equipment and level if known.

## Locked versions and verification

- Tested sound commit `d900149ef451b3c9583c11fc878155f370fbf445`. Clean MP4 SHA-256 `541c2d6d73029d25adbfbdc2286c53c56a7f204e82d44210abb5a87319ba9eba`.
- Final picture is the director’s [](https://github.com/tecxbro/imessagevideo/blob/19d50dc26e4e8e2f2875affdb3b2c7b2ca6861be/trials/pinch-hit/films/final-picture.mp4) from commit . SHA-256 . 1280×720, 576 frames, 24 fps.
- Timing trial A uses [early picture ](https://github.com/tecxbro/imessagevideo/blob/3324065c5386952c1db87a77925a5df9c1d81dff/trials/pinch-hit/films/early.mp4). Trial B uses [hold-test picture ](https://github.com/tecxbro/imessagevideo/blob/19d50dc26e4e8e2f2875affdb3b2c7b2ca6861be/trials/pinch-hit/films/hold-test.mp4).
- [Editable PCM master and stems](https://github.com/tecxbro/imessagevideo/tree/d900149ef451b3c9583c11fc878155f370fbf445/sound-trial/pinch/final) · [Cue data, provenance and rerender commands](https://github.com/tecxbro/imessagevideo/blob/d900149ef451b3c9583c11fc878155f370fbf445/sound-trial/README.md) · [Clean export report](https://github.com/tecxbro/imessagevideo/blob/d900149ef451b3c9583c11fc878155f370fbf445/sound-trial/reports/pinch-final.json).
- For export QC after the cold view, [planted MP4](https://github.com/tecxbro/imessagevideo/blob/d900149ef451b3c9583c11fc878155f370fbf445/sound-trial/pinch/final-faults/mix.mp4) has SHA-256 `7363f8b2b915380fdd517bc3d2fb2474f24721c0271ba7e7536408d42c2c8425`. The [repeatable check](https://github.com/tecxbro/imessagevideo/blob/d900149ef451b3c9583c11fc878155f370fbf445/sound-trial/check_export.py) finds a 208.375 ms late send and a missing pencil-contact cue in the decoded AAC. The [fault report](https://github.com/tecxbro/imessagevideo/blob/d900149ef451b3c9583c11fc878155f370fbf445/sound-trial/reports/pinch-final-faults.json) records both. The clean file retains exact picture packets and timing and passes both quiet windows at −27.1 LUFS and −5.0 dBTP.
