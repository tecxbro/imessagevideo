# Blind timing revision

A fresh agent received the Sound skill and runtime, the original rough picture and score with assets, and a newly named silent cut. It received no timing map or change list. It compared the pictures, remapped the mix and verified the decoded export. The revised master SHA-256 is `a889b945750d72442040bbde05b7eea39cbb9236269ee1b8e8c15d62b0983f21`.

The agent found the readable crescent at f274 (previously f266), the rabbit release at f289 (previously f281), and the settled end card at f329 (previously f321). Seven earlier landmarks stayed put. The release music, cloth and audience exhale all moved 16,000 samples later while retaining their intended offsets. All nine picture-bound cues passed. The [timing comparison](timing-comparison.json), [consecutive decoded frames](stage-boundaries.png) and [independent verification](independent-verify.json) retain the evidence.

The fresh agent's stale-audio control found a near-timing musical pattern that the old matcher scored at 0.915. The agent raised the release fingerprint's correlation threshold to 0.95 and verified that the clean exports still passed. The reusable checker now chooses the strongest valid signature across the search window before measuring its timing. An independent rerun with the unmodified rough plan rejects all three stale cues at −333.333 ms. See the [new checker’s stale control](stale-current-verifier.json).

The test used the 15-second Direction rough as its starting point. Direction's separate editorial lock has its own picture and evidence. Human audition is pending.

From the repository root, reproduce the positive timing revision:

```sh
S=skill/imessage-motion-recreation/sound
D=review/imv-v3/sound/direction
python3 "$S/sound.py" mix "$D/rough/b.json" "$D/blind/picture.mp4" /tmp/moon-blind
python3 "$S/sound.py" verify "$D/rough/b.json" "$D/blind/picture.mp4" /tmp/moon-blind/mix.mp4 /tmp/moon-blind/manifest.json
```
