# Running the bundled tools

The package contains source, schema, dependency pins and detailed execution evidence. It does not include generated video, dependency directories, browser binaries, or proprietary font binaries.

For a standalone project, copy scripts/engines, scripts/shared and scripts/verification to its root as engines, shared and verification, and copy scripts/*.py into its scripts directory. The project utilities locate delivery-state.json, references and outputs beside those directories. The portable delivery archive already has that layout. Install JavaScript dependencies with `cd engines` then `npm ci`; engines may also be run directly from this skill's scripts/engines directory with explicit scene/output paths. The browser adapters need an installed Chromium (set CHROME_PATH if its path differs from /usr/bin/chromium) and FFmpeg. Python needs the pinned packages in engines/requirements.txt; use a local virtual environment. FontTools can subset actual verified fonts into WOFF without a Brotli dependency. Obtain any source fonts from their original provider and preserve the license; this package records the Apple source and hashes, not the binaries.

Use scripts/shared/SCHEMA.md for measured scene authoring. Run the engines from the scripts directory as described in scripts/engines/README.md. The neutral smoke tests in the original project proved capability only. The Figma converter remains an unexecuted prototype because account discovery did not respond; follow its audit and the installed Figma skills before use.

Per-source observations and step logs are in references/evidence. The execution-ledger.md distinguishes observed facts, failed attempts and corrections. A future run must acquire its own actual reference and repeat fidelity checks.
