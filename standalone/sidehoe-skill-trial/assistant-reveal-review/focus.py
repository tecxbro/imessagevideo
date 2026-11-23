"""Extract encoded views of the inbox scroll, assistant reveal, and calendar wipe."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hyperframes-review"))
import focus

if __name__ == "__main__":
    full = (0, 0, 2000, 2000)
    stage_title = (566, 150, 1445, 735)
    focus.FOCUS = {
        41: ("before-inbox-scroll-adjustment", full),
        42: ("first-inbox-scroll-exposure", full),
        46: ("inbox-rows-in-motion", full),
        47: ("inbox-chrome-and-rows-during-scroll", full),
        48: ("inbox-next-scroll-frame", full),
        51: ("inbox-pins-before-their-fade", full),
        59: ("inbox-last-adjusted-scroll-frame", full),
        60: ("inbox-after-adjustment", full),
        133: ("last-frame-before-assistant", full),
        134: ("assistant-first-camera-opening", full),
        135: ("assistant-upper-refraction", full),
        138: ("assistant-pinned-portraits-appear", full),
        140: ("assistant-first-line-and-partial-lower-line", stage_title),
        141: ("assistant-title-and-handset", full),
        142: ("assistant-next-reveal-frame", stage_title),
        144: ("assistant-two-lines-settling", stage_title),
        151: ("assistant-last-adjusted-title-frame", stage_title),
        152: ("assistant-after-the-title-adjustment", stage_title),
        192: ("attached-active-title-and-hearts", (320, 790, 1630, 1190)),
        472: ("calendar-before-departure", full),
        473: ("calendar-cursor-starts-departing", full),
        475: ("calendar-first-mosaic-cells", full),
        476: ("calendar-mosaic-and-cursor-clearance", full),
        477: ("calendar-last-uncovered-cells", full),
        478: ("first-ring-tile", full),
        706: ("attached-profile-badge", (692, 688, 1310, 1315)),
        777: ("last-frame", full),
    }
    focus.main()
