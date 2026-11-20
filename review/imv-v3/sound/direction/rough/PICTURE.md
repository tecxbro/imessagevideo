# The Moon Cue rough cut

Direction delivered the 960 × 540 silent picture master in commit `2873e043a37685031da680220e119cc4dd7ab9c2`. The MP4 has one H.264 video stream and 360 displayed frames at 24 fps, for 15 seconds. Its SHA-256 is `573509992ed7d0715bee09477e75a3f993b79c204ae490e1b43556e3760b6d3b`, matching Direction's receipt.

The frame strips show the decoded frames adjacent to each measured boundary. Teal boxes mark the measured patch on the detected frame. The four template PNGs are unscaled crops from this silent master. The landmark search windows use scene neighborhoods and allow the visible events to move within them. [Frame evidence](frame-evidence.png) · [Detector definitions](landmarks.json)

| Landmark | Frame | Picture time (s) | Visible boundary |
|---|---:|---:|---|
| `message.question.press` | 82 | 41/12 | The blue send circle shrinks around the arrow. |
| `message.question.send` | 84 | 7/2 | The question appears in a blue bubble. |
| `message.answer.receive` | 113 | 113/24 | The answer bubble appears below the question. |
| `prop.table.reveal` | 181 | 181/24 | The phone gives way to a sharp view of the red tin on the prop table. |
| `prop.tin.open` | 197 | 197/24 | The lid begins separating from the lower rim. |
| `prop.moon.lift` | 218 | 109/12 | The gloved hand enters the shot and takes the crescent stick. |
| `stage.return` | 246 | 41/4 | The theater returns in a cut to the amber stage. |
| `stage.moon.enter` | 266 | 133/12 | The tip and interior curve define the crescent against the stage. |
| `stage.rabbit.release` | 281 | 281/24 | The right ear first shifts into its turn. |

Direction's map marks the start of the moon animation at frame 259, and the first shadow pixels appear at frame 261. The music and effects treatments use frame 266 as the cue reference, where the crescent shape is clear. The rabbit movement is small at frame 281. Use the close crop and inspect adjacent frames again after reframing or a substantial camera change.

## Recheck the picture

From the repository root, use the checked picture or pass another MP4 path to the same command. The script returns measured frame indices and exact presentation timestamps.

```sh
PYTHONPATH=skill/imessage-motion-recreation/sound python3 - review/imv-v3/sound/direction/rough/picture.mp4 <<'PY'
import json
import sys
from pathlib import Path
from landmarks import resolve_landmarks

folder = Path("review/imv-v3/sound/direction/rough")
detectors = json.loads((folder / "landmarks.json").read_text())
for event, match in resolve_landmarks(Path(sys.argv[1]), detectors, folder).items():
    print(event, match["frame"], match["pts"], round(match["score"], 3))
PY
```

In a retime check, eight repeated stage frames inserted before the moon animation moved the crescent to frame 274 (137/12 s) and the rabbit to frame 289 (289/24 s). Seven earlier boundaries resolved to the original frames after the H.264 re-encode. The detector definitions were reused as written.
