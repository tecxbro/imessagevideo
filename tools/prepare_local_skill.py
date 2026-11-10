#!/usr/bin/env python3
"""Make the extracted working skill local-first; frozen v3 ZIP stays intact."""
from pathlib import Path
import hashlib, json

ROOT=Path(__file__).resolve().parents[1]
skill=ROOT/'skill/imessage-motion-recreation';p=skill/'SKILL.md';s=p.read_text()
s=s.replace('description: Research a company, direct or recreate Apple Messages launch motion, and retrieve complete private example projects with their actual code, assets and five rendered formats. Use visual studies, editable UI components, measured choreography, real rendering engines and UI sound.','description: Research, direct and recreate Apple Messages launch motion using the complete local example projects, actual source code, assets, five renderers, visual studies, editable UI components, measured timing and UI sound in this checkout.')
s=s.replace('Version 3 combines direction instructions, visual studies, component code and access to the complete private example library.','Version 3.1 local combines direction instructions, visual studies, component code and the complete example library stored in this checkout.')
start=s.index('## Retrieve complete examples on demand') if '## Retrieve complete examples on demand' in s else s.index('## Use the complete local library')
end=s.index('## Read the relevant knowledge',start)
section='''## Use the complete local library

The canonical local registry is [LOCAL-LIBRARY.json](../../LOCAL-LIBRARY.json), two directories above this skill folder. It resolves the six full projects and all supporting resources using portable paths relative to the checkout root. Open the [offline full-code/video viewer](../../catalog/index.html) and [every-file browser](../../inventory/index.html). The [location guide](../../LOCATIONS.md) and [exact skill/gap audit](../../reports/SKILL-CONTENTS-AND-GAPS.md) explain every layer. The original frozen skill/archive snapshots remain under `archives/`.

**Normal use requires no Drive, Notion, account or internet lookup for stored examples.** After cloning, run `python3 tools/sync_library.py` once from the checkout root: it assembles the tracked local archive pieces, verifies their hashes and restores the complete payloads. A clone alone does not include oversized raw scene data and archive binaries. Resolve existing local paths and inspect actual files before considering recovery. The original [Drive manifest](library/manifest.json) is retained as historical backup provenance, not the primary path. Do not download a file that already exists locally.

Run these from the checkout root:

```bash
python3 tools/library.py list
python3 tools/library.py where 04-poke
python3 tools/library.py find frames.csv
python3 tools/library.py verify
```

Each project is at `projects/ARCHIVE_ID/imessage-recreations/`. Read its `README-COMPLETE-EXAMPLE.md`. It contains the full measured `scenes/EXAMPLE/scene.json`, declared image/font assets, the original source clip, five completed films, all genuine shared adapters, per-method entry wrappers, authoring code, comparisons and analysis. Run `tools/render_example.py` **inside that materialized project**, after installing its pinned dependencies. Rendering is separate from opening stored films or reading source; the repository does not vendor third-party package installations or browser binaries.

The six examples use one complete scene plus genuine shared adapters for Remotion, GSAP, HTML/SVG, Pillow and native Motion Canvas. The per-method wrappers select that actual implementation; thirty independently rewritten standalone scene projects were not authored. Full scene data is not replaced by the neutral starters.

Supporting resources are under `resources/ARCHIVE_ID/`: frozen delivery, thirty silent masters, all retained authored source/fixtures, complete UI audio inputs, pinned font inputs/Linux fallbacks, and later workflow/review source. Their immutable ZIPs and all seventy-eight original transport parts are also retained in `archives/`. Use the inventory's relative paths if the checkout moves. Historical absolute paths inside scan reports remain provenance labels; `tools/library.py resolve-historical PATH` resolves retained canonical cases without rewriting their history.

Keep this private repository's current visibility unless the user explicitly changes its audience. Prior rejection of a different public source-site upload is historical; it does not prohibit this explicitly authorized private GitHub migration. Figma remains an unvalidated prototype, not a completed sixth method. New-company research may need online primary sources unless sufficient local documents/UI evidence are supplied.

'''
s=s[:start]+section+s[end:]
s=s.replace('Read `director/analysis/index.json`: bundled CSVs cover all 7,499 aligned native output frames across the six films, with source mapping and residual error.','Read `director/analysis/index.json`: bundled historical CSVs cover all 7,499 aligned native output frames across the six accepted GSAP comparisons, with source mapping and residual error. These are not a fresh all-five-method scan.')
s=s.replace('Retrieve complete sound inputs, sources, stems and license/provenance records through the private library manifest; the compact skill carries the workflow and reference evidence.','Read complete sound inputs, sources, stems and license/provenance records locally under `resources/complete-ui-audio-source-v1/`; resolve the exact paths through the local registry/inventory. The skill carries the workflow and reference evidence.')
s=s.replace('Add accepted new examples to the private registry with hashes and rendered visual references; preserve frozen deliveries.','Add accepted new examples to the local registry/inventory with hashes and rendered visual references; preserve frozen deliveries.')
p.write_text(s)
readme='''# Local-first complete example library

All twelve resource archives are extracted in this checkout. Start with
[the local registry](../../../LOCAL-LIBRARY.json), [location guide](../../../LOCATIONS.md),
[offline viewer](../../../catalog/index.html), and [every-file browser](../../../inventory/index.html).
Run `python3 tools/library.py list`, `where 04-poke`, `find QUERY`, or `verify`
from the checkout root. Full code, assets, movies and analysis are local after
local chunk synchronization finishes. No Drive or Notion is needed for normal use.

Each case lives at `projects/ARCHIVE_ID/imessage-recreations/`; supporting packs
live under `resources/ARCHIVE_ID/`. Immutable ZIPs and original transport parts
live under `archives/`. Use the inventory for every exact filename and hash.

`manifest.json`, `materialize.py` and the original v3 ZIP remain unmodified
historical backup/retrieval evidence. Their Drive pointers are not instructions
to prefer the internet over available local files. See
[the detailed skill audit](../../../reports/SKILL-CONTENTS-AND-GAPS.md) for the
fourteen study names, nine component APIs, nine starters and actual limits.

Opening films and reading source works offline. Rerendering also needs the
pinned third-party dependencies installed for the target computer. Fresh online
company research needs network access unless adequate local evidence is given.
Figma is unvalidated; full-scene code and historical frame metrics do not imply
semantic editability of every raster element or perfect identity to a reference.
'''
(skill/'library/README.md').write_text(readme)
(skill/'library/index.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="0;url=../../../catalog/index.html"><title>Local video and full code library</title><p><a href="../../../catalog/index.html">Open the complete offline video and code viewer</a></p><p><a href="../../../inventory/index.html">Find every local file</a></p></html>\n''')
(skill/'library/local-paths.json').write_text(json.dumps({'library_root_relative_to_this_file':'../../..','registry':'../../../LOCAL-LIBRARY.json','viewer':'../../../catalog/index.html','inventory':'../../../inventory/ALL-FILES.csv','storage':'local-checkout','drive_required':False},indent=2)+'\n')
version=json.loads((skill/'version.json').read_text());version.update(version='3.1.0-local',local_registry='../../LOCAL-LIBRARY.json',normal_use_requires_drive=False);(skill/'version.json').write_text(json.dumps(version,indent=2)+'\n')
running=skill/'RUNNING.md';rs=running.read_text();banner='''## Local checkout

For this repository use `../../LOCAL-LIBRARY.json` and `../../catalog/index.html`.
Run `python3 tools/sync_library.py` from the checkout root to reassemble local archive/oversized scene data before offline use.
Stored films, atlases and code need no network after that. Third-party Node/Python
packages, FFmpeg and a supported browser must be installed before rerendering;
those environment installations are not bundled source. Read `../../MAC-SETUP.md`.
Historical Drive instructions below remain recovery documentation only.

'''
if not rs.startswith('## Local checkout'):running.write_text(banner+rs)
checks={str(f.relative_to(skill)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(skill.rglob('*')) if f.is_file() and f.name!='checksums.json' and '__pycache__' not in f.parts and f.suffix!='.pyc'}
(skill/'checksums.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps({'local_skill_version':version['version'],'checksummed_files':len(checks),'drive_needed_for_normal_use':False}))
