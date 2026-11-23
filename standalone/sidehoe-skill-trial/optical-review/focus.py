"""Compare the transition and its neighboring frames at the source clock."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hyperframes-review"))
import focus


if __name__ == "__main__":
    whole_frame = (0, 0, 2000, 2000)
    focus.FOCUS = {
        106: ("profile-control", (680, 650, 1320, 1320)),
        191: ("type-and-hearts-control", (365, 790, 1635, 1180)),
        333: ("before-sofia-push", whole_frame),
        335: ("sofia-push-onset", whole_frame),
        336: ("sofia-push", whole_frame),
        337: ("sofia-shutter", whole_frame),
        338: ("sofia-history", whole_frame),
        339: ("sofia-keyboard", whole_frame),
        348: ("sofia-settled-controls", whole_frame),
        349: ("sofia-hold", whole_frame),
        391: ("send-cursor-approach", (1580, 1256, 1880, 1600)),
        398: ("send-cursor-in-motion", (1560, 1072, 1900, 1416)),
        397: ("calendar-first-visible", whole_frame),
        399: ("calendar-approach", whole_frame),
        400: ("calendar-before", whole_frame),
        401: ("calendar-overlap", whole_frame),
        402: ("calendar-after", whole_frame),
        405: ("calendar-settling", whole_frame),
        413: ("calendar-appointments", (230, 420, 1770, 1150)),
        416: ("calendar-headings", (300, 310, 1820, 570)),
        421: ("after-calendar-entry", whole_frame),
        612: ("calendar-tile-face", (738, 1090, 1250, 1655)),
        655: ("follow-handset-registration", whole_frame),
        667: ("follow-handset", whole_frame),
        675: ("follow-cursor-contact", (710, 880, 1300, 1400)),
    }
    if "--attachments" in sys.argv:
        sys.argv.remove("--attachments")
        focus.FOCUS = {
            190: ("attached-title-and-hearts", (350, 790, 1655, 1200)),
            706: ("attached-profile-badge", (730, 730, 1270, 1270)),
        }
    focus.main()
