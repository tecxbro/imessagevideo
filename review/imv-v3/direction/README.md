# The Moon Cue

A 15-second Keiki launch film about the customer who needs an answer while a
show is already in progress. The demonstration depicts a documented customer
text and agent reply on iMessage in an authored scenario.

- [Finished film with Sound’s mix](the-moon-cue.mp4) and [editable sound project](sound/README.md)
- [Editable picture source and render instructions](../../../skill/imessage-motion-recreation/direction/film/README.md)
- [Direction skill](../../../skill/imessage-motion-recreation/direction/SKILL.md) and [ten optional film studies](../../../skill/imessage-motion-recreation/direction/studies/README.md)
- [Original rough cut](rough.mp4) and [locked silent picture](locked.mp4)
- [Revision evidence](REVISION.md), [Keiki claim record](CLAIMS.md) and [source audit](SOURCES.md)
- [Picture event map](locked.events.json) and [independent send landmark check](send-landmark-result.json)

Picture is H.264, 960 × 540, 24/1 fps and exactly 360 frames. Both silent
exports decoded in full. In an isolated directory, exporting only the film
source, pinned UI adapter and base Pillow renderer reproduced the locked
MP4 and map byte for byte.

```sh
sha256sum -c rough.sha256
sha256sum -c locked.sha256
sha256sum -c final.sha256
ffmpeg -v error -xerror -i the-moon-cue.mp4 -f null -
```
