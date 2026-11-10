## Local checkout

For this repository use `../../LOCAL-LIBRARY.json` and `../../catalog/index.html`.
Run `python3 tools/sync_library.py` from the checkout root to reassemble local archive/oversized scene data before offline use.
Stored films, atlases and code need no network after that. Third-party Node/Python
packages, FFmpeg and a supported browser must be installed before rerendering;
those environment installations are not bundled source. Read `../../MAC-SETUP.md`.
Historical Drive instructions below remain recovery documentation only.

# Running the bundled tools

The package contains source, schema, dependency pins and detailed execution evidence. It does not include generated video, dependency directories, browser binaries, or proprietary font binaries.

For a standalone project, copy scripts/engines, scripts/shared and scripts/verification to its root as engines, shared and verification, and copy scripts/*.py into its scripts directory. The project utilities locate delivery-state.json, references and outputs beside those directories. The portable delivery archive already has that layout. Install JavaScript dependencies with `cd engines` then `npm ci`; engines may also be run directly from this skill's scripts/engines directory with explicit scene/output paths. The browser adapters need an installed Chromium (set CHROME_PATH if its path differs from /usr/bin/chromium) and FFmpeg. Python needs the pinned packages in engines/requirements.txt; use a local virtual environment. FontTools can subset actual verified fonts into WOFF without a Brotli dependency. Obtain any source fonts from their original provider and preserve the license; this package records the Apple source and hashes, not the binaries.

Use scripts/shared/SCHEMA.md for measured scene authoring. Run the engines from the scripts directory as described in scripts/engines/README.md. The neutral smoke tests in the original project proved capability only. The Figma converter remains an unexecuted prototype because account discovery did not respond; follow its audit and the installed Figma skills before use.

Per-source observations and step logs are in references/evidence. The execution-ledger.md distinguishes observed facts, failed attempts and corrections. A future run must acquire its own actual reference and repeat fidelity checks.

The director upgrade adds selected source/rebuild frame images, nine editable component builders, nine new motion starters, measured recipe studies, a design/director decision workflow and all7,499 native-frame CSV rows. Double-click director/index.html after extracting the ZIP; it is self-contained and needs no server. Its SVG preview and exports require no installed dependencies. Rendering a video still uses the bundled engines and their real dependencies. See director/README.md and director/component-contracts.md. Use director/package_skill.py --out /absolute/new-version.zip to preserve these additions and previous frozen ZIPs.

## Complete private library (version3)

For a new company, begin with library/RESEARCH-FIRST.md. Open library/index.html for finished examples plus COMPLETE actual renderer source beneath them. library/manifest.json maps every complete project/movie/source archive to authenticated private Drive files and SHA256 identities. Use library/materialize.py to plan/download/verify/extract. Render from each materialized project's tools/ entrypoints; library/project-tools contains their source copies for inspection/installation under a project tools/ folder. Model context should load the relevant code and images on demand; all source is accessible without injecting gigabytes into one prompt. Original full movies/fonts are in the privatepacks; the compact skill also contains actual images, complete shared engine code, neutral components, motion starters and native-frame evidence.
