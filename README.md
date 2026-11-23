# iMessage motion — complete local library

[All local iMessage video skills, projects, and archived versions (November 22, 2026)](GITHUB-ARCHIVE.md)

This private repository contains the skill **and all the production bytes it references**: six measured example projects, authored code, assets, original and reconstructed videos, UI-audio sources, visual motion studies, and analysis. Everything is stored in ordinary Git, including verified chunks for files too large to store as single GitHub files. **Clone, then run the one-time local assembly command below to recreate every canonical file.** No Git LFS, GitHub Release, GitHub CLI, Google Drive or Notion connection is required for normal use.

Start with [the final production code and keyframes](FINAL-PRODUCTION.md), [the local video/code catalogue](catalog/index.html), [the full location guide](LOCATIONS.md), or [the skill instructions](skill/imessage-motion-recreation/SKILL.md). For a detailed account of what is taught and what remains unfinished, read [Skill contents and gaps](reports/SKILL-CONTENTS-AND-GAPS.md).

## Final-code completeness

[The new independent audit](reports/completeness-audit/README.md) confirms the
six accepted scene/keyframe files, all 4,632 declared assets, current five-engine
source and all thirty final videos. The originals/results fully decoded with
zero errors. [FINAL-PRODUCTION.md](FINAL-PRODUCTION.md) identifies exactly which
code to edit or run; [FAILURES-AND-FIXES.md](FAILURES-AND-FIXES.md) explains the
measured failures and accepted improvements. Older builders are optional history,
not required steps in the final render route. Temporary full-frame PNG caches
are outside this final-working-set claim.

## Get every file onto your computer

You need Git, Python 3.11 or later, access to the private `tecxbro/imessagevideo` repository, and enough disk space for Git objects, tracked archive chunks, assembled ZIPs and restored projects. Use your normal Git HTTPS authentication with an account that can access this private repository. Run these commands separately:

```bash
git clone https://github.com/tecxbro/imessagevideo.git
cd imessagevideo
python3 tools/sync_library.py
```

**Cloning includes all source bytes, but the large derived files still need local reassembly.** Ordinary code, assets, videos, fonts and evidence are readable in the main branch. [archives/resource-parts/](archives/resource-parts/) contains seventy-eight verified parts, each at most 24 MiB, covering twelve complete resource ZIPs. Two smaller frozen skill/release-verification snapshot ZIPs are also tracked normally in [archives/](archives/).

`tools/sync_library.py` uses only Python's standard library and local files. It verifies all seventy-eight part hashes, rebuilds the twelve full ZIPs with their exact recorded SHA256 values, then safely extracts/merges the complete packs. This restores the two identical full Daniel scene copies and any other missing canonical payload. It does not download anything, require a GitHub account/tool connection, or contact Drive after cloning. Existing identical payload files are reused; conflicting files are not silently overwritten.

The assembled ZIPs and two large Daniel `scene.json` files are ignored as derived working files because of GitHub's single-file size limit. Their **complete exact bytes remain in the tracked archive parts**; ignoring the assembled copies does not omit them from the library. [LOCAL-LIBRARY.json](LOCAL-LIBRARY.json) records the local paths and SHA256 identities. Let the assembly command finish before full verification or opening a large scene. Keep the repository private.

On a Mac, follow [MAC-SETUP.md](MAC-SETUP.md) for prerequisites, local viewing, skill installation and opening the cloned folder in Codex. This repository does not remotely install or control anything on your Mac.

## Open and find things locally

- [catalog/index.html](catalog/index.html): original films, reconstructed results in five methods, full shared renderer source, and links to the exact scene, analysis and visual references.
- [inventory/index.html](inventory/index.html): searchable local file inventory.
- [inventory/ALL-FILES.csv](inventory/ALL-FILES.csv): exact file-by-file locations and metadata.
- [LOCAL-LIBRARY.json](LOCAL-LIBRARY.json): machine-readable roots for every restored project/resource pack.
- [LOCATIONS.md](LOCATIONS.md): human-readable map of code, movies, assets, sound, analyses and history.
- [skill/imessage-motion-recreation/director/index.html](skill/imessage-motion-recreation/director/index.html): editable neutral motion starters, component anatomy and paired source/rebuild teaching images.

Keep the directory structure intact. Operational catalogue links are relative, so the top-level repository folder can move. Open the HTML files from the cloned folder; GitHub's file viewer is not the local video application.

Python 3.11 or later supplies the local lookup and verification tools without a third-party Python package installation:

```bash
python3 tools/library.py list
python3 tools/library.py where 04-poke
python3 tools/library.py find frames.csv
python3 tools/library.py verify
python3 tools/library.py verify --all-files
```

`where` accepts an example ID, archive ID, title or matching substring and returns the core example file paths. `find` searches filename/path substrings. `verify` checks the registered archive and core scene/reference/result identities; `--all-files` also hashes the complete generated payload inventory and can take longer. Use `python3 tools/library.py --help` for the command contract.

## All six complete examples

Each project keeps its full accepted measured scene, every declared runtime asset, original reference, five finished reference-audio movies, real shared engine code, per-method run entrypoints, provenance and retained authoring/evidence files.

| Example | Full project | Complete scene | Finished movies |
|---|---|---|---|
| PhotonHQ | [01-photonhq project](projects/01-photonhq-complete-v1/imessage-recreations/) | [scene.json](projects/01-photonhq-complete-v1/imessage-recreations/scenes/01-photonhq/scene.json) | [deliverables/01-photonhq](projects/01-photonhq-complete-v1/imessage-recreations/deliverables/01-photonhq/) |
| Daniel Tian's Photon | [02-danieltian project](projects/02-danieltian-complete-v1/imessage-recreations/) | [scene.json — assemble locally](STORAGE.json) | [deliverables/02-danieltian](projects/02-danieltian-complete-v1/imessage-recreations/deliverables/02-danieltian/) |
| Photon Mini App | [03-photon-mini project](projects/03-photon-mini-complete-v1/imessage-recreations/) | [scene.json](projects/03-photon-mini-complete-v1/imessage-recreations/scenes/03-photon-mini/scene.json) | [deliverables/03-photon-mini](projects/03-photon-mini-complete-v1/imessage-recreations/deliverables/03-photon-mini/) |
| Poke | [04-poke project](projects/04-poke-complete-v1/imessage-recreations/) | [scene.json](projects/04-poke-complete-v1/imessage-recreations/scenes/04-poke/scene.json) | [deliverables/04-poke](projects/04-poke-complete-v1/imessage-recreations/deliverables/04-poke/) |
| Linq | [05-linq project](projects/05-linq-complete-v1/imessage-recreations/) | [scene.json](projects/05-linq-complete-v1/imessage-recreations/scenes/05-linq/scene.json) | [deliverables/05-linq](projects/05-linq-complete-v1/imessage-recreations/deliverables/05-linq/) |
| Launch gallery / Rene | [06-gallery project](projects/06-gallery-complete-v1/imessage-recreations/) | [scene.json](projects/06-gallery-complete-v1/imessage-recreations/scenes/06-gallery/scene.json) | [deliverables/06-gallery](projects/06-gallery-complete-v1/imessage-recreations/deliverables/06-gallery/) |

Inside each project, start with `README-COMPLETE-EXAMPLE.md`. The original is `references/<example-id>/source.mp4`; results are `deliverables/<example-id>/<method>.mp4`; explicit run entrypoints are in `examples/<example-id>/`; the genuine implementations are in `engines/`.

The architecture is **one full measured scene per film plus five genuine shared adapters**: Remotion React, GSAP, HTML/SVG, Python/Pillow + FFmpeg, and native Motion Canvas. Per-example method wrappers select those implementations. This repository does not pretend that five independently rewritten standalone branded applications were authored for each film. Figma is an unvalidated prototype, not a completed sixth renderer.

## The rest of the production library

| Location | Preserved contents |
|---|---|
| [resources/frozen-visual-delivery-v1](resources/frozen-visual-delivery-v1/) | Original frozen visual delivery and its review/source hierarchy |
| [resources/silent-picture-masters-v1](resources/silent-picture-masters-v1/) | Thirty silent reconstructed picture masters and associated records |
| [resources/all-authored-source-and-fixtures-v1](resources/all-authored-source-and-fixtures-v1/) | Retained authoring programs, source history, neutral tests and corrective fixtures |
| [resources/complete-ui-audio-source-v1](resources/complete-ui-audio-source-v1/) | Complete later UI-sound inputs, licensed stock/source records, generated inputs, cues, stems, mixes, previews, reports and portable audio tools |
| [resources/font-inputs-and-linux-fallbacks-v1](resources/font-inputs-and-linux-fallbacks-v1/) | Pinned font inputs, their license records and Linux fallback dependencies |
| [resources/later-workflow-and-review-source-v1](resources/later-workflow-and-review-source-v1/) | Later director/review implementation and workflow/source audits |
| [archives/](archives/) | Tracked verified archive parts and two frozen snapshots; twelve full ZIPs are assembled locally by `tools/sync_library.py` |
| [release-evidence/](release-evidence/) | Earlier release verification records |
| [inventory/](inventory/) | Exact local file inventory and restoration/verification records |

Some content is deliberately duplicated between a complete case and a historical archive. The inventory is the authority for current file locations and counts. Original fonts, media and effects retain their original license conditions; private storage does not grant new distribution rights.

The thirty principal five-method movies retain the supplied films' soundtracks. The later UI-audio resources contain the separately produced sourced/generated effects and optional music. Their provenance records distinguish these modes. Reading the video title alone is not enough to establish which audio it contains.

## What the skill teaches

The entrypoint is [skill/imessage-motion-recreation/SKILL.md](skill/imessage-motion-recreation/SKILL.md). It directs the agent to research a company, record source-backed facts and real UI, choose a causal story, inspect actual visual references, select components/motions, author a shot plan, render through a real engine, align UI sounds, compare native frames and deliver the complete source/evidence.

It includes fourteen **selected measured motion studies**, nine editable neutral components, nine newly authored motion starters, a design grammar, a shot-plan schema, a company-research schema, a heuristic motion router, source/rebuild images and all 7,499 historical aligned-frame comparison rows. Fourteen is the present number of curated lessons, not the number of animations in the six complete films. More teaching cards and semantically reusable extractions can be authored from the full scenes. The [contents and gaps report](reports/SKILL-CONTENTS-AND-GAPS.md) lists every study and its exact scope.

This is an instruction/code/reference package read by an agent, not trained model weights or a fully autonomous video generator. The model opens relevant local files as needed; the complete library is not injected into its prompt at once.

Install the skill link if you want it discoverable from your local skill directory:

```bash
python3 tools/install_skill.py
```

The default is a symlink at `~/.agents/skills/imessage-motion-recreation` pointing to this checkout. An already-correct link is accepted; a different existing destination is refused rather than overwritten. Keep the checkout available. [MAC-SETUP.md](MAC-SETUP.md) explains selecting a custom destination and opening a local Codex session.

## Offline access versus rendering setup

Stored code, images, video, audio, JSON and CSV analysis can be accessed offline after cloning **and completing `python3 tools/sync_library.py` once**. The assembly command itself is fully offline. The viewers do not need a Drive account or a generation API. The preserved [Drive manifest](skill/imessage-motion-recreation/library/manifest.json) is historical recovery provenance; [LOCAL-LIBRARY.json](LOCAL-LIBRARY.json) maps normal local use and tracked archive identities.

Rerendering is a separate setup task. This repository supplies actual renderer source and pinned manifests, **not installed `node_modules`, virtual environments, browser binaries or a cross-platform runtime image**. Depending on the method, install compatible Node/Python dependencies, Chromium, FFmpeg, Cairo/fontconfig and the required fonts. Follow the selected project's `README-COMPLETE-EXAMPLE.md`, the skill's [RUNNING.md](skill/imessage-motion-recreation/RUNNING.md) and [engine instructions](skill/imessage-motion-recreation/scripts/engines/README.md), then validate that environment. Fresh company research also needs online sources unless a complete local evidence pack is provided.

Historical fidelity measurements, renderer parity, audio checks and static viewer validation have defined scopes. They do not establish 100% perceptual identity, a new clean-machine render of all thirty movies, or interactive playback on your device. Known limits and the prioritized remaining work are recorded in [SKILL-CONTENTS-AND-GAPS.md](reports/SKILL-CONTENTS-AND-GAPS.md) and [OFFLINE-VIEWER.md](reports/OFFLINE-VIEWER.md).
