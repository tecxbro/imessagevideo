"""Extract encoded comparisons of the Sofia handoff, cursor, and closing typography."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hyperframes-review"))
import focus

if __name__ == "__main__":
    full = (0, 0, 2000, 2000)
    messages = (754, 685, 1810, 1380)
    closing_title = (475, 1142, 1540, 1410)
    focus.FOCUS = {
        192: ("attached-active-title-and-hearts", (320, 790, 1630, 1190)),
        351: ("before-sofia-adjustment", full),
        352: ("sofia-handset-and-suggested-reply", full),
        353: ("suggested-reply-and-controls", messages),
        354: ("suggested-reply-starting-to-detach", messages),
        356: ("suggestion-and-controls-during-withdrawal", messages),
        357: ("suggestion-detached-from-handset", full),
        359: ("end-of-measured-sofia-handoff", messages),
        360: ("first-control-after-handoff", full),
        670: ("before-cursor-approach-adjustment", full),
        671: ("first-adjusted-handset-and-approach", full),
        672: ("cursor-approach-before-contact", full),
        674: ("cursor-one-frame-before-contact", (320, 970, 1145, 1280)),
        675: ("first-yes-contact", (320, 970, 1145, 1280)),
        693: ("before-header-reappears", full),
        694: ("follow-up-handset-withdrawing", full),
        695: ("last-follow-up-before-closing", full),
        696: ("first-closing-frame", full),
        706: ("attached-profile-badge", (692, 688, 1310, 1315)),
        717: ("first-closing-word", closing_title),
        735: ("first-line-settled", closing_title),
        754: ("second-line-arrival", closing_title),
        765: ("full-closing-title", closing_title),
        767: ("title-and-pink-wash-in-fade", full),
        774: ("late-closing-fade", full),
        777: ("last-frame", full),
    }
    focus.main()
