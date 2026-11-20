# The Moon Cue, locked sound delivery

[Play the selected mix](a/mix.mp4) · [Edit the cues](a.json) · [Read the export check](a/verify.json) · [Check the picture](PICTURE.md)

Treatment A carries the film with a seated room and physical sounds. Direction chose it from the rough treatments and their measurements. Around the reply, the room remains nearly still. The locked edit shortens the reply-to-tin wait and gives the eye a red object that survives the change of viewpoint. The wait bed starts earlier relative to the tin cut and is quieter than in the rough, so it recedes by the metal contact. The tin and paper lead the physical passage. The audience's visible shift now has its own sound anchor rather than sharing the rabbit's.

| Picture point | Rough frame | Locked frame | Sound decision |
| --- | ---: | ---: | --- |
| Outgoing bubble | 84 | 84 | Impact follows the bubble exactly. |
| Incoming bubble | 113 | 113 | Impact follows by 12 ms. The preceding hold remains quiet. |
| Red tin fills the new shot | 181 | 153 | The room tone leads in and tapers by the lid. |
| Lid separates | 197 | 165 | The metal cue reaches its impact at release. |
| Paper first lifts | 218 | 189 | Paper impact follows by 6 ms. |
| Return to stage | 246 | 212 | A soft audience bed leads the cut by 85 ms. |
| Crescent reads at the stage edge | 266 | 218 | The edge first appears at f216. A leaves this beat carried by the picture and room. |
| Rabbit turns its ears | 281 | 254 | A quiet cloth cue marks the gesture. |
| Audience leans | — | 270 | The audience exhale crests 60 ms after the visual turn. |

Human listening is pending. The sync, peak and quiet-range observations come from the encoded export. The 15-second delivery uses the exact locked H.264 picture SHA-256 `838fbb35fa9741cb373875d2c6f88536c2dd46ab6abc39978e47a1d7f978cec7`. Its bound manifest contains the source audio, stem, PCM master and encoded MP4 hashes. All eight action cues pass the decoded picture and audio check at 0.000 ms error against their authored offsets. The mix measures −29.7 LUFS and −4.14 dBTP, with no PTS gaps or energy dropout. The reply hold and end hold decode to digital silence.

The [original rough A](../rough/a/mix.mp4) and [locked A](a/mix.mp4) let the filmmaker compare both cut timings with the same sound treatment. The [rough A/B comparison](../rough/README.md) documents the musical option. [Locked B](b/mix.mp4) uses [its own plan](b.json) and places the musical release 18 ms after the crescent reads in the locked cut.

## Reproduce the delivery

From the repository root:

```sh
S=skill/imessage-motion-recreation/sound
D=review/imv-v3/sound/direction/locked
python3 "$S/direction/synthesize.py" review/imv-v3/sound/direction/assets
python3 "$S/direction/arrange.py" "$D" --locked
python3 "$S/sound.py" mix "$D/a.json" "$D/picture.mp4" /tmp/moon-lock
python3 "$S/sound.py" verify "$D/a.json" "$D/picture.mp4" /tmp/moon-lock/mix.mp4 \
  /tmp/moon-lock/manifest.json --report /tmp/moon-lock/verify.json
(cd "$D" && sha256sum -c SHA256SUMS)
```

The four [stems](a/) are full-length 48 kHz stereo WAVs aligned at sample zero. The music and dialogue stems are silent in A. The effects, atmosphere, original source WAVs and cue plan are separately editable. The PCM mix is their sum.

The [fresh-agent reuse check](../locked-reuse/README.md) exercised the selected mix on another picture revision.
