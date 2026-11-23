"""Review the handset entrance and calendar handoff on the decoded export."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hyperframes-review"))
import focus


if __name__ == "__main__":
    stage = (0, 0, 2000, 2000)
    focus.FOCUS = {
        133: ("before-handset-entrance", stage),
        134: ("first-handset-and-pin", stage),
        135: ("handset-and-upper-refraction", stage),
        136: ("handset-and-lower-refraction", stage),
        137: ("last-handset-refraction", stage),
        138: ("after-handset-entrance", stage),
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
        403: ("calendar-first-frame-without-suggestion", stage),
        408: ("calendar-time-labels", (220, 550, 385, 1850)),
        412: ("calendar-time-labels-settle", (220, 550, 385, 1850)),
        413: ("calendar-handoff-control", stage),
        608: ("calendar-tile-approach", stage),
        613: ("calendar-tile-face", (740, 1000, 1280, 1900)),
        617: ("calendar-tile-exit", stage),
        669: ("follow-cursor-lead-in", stage),
        670: ("follow-cursor-approach", stage),
        671: ("follow-before-closeup", stage),
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
