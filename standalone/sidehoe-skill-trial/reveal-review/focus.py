"""Compare native crops around the repaired Sidehoe shots."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hyperframes-review"))
import focus


if __name__ == "__main__":
    stage = (0, 0, 2000, 2000)
    focus.FOCUS = {
        133: ("identity-before-reveal", stage),
        135: ("first-letter-and-refraction", stage),
        136: ("first-row-and-refraction", stage),
        138: ("handset-rack-focus", stage),
        140: ("assistant-reveal", stage),
        144: ("pinned-profiles", stage),
        150: ("handset-wash", stage),
        157: ("handset-veil", stage),
        161: ("handset-exit", stage),
        184: ("personal-type-entry", (350,780,1655,1250)),
        190: ("attached-title-and-hearts", (350,790,1655,1200)),
        198: ("personal-hearts-in-motion", stage),
        209: ("personal-title-exit", stage),
        212: ("title-to-portrait-handoff", stage),
        400: ("calendar-before", stage),
        401: ("calendar-handoff", stage),
        402: ("calendar-after", stage),
        405: ("calendar-labels-and-pointer", stage),
        706: ("attached-profile-badge", (730,730,1270,1270)),
        765: ("closing-hold", stage),
        766: ("closing-fade-start", stage),
        776: ("closing-fade-tail", stage),
        777: ("final-frame", stage),
    }
    focus.main()
