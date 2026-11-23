"""Capture matched source, previous, and current casing, keyboard and badge frames."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hyperframes-review"))
import focus

if __name__ == "__main__":
    full = (0, 0, 2000, 2000)
    top = (64, 755, 1945, 1550)
    keys = (170, 1020, 1830, 2000)
    badge = (690, 650, 1310, 1315)
    focus.FOCUS = {
        138: ("before-revised-shoulder", top),
        139: ("first-curved-shoulder", top),
        145: ("speaker-and-antenna-light", top),
        150: ("held-speaker-slot", top),
        151: ("casing-hold-before-exit", top),
        152: ("source-matched-case-and-speaker", top),
        153: ("first-exit-after-continuous-hold", top),
        160: ("speaker-during-exit", (64, 875, 1950, 1660)),
        161: ("last-assistant-frame", full),
        162: ("first-title-after-cut", full),
        192: ("attached-title-and-hearts", (320, 790, 1630, 1190)),
        479: ("blue-calendar-31-tile-arrival", full),
        675: ("cursor-contacts-yes", (320, 967, 1150, 1270)),
        689: ("before-keyboard-withdrawal-adjustment", keys),
        690: ("first-withdrawal-keyboard", keys),
        691: ("keyboard-letters-during-withdrawal", keys),
        692: ("keycaps-track-camera", keys),
        693: ("keyboard-and-composer-withdrawal", keys),
        694: ("handset-header-returns", full),
        695: ("last-withdrawal-frame", full),
        696: ("closing-badge-cut", full),
        700: ("before-artwork-registration", badge),
        701: ("first-separated-badge-elements", badge),
        706: ("attached-profile-badge", badge),
        711: ("badge-before-outline-join", badge),
        712: ("badge-outline-join", badge),
        716: ("badge-marks-shrinking", badge),
        732: ("held-card-artwork", badge),
        765: ("last-held-badge", badge),
        766: ("first-fade-frame", badge),
        777: ("last-frame", full),
    }
    focus.main()
