# Private production library

If the private checkout is available, run `python3 tools/sync_library.py`
from its root. It restores archives from tracked pieces and verifies each
hash. `python3 tools/library.py list`, `where 04-poke`, `find QUERY`, and
`verify` locate and check full projects. Open `catalog/index.html` to browse
the accepted videos and code, or `inventory/index.html` for the file inventory.

The checkout holds six complete timelines, thirty renderer exports,
thirty silent pictures, sound assets, comparison data, and editable source
under `projects/` and `resources/`. See `FINAL-PRODUCTION.md` and
`reports/completeness-audit/README.md` in that checkout for their verified
scope. These are existing deliveries. Their original footage and fonts
carry the terms recorded with their source.

The portable [director toolkit](../director/README.md) has nine authored
movement starters and an offline [visual explorer](../director/index.html).
The [measured studies](../director/analysis/index.json) describe native
frames and compare earlier outputs across the timeline. Use the relevant
study for learning motion and inspect the actual supplied reference for
a new recreation. Keep measured source motions distinct from new authored
ones and with their source time map.

The [library manifest](../library/manifest.json) retains historic recovery
provenance. Use the checkout's `LOCAL-LIBRARY.json` and offline restore in
normal use. The [reconstruction playbook](../references/reconstruction-playbook.md)
and prior checkout's `FAILURES-AND-FIXES.md` describe known differences and
the checks that resolved earlier issues.
