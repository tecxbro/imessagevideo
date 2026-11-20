# Recreation's owner-supplied Train Options retime

Recreation handed off the silent revision and its checksum at `3fa0021` without a change list, frame number or event map. The 120-frame, 30 fps silent master decoded in full and its SHA-256 matched `f555d505a3298befe18332c90b9fde7f3d3cbf8255534a4149fdbbe862bc16c6`. This uses the approved Train score and is separate from Recreation's reserved unseen-film run.

The [adjacent decoded frames](seat-selection-frames.png) show the seat check mark moving from f74 to f84. The request, drawer and receipt anchors remain at f30, f56 and f89. The original [editable plan](../../../../../skill/imessage-motion-recreation/sound/recreation/train.plan.json) resolved all four actions directly from the revised picture.

| Measurement | Approved | Revised |
| --- | ---: | ---: |
| Seat picture anchor | 118,400 samples | 134,400 samples |
| Authored impact offset | +432 samples | +432 samples |
| Expected cue impact | 118,832 samples | 134,832 samples |

The [remapped mux](remapped/mix.mp4) matches the revised silent master's H.264 packets and presentation times. Its decoded seat impact calculates to sample 134,833, an error of +0.021 ms, and all four cues pass. The peak estimate is −13.01 dBTP. The [stale mux](stale.mp4) uses the approved PCM against the delayed picture action. Its impact lands at sample 118,833 and fails 333.312 ms early. The [decoded pass](remapped/verify.json) and [stale rejection](stale.verify.json) record the measurements. Human audition is pending.

- Remapped MP4 SHA-256 `92c332530a67c1d60e94ed7ff07dd455b2c00911b510fab40249b2d3d7f84365`
- Stale MP4 SHA-256 `c7acb0ffa962fd1281fa9cffb2fe56fb1adf317d2787be765d80209a4d09cfc0`
- Editable delivery includes the [PCM master](remapped/mix.wav), [individual cue stems](remapped/cue-stems/), [effects stem](remapped/effects.wav), [binding manifest](remapped/manifest.json) and the original [source asset inventory](../README.md).

## Reproduce from the repository root

```sh
S=skill/imessage-motion-recreation/sound
D=review/imv-v3/sound/recreation
N="$D/owner-retime"
work=$(mktemp -d)
(cd "$N" && sha256sum -c SHA256SUMS)
python3 "$S/sound.py" mix "$S/recreation/train.plan.json" "$N/revised-silent.mp4" "$work/remapped"
PYTHONPATH="$S" python3 -m recreation.render_stems "$S/recreation/train.plan.json" "$work/remapped"
python3 "$S/sound.py" verify "$S/recreation/train.plan.json" "$N/revised-silent.mp4" \
  "$work/remapped/mix.mp4" "$work/remapped/manifest.json" --report "$work/remapped/verify.json"
status=0
python3 "$S/retime_control.py" "$S/recreation/train.plan.json" "$N/revised-silent.mp4" \
  "$D/final/manifest.json" "$work/stale" || status=$?
test "$status" -eq 1
```
