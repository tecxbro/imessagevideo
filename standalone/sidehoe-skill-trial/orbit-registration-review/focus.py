"""Capture matched frames around Sofia's suggestion and the four-tile orbit."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hyperframes-review"))
import focus

if __name__ == "__main__":
    full=(0,0,2000,2000)
    suggestion=(713,745,1760,1348)
    orbit=(270,493,1755,1591)
    exit_crop=(407,921,1620,2000)
    focus.FOCUS={
        192:("attached-title-and-hearts",(320,790,1630,1190)),
        339:("before-suggestion-fit",suggestion),
        340:("first-suggestion-fit",suggestion),
        341:("rising-angled-suggestion",suggestion),
        342:("sofia-suggestion-lettering",suggestion),
        343:("sofia-suggestion-as-camera-settles",suggestion),
        346:("last-fitted-suggestion-frame",suggestion),
        347:("following-suggestion-frame",suggestion),
        479:("calendar-31-tile-arrival",orbit),
        482:("last-earlier-tile-handoff-frame",orbit),
        483:("first-registered-orbit-frame",orbit),
        486:("four-independent-tiles",orbit),
        522:("red-tile-foreground",orbit),
        550:("dark-and-ring-tiles-approach",orbit),
        554:("dark-glyph-and-ring-material",orbit),
        555:("front-tile-exchange",orbit),
        557:("ring-tile-shift-and-focus",orbit),
        558:("ring-crosses-forward",orbit),
        562:("rings-continue-through-foreground",orbit),
        575:("calendar-and-ring-tiles",orbit),
        612:("curved-calendar-face",orbit),
        614:("start-of-tile-exit",exit_crop),
        617:("tile-descent-exposure",exit_crop),
        621:("last-visible-tile-streak",exit_crop),
        622:("first-empty-frame",full),
        675:("cursor-contact",(320,967,1150,1270)),
        694:("retained-keyboard-streaks",(178,1295,1818,2000)),
        706:("attached-profile-badge",(690,650,1310,1315)),
        777:("last-decoded-frame",full),
    }
    focus.main()
