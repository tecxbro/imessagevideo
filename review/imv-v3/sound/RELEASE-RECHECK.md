# Sound package replay

The extracted skill passed all six sync cases. The correct and remapped exports measured 0.000 ms error against the +120-sample offset. The late and jointly shifted cues measured +200.000 ms. The missing cue went undetected by the waveform match. The stale fixture cue measured −250.000 ms on the revised picture. The encoded quality run passed the intact control and rejected the removed overlay, dropout, clipping, short audio and discontinuous timestamps.

The prior [cold retime](direction/locked-reuse/README.md) retains its original evidence. The revised picture SHA-256 is `5c5c72399375edbf6075846531e50864abc4abf9f2171d338f4b061697383db8` and its mux SHA-256 is `0c7a28cc504920a9ca91752f3cfe66d8b58b0e5de071008690d494295607397a`. The audience action resolves at f275, its new impact at sample 552,880. The authored +2,880-sample lag remains 60 ms. Decoded AAC measures 0.000 ms error on the remap and −208.333 ms on the stale mix. Both reports matched the checked-in JSON byte for byte on the replay runtime. Human audition is pending.

## Reproduce from a clean extraction

Run from the repository root at the Sound handoff commit. The checkout supplies the package and exact review assets. The tests run from the new directory.

```sh
S=skill/imessage-motion-recreation/sound
D=review/imv-v3/sound/direction
work=$(mktemp -d)
git archive HEAD "$S" "$D/locked" "$D/locked-reuse" "$D/assets" | tar -x -C "$work"
cd "$work"
python3 "$S/example.py" results/sync
python3 "$S/quality_controls.py" results/quality
(cd "$D/locked-reuse" && sha256sum -c SHA256SUMS)
python3 "$S/sound.py" verify "$D/locked/a.json" "$D/locked-reuse/picture.mp4" \
  "$D/locked-reuse/export/mix.mp4" "$D/locked-reuse/export/manifest.json" \
  --report results/retime.json
control_status=0
python3 "$S/retime_control.py" "$D/locked/a.json" "$D/locked-reuse/picture.mp4" \
  "$D/locked/a/manifest.json" results/stale || control_status=$?
test "$control_status" -eq 1
```

The stale control uses the previously approved WAV and the exact revised picture. The MP4, copied WAV and decoded report are written to `results/stale`. Confirm the `audience-release` cue is reported early, then compare against the cue in `results/retime.json`.
