# The Moon Cue picture lock

Direction delivered the silent 960 × 540 master in commit `db92188`. The MP4 has one H.264 video stream and 360 displayed frames at 24 fps, for 15 seconds. Its SHA-256 is `838fbb35fa9741cb373875d2c6f88536c2dd46ab6abc39978e47a1d7f978cec7`, matching Direction's receipt. [Picture master](picture.mp4) · [Direction event map](picture.events.json)

The frame strips show the decoded neighbors of each boundary. Teal boxes mark the measured patches. The PNG templates are unscaled crops from this silent master. The revised interface, staging, and prop geometry required new crops for those actions. [Frame evidence](frame-evidence.png) · [Detector definitions](landmarks.json)

| Landmark | Frame | Picture time (s) | Visible boundary |
|---|---:|---:|---|
| `message.question.press` | 82 | 41/12 | The blue send control compresses. |
| `message.question.send` | 84 | 7/2 | The question enters the thread in blue. |
| `message.answer.receive` | 113 | 113/24 | The answer enters below it. |
| `prop.table.reveal` | 153 | 51/8 | The phone disappears in the cut to the sharp tin and table. |
| `prop.tin.open` | 165 | 55/8 | A slit appears between the lid and lower rim. |
| `prop.moon.lift` | 189 | 63/8 | The already-held paper crescent first moves up. |
| `stage.return` | 212 | 53/6 | The amber theater returns in a cut. |
| `stage.moon.enter` | 218 | 109/12 | The crescent tip and inner curve become clear against the stage. |
| `stage.rabbit.release` | 254 | 127/12 | The rabbit ear starts to turn. |
| `stage.audience.release` | 270 | 45/4 | The right spectator starts leaning in. |

Direction's `stage.moon.enter` at frame 216 identifies the first shadow edge. The detector uses frame 218 for the crescent reveal as it becomes legible. The spectator passes through a similar pose again while settling back. Its search window covers the first lean and ends before the settling motion.

## Recheck the picture

Run from the repository root. Set the argument to a revised MP4 to measure its picture clock with the same regions. If the framing or animation changes, inspect the crop and neighboring frames again.

```sh
PYTHONPATH=skill/imessage-motion-recreation/sound python3 - review/imv-v3/sound/direction/locked/picture.mp4 <<'PY'
import json
import sys
from pathlib import Path
from landmarks import resolve_landmarks

folder = Path("review/imv-v3/sound/direction/locked")
detectors = json.loads((folder / "landmarks.json").read_text())
for event, match in resolve_landmarks(Path(sys.argv[1]), detectors, folder).items():
    print(event, match["frame"], match["pts"], round(match["score"], 3))
PY
```
