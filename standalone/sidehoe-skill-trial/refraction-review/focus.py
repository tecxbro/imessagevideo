"""Extract matching source, previous, and revised handset frame crops."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hyperframes-review"))
import focus

if __name__ == "__main__":
    full = (0, 0, 2000, 2000)
    entrance = (65, 560, 1935, 2000)
    keys = (50, 1320, 1950, 2000)
    focus.FOCUS = {
        133: ("before-assistant-handset-cut", full),
        134: ("first-assistant-handset-frame", entrance),
        135: ("colored-rim-and-refracted-controls", entrance),
        136: ("side-portrait-light-and-rail-reflection", entrance),
        137: ("handset-refraction-settles", entrance),
        138: ("next-assistant-handset-frame", entrance),
        192: ("attached-active-title-and-hearts", (320, 790, 1630, 1190)),
        342: ("before-sofia-closeup-adjustment", full),
        343: ("sofia-railing-and-keyboard-start", full),
        345: ("sofia-composer-and-key-approach", keys),
        347: ("sofia-composer-and-key-closest", keys),
        351: ("sofia-key-end", keys),
        352: ("after-sofia-closeup-adjustment", full),
        479: ("calendar-31-tile-arrival", full),
        658: ("follow-handset-bevel-and-keyboard", full),
        675: ("yes-cursor-contact", (320, 967, 1150, 1270)),
        706: ("attached-profile-badge", (692, 688, 1310, 1315)),
        777: ("last-frame", full),
    }
    focus.main()
