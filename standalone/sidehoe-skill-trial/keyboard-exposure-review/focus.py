"""Capture matched source, previous, and current keyboard and glass frames."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hyperframes-review"))
import focus

if __name__ == "__main__":
    full = (0, 0, 2000, 2000)
    shoulder = (70, 750, 1936, 1580)
    glass = (396, 890, 1600, 1200)
    keyboard = (178, 1295, 1818, 2000)
    focus.FOCUS = {
        138: ("before-glass-clearance-fit", shoulder),
        139: ("first-revised-glass-frame", shoulder),
        141: ("camera-island-entrance", shoulder),
        145: ("case-and-glass-hold", shoulder),
        151: ("glass-before-hold-end", glass),
        152: ("clear-glass-above-camera-island", glass),
        153: ("glass-as-the-handset-exits", glass),
        157: ("moving-camera-island", (396, 942, 1600, 1320)),
        161: ("final-glass-and-case", full),
        162: ("first-title-frame", full),
        192: ("attached-title-and-hearts", (320, 790, 1630, 1190)),
        342: ("sofia-closeup-control", full),
        479: ("calendar-31-tile-arrival", full),
        675: ("cursor-contact", (320, 967, 1150, 1270)),
        689: ("early-keyboard-control", keyboard),
        690: ("before-key-specific-exposure", keyboard),
        691: ("keyboard-letters-in-early-withdrawal", keyboard),
        692: ("keyboard-shear-and-caps", keyboard),
        693: ("three-key-rows-during-pullback", keyboard),
        694: ("individual-key-streaks", keyboard),
        695: ("last-visible-keyboard", keyboard),
        696: ("first-closing-badge-frame", full),
        706: ("attached-profile-badge", (690, 650, 1310, 1315)),
        777: ("last-decoded-frame", full),
    }
    focus.main()
