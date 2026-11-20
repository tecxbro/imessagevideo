# The Moon Cue, rough-cut sound review

Play [A](a/mix.mp4) and [B](b/mix.mp4) in either order. For a blind audition send just those MP4s. Listen across the unanswered question, the trip from the reply to the tin, and the moment the stage moon becomes legible. Mark the time where you feel the story move and name anything that steals attention from the text or prop. Human audition is pending.

Both 15-second mixes use the same picture bytes and the same basic Foley. They leave a clean pause after the send, anchor the tin and paper to visible actions, and suggest a small audience settling after the rabbit relaxes. The variants differ only in how they carry the wait and release. The plans record their exact materials and intended offsets. The test files have integrated loudness within 0.2 LU (A −30.3 LUFS, B −30.1 LUFS). The measured true peaks are −4.0 dBTP and −4.3 dBTP.

The silent picture and event map were supplied by Direction at `2873e04`. The master SHA-256 is `573509992ed7d0715bee09477e75a3f993b79c204ae490e1b43556e3760b6d3b`. Review the [frame evidence](frame-evidence.png), [picture notes](PICTURE.md) and the [A](a/verify.json) and [B](b/verify.json) reports. Both verify with zero audio-clock discontinuity, no clipping, and no detected energy dropout. A passes eight event-bound cues and B passes nine. The contract's authored moon entry at f259 happens before the crescent is legible in the encoded picture at f266. The sound intended to underline recognition uses f266.

From this folder `sha256sum -c SHA256SUMS` checks all review assets. From the repository root:

```sh
S=skill/imessage-motion-recreation/sound
D=review/imv-v3/sound/direction/rough
python3 "$S/direction/synthesize.py" review/imv-v3/sound/direction/assets
python3 "$S/direction/arrange.py" "$D"
python3 "$S/sound.py" mix "$D/a.json" "$D/picture.mp4" /tmp/moon-a
python3 "$S/sound.py" verify "$D/a.json" "$D/picture.mp4" /tmp/moon-a/mix.mp4 /tmp/moon-a/manifest.json
python3 "$S/sound.py" verify "$D/b.json" "$D/picture.mp4" "$D/b/mix.mp4" "$D/b/manifest.json"
```
