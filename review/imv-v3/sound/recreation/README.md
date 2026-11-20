# Recreation sound handoff

The exact silent picture and checked audio export are in each cut folder. Play `final/mix.mp4` for the scored locked recreation and `edited/mix.mp4` for the recut. The original sounds and template crops are in `assets/`. The `cue-stems/` WAVs start at picture zero and sum exactly to the master. Keep them on separate tracks to adjust any interaction. Human listening is pending.

| Cut | Exact picture SHA-256 | Muxed export SHA-256 |
|---|---|---|
| Final | `eca99d87a9b8e92a5ca31c2b16bff5ba42f23ba7236ab8182c08ce9e71d81c8f` | `8435575bb2546e893389e4e3469ff848e69856c01f6e3a338d794b66f3c10cbf` |
| Edited | `6e9cdc57f6e3e4b178955e86aa23c9e7c55596ef16c470c0cae48f945df92b8f` | `9bc9687aaa516f83066b9293888192ae0d4bf05548bcb14de5f69f6b5e954def` |

Both MP4s pass the decoded export check. Each has 120 H.264 picture frames at 30/1 and a four-second 48 kHz stereo AAC audio stream. The encoded mux preserves the original picture packets and presentation timestamps. Estimated true peak is −13.02 dBTP in both. There are zero audio presentation discontinuities, measured energy dropouts or material differences against the respective PCM. All four audio impacts are within 0.021 ms of their intended offsets relative to the decoded picture.

The edited picture moves the seat check from frame 74 to 69 and changes the outgoing request to Northgate. The same plan moves the selected cue 8,000 samples earlier and retains its intended 9 ms lag. The other three anchors and effect placements stay at their measured samples.

`stale-pcm.check.json` documents a control made by muxing the final PCM against the edited picture. The control used that same stale PCM as its comparison wave and valid control file hashes, so waveform comparison alone passed. The visual anchor still exposed the seat latch, 166.688 ms late against picture. The report rejects that control.

The consecutive-frame sheet shows the final picture at frames 29–32, 55–58, 73–76 and 88–91, from top to bottom. The request, picker, seat check and receipt first appear in column two.

## Source inventory

All source files below are from Recreation’s commit `f0d65672e022ff1c827bd12bf1470445b85196d5`.

| Source from `review/imv-v3/recreate/train/` | Inspected streams and role |
|---|---|
| `reference.mp4` | H.264 with 48 kHz mono AAC, four seconds. Original reference film with its own synthesized tone soundtrack. SHA-256 `8f73c68dd6ede5b0ff1882085c549f62653f50659ed0c9473a9e33da7d2c9a22`. |
| `first.mp4` | H.264 silent first pass. Purple seat check is first filled four frames after the locked handoff’s event. SHA-256 `fbc5087e12781443be9fb1eddae4bdea792ab76faef0bb629772b6969853f352`. |
| `final.mp4` | H.264 silent locked recreation. Exact bytes copied to `final/picture.mp4`. |
| `edited.mp4` | H.264 silent alternate edit. Exact bytes copied to `edited/picture.mp4`. |

The historical reference music-free tone cues come from Recreation’s `recreate/example/reference/render.mjs`. The new source effects are synthesized independently from the sound recipe. The new mix leaves intentional silence between visible actions and through the held ending. See [the train score recipe](../../../../skill/imessage-motion-recreation/sound/recreation/README.md) for rebuilding or adjusting it.

Run `sha256sum -c SHA256SUMS` inside this folder to verify the exact review files.
