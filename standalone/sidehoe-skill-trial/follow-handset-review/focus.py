"""Extract matched frames from the calendar handoff and the follow-up camera push."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hyperframes-review"))
import focus

if __name__ == "__main__":
    full = (0, 0, 2000, 2000)
    controls = (586, 945, 1050, 1114)
    focus.FOCUS = {
        192: ("attached-active-title-and-hearts", (320, 790, 1630, 1190)),
        477: ("last-calendar-frame-before-tile", full),
        478: ("calendar-cell-crosses-ring-tile", full),
        479: ("flame-and-31-arrive", full),
        480: ("first-app-tile-overlap", full),
        482: ("four-tile-overlap", full),
        483: ("first-unchanged-orbit-frame", full),
        629: ("before-settled-follow-phone", full),
        630: ("first-adjusted-follow-phone", full),
        633: ("phone-nearly-settled", full),
        640: ("follow-phone-header-and-keyboard", full),
        647: ("last-frame-before-no", controls),
        648: ("no-first-appears", controls),
        649: ("before-yes", controls),
        650: ("yes-first-appears", controls),
        657: ("case-and-keyboard-before-closest-frame", full),
        658: ("bevel-chips-and-keyboard", full),
        659: ("last-complete-handset", full),
        660: ("first-cropped-push-frame", full),
        667: ("cropped-handset-lens-push", full),
        670: ("last-cropped-push-adjustment", full),
        671: ("cursor-approach-after-adjustment", full),
        674: ("last-frame-before-yes-contact", (320, 967, 1150, 1270)),
        675: ("yes-contact", (320, 967, 1150, 1270)),
        706: ("attached-profile-badge", (692, 688, 1310, 1315)),
        777: ("last-frame", full),
    }
    focus.main()
