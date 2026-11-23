"""Compare the matching native frames for the handset and portrait transition."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hyperframes-review"))
import focus


if __name__ == "__main__":
    stage = (0, 0, 2000, 2000)
    focus.FOCUS = {
        190: ("attached-title-and-hearts", (350, 790, 1655, 1200)),
        253: ("portrait-wipe-before", stage),
        254: ("portrait-wipe-entry", stage),
        255: ("portrait-wipe-moving", stage),
        256: ("portrait-wipe-later", stage),
        257: ("portrait-wipe-tail", stage),
        258: ("portrait-wipe-handoff", stage),
        341: ("sofia-before-revision", stage),
        342: ("sofia-closeup-entry", stage),
        348: ("sofia-message-and-keyboard", stage),
        351: ("sofia-closeup-end", stage),
        352: ("sofia-pullback-control", stage),
        365: ("send-typography", stage),
        391: ("send-typography-exit", stage),
        400: ("calendar-before", stage),
        401: ("calendar-handoff", stage),
        402: ("calendar-after", stage),
        671: ("follow-before-revision", stage),
        674: ("follow-cursor-arrival", stage),
        675: ("follow-cursor-contact", (325, 955, 1190, 1305)),
        679: ("follow-controls", stage),
        686: ("follow-feedback", (315, 920, 1190, 1285)),
        688: ("follow-hold-and-light", stage),
        693: ("follow-handset-pullback", stage),
        694: ("follow-exit-control", stage),
        706: ("attached-profile-badge", (730, 730, 1270, 1270)),
        777: ("last-frame", stage),
    }
    focus.main()
