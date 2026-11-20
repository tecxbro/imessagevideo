# Poke sound comparison

Play `treatment-01/mix.mp4` and `treatment-02/mix.mp4`. Share only the two numbered MP4s for an unlabeled audition. Ask which version makes the restaurant choice read clearly and whether the card benefits from a sound. Human listening is pending.

The common silent `poke-picture.mp4` was trimmed from the local accepted Pillow master. Its SHA-256 is `18ce67a814ef24e4ac9371134e3e5e984f668c4a992ea830f05ac9f2ab15861d`. The exact source master hash is `3b2e0e8be9ee2ffdd13127e1d3e4495eec53d5e40ef8fdd039a7f395b693445c`. The contact sheet and frame sequences show the picture events around cut frames 61, 131 and 173. The Motion handoff image uses ordered frames 30, 31, 32, 33 (top) and 50, 51, 52, 53 (bottom).

Each treatment has a float PCM `mix.wav`, its non-empty stems, the picture-bound `manifest.json` and decoded `check.json`. Both pass their cue and silence checks. Decoded estimated true peak is −13.12 dBTP for both, and audio presentation shows zero timestamp discontinuities. The same choice impact follows the blue check by 18.021 ms in both exports. Treatment 01’s opening impact leads its frame by 12 ms. Its card entry impact follows by 11.958 ms. These numbers measure the waveform markers and their frame timestamps.

Verify the committed files with `sha256sum -c SHA256SUMS` from this folder. See [the sound example recipe](../../../../skill/imessage-motion-recreation/sound/masters/README.md) for reproduction and renderer checks.

The Clone iMessage UI handoff sheet shows frames 11–14, 43–46 and 63–66 in order across its three rows. The send, reply and Love badge first appear in the second image of each row. The five-renderer result records frame 12/sample 24000 and a passing 12 ms audio lag for every newly rendered picture.
