"""Extract time-matched views of the casing, response controls, and cursor."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hyperframes-review"))
import focus

if __name__ == "__main__":
    full = (0, 0, 2000, 2000)
    follow = (140, 0, 1870, 2000)
    controls = (330, 970, 1140, 1290)
    focus.FOCUS = {
        318: ("before-sofia-casing-registration", full),
        319: ("first-sofia-casing-registration", full),
        324: ("sofia-handset-and-keyboard", full),
        329: ("last-sofia-casing-registration", full),
        330: ("after-sofia-casing-registration", full),
        649: ("before-follow-up-header-registration", full),
        650: ("first-follow-up-header-registration", full),
        658: ("follow-up-header-and-casing", full),
        660: ("after-follow-up-header-registration", full),
        672: ("before-stage-close-up", follow),
        674: ("yes-before-contact", controls),
        675: ("first-yes-contact", controls),
        676: ("after-yes-contact", controls),
        681: ("follow-up-close-up-with-yes-held", follow),
        685: ("first-yes-feedback", controls),
        687: ("yes-pressed", controls),
        690: ("last-close-up-cursor-registration", controls),
        693: ("phone-and-cursor-withdrawing", full),
        694: ("after-close-up-registration", full),
        777: ("final-frame", full),
    }
    focus.main()
