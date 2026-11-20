# Blind revision of the selected lock mix

After the selected lock mix passed, a fresh agent received the Sound skill in a dedicated input directory, both silent masters, and the previous editable score with source assets. Its conversation contained no moved event, frame hint or revised event map. The task limited its inputs to that directory. It diagnosed and remapped the cut independently.

The agent found the audience movement at f275, five frames after its f270 position in the approved picture. The other nine decoded landmarks stayed on their original frames. Both cuts contain 360 frames at 24 fps. The [audience frame strip](evidence/audience-detail.png) shows both boundaries. The audience cue's impact moved from sample 542,880 to 552,880 while retaining the intended +2,880 samples (+60 ms) after the visible lean. Its estimated error in decoded AAC is 0.000 ms. All eight event-bound cues and both silent holds passed. Human listening is pending.

The [fresh-agent MP4](export/mix.mp4) is SHA-256 `0c7a28cc504920a9ca91752f3cfe66d8b58b0e5de071008690d494295607397a`. The [revised silent master](picture.mp4) is SHA-256 `5c5c72399375edbf6075846531e50864abc4abf9f2171d338f4b061697383db8`. The [fresh-agent verification](export/verify.json) covers that exact pair. The final MP4, PCM master, four stems and original [editable locked plan](../locked/a.json) reproduce the remap.

The [stale-audio control](stale.verify.json) pairs the approved locked PCM with the revised master and updates its delivery hashes. It fails with the audience impact at −208.333 ms against the revised picture and authored delay.

From the repository root:

```sh
S=skill/imessage-motion-recreation/sound
D=review/imv-v3/sound/direction
python3 "$S/sound.py" verify "$D/locked/a.json" "$D/locked-reuse/picture.mp4" \
  "$D/locked-reuse/export/mix.mp4" "$D/locked-reuse/export/manifest.json"
(cd "$D/locked-reuse" && sha256sum -c SHA256SUMS)
```
