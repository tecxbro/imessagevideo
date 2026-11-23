"""Extract matched source, previous, and revised handset and badge frames."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hyperframes-review"))
import focus

if __name__ == "__main__":
    full = (0, 0, 2000, 2000)
    rim = (64, 875, 1950, 1660)
    badge = (692, 688, 1310, 1315)
    focus.FOCUS = {
        135: ("retained-assistant-entrance", full),
        152: ("before-revised-exit", full),
        153: ("first-casing-adjustment", full),
        155: ("exit-shoulders-and-screen", full),
        157: ("case-highlight-before-exit", full),
        158: ("moving-shoulders-and-status", rim),
        159: ("refracted-status-before-cut", rim),
        160: ("casing-and-shutter-streaks", rim),
        161: ("last-phone-frame", full),
        162: ("first-title-frame", full),
        187: ("before-heart-contour-fit", (320, 790, 1630, 1190)),
        188: ("first-adjusted-title-hearts", (320, 790, 1630, 1190)),
        192: ("attached-active-title-and-hearts", (320, 790, 1630, 1190)),
        196: ("last-adjusted-title-hearts", (320, 790, 1630, 1190)),
        197: ("after-heart-contour-fit", (320, 790, 1630, 1190)),
        347: ("retained-sofia-closeup", (50, 1320, 1950, 2000)),
        479: ("calendar-31-tile-arrival", full),
        675: ("yes-cursor-contact", (320, 967, 1150, 1270)),
        700: ("before-badge-outline-fit", badge),
        701: ("first-refined-badge-corner", badge),
        704: ("badge-shoulders-in-motion", badge),
        706: ("attached-profile-badge", badge),
        711: ("last-refined-badge-corner", badge),
        712: ("after-badge-outline-fit", badge),
        777: ("last-frame", full),
    }
    focus.main()
