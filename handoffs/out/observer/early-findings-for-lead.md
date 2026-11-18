# Observer — early findings for the lead

Phase-1 recon, all siblings still at `c49482a`. Three items need a
lead/builder decision; details in `observations/early-findings.md`.

1. **No `director/motion-catalog/` seed exists at base.** The effort brief
   describes a "seed motion-catalog with 6 entries"; `git ls-tree` shows no
   such path at c49482a. Closest real assets: `director/catalogue.json`
   (14 studies), `director/motions.mjs` (9 starters),
   `director/source-studies/` (3 recipe files). If the catalog agent was
   told to *expand* a 6-entry seed, clarify whether it creates the
   directory fresh or extends `catalogue.json`.

2. **Catalog worktree has no scene.json access.** Its sparse checkout
   includes the six source.mp4s + authored fixtures but zero
   `projects/*/scenes/`. A *source-backed measured* catalog (matching the
   existing studies, which cite canonical IDs + literal keys) probably
   needs scenes or `sync_library.py`. Also: `02-danieltian`'s scene lives
   in `STORAGE.json` — a grep for project scene.json finds only 5/6.

3. **Transfer-test film chosen: `03-photon-mini`.** See
   `unfamiliar-choice.md`. When the trial runs, the trial checkouts must
   exclude `projects/03-photon-mini-complete-v1/` AND `catalog/` +
   `inventory/` (they render the accepted films). Protocol:
   `observations/trial-protocol.md`.

— observer (devin-agent-observer)
