"""Capture matched Sofia handset and tile overlap frames."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hyperframes-review"))
import focus

if __name__ == "__main__":
    full=(0,0,2000,2000)
    early_phone=(448,0,1552,2000)
    keys=(180,1320,1830,2000)
    orbit=(270,493,1755,1591)
    focus.FOCUS={
        192:("attached-title-and-hearts",(320,790,1630,1190)),
        318:("before-complete-case-fit",full),
        319:("first-fitted-case",early_phone),
        321:("case-curves-during-entry",early_phone),
        325:("case-and-composer-moving",early_phone),
        328:("sofia-rails-and-screen",early_phone),
        329:("case-before-closest-held-frame",early_phone),
        330:("sofia-casing-and-composer",early_phone),
        331:("case-start-of-push",early_phone),
        333:("last-visible-bottom-case",early_phone),
        335:("bottom-curves-leave-crop",early_phone),
        336:("keyboard-ink-as-the-phone-grows",keys),
        339:("keyboard-and-composer-in-the-push",keys),
        340:("composer-controls-during-push",keys),
        342:("sofia-messages-at-closest-approach",full),
        343:("next-closeup-control-frame",full),
        479:("calendar-31-tile-arrival",orbit),
        503:("orbit-before-first-continuity-adjustment",orbit),
        505:("first-orbit-continuity-change",orbit),
        515:("tile-path-midpoint",orbit),
        522:("overlapping-tiles-track-the-source",orbit),
        525:("last-tile-continuity-change",orbit),
        527:("after-orbit-continuity-adjustment",orbit),
        557:("retained-ring-motion",orbit),
        675:("cursor-contact",(320,967,1150,1270)),
        694:("retained-keyboard-exposure",(178,1295,1818,2000)),
        706:("attached-profile-badge",(690,650,1310,1315)),
        777:("last-decoded-frame",full),
    }
    focus.main()
