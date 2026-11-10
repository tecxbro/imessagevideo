# Complete local iMessage motion library

This private release preserves all twelve complete resource ZIPs, all
seventy-eight original transport fragments and both frozen skill/release ZIPs.
The `main` branch contains readable source, ordinary media/assets, local skill,
offline viewers, file inventory, evidence and Mac setup instructions.

After cloning, run `python3 tools/sync_library.py` using an authenticated GitHub
CLI connection. It downloads the fourteen ZIPs from this repository, verifies
their byte counts and SHA256, recreates all original transport fragments and
extracts/merges the complete projects. GitHub is the only setup source; Drive
and Notion are not required. Subsequent stored-library use is local/offline.

`GITHUB-ASSETS.json` on main records the exact file identities and observed
GitHub asset metadata. The original accepted projects and archive bytes remain
unchanged. Font/source license records are preserved. Keep this repository and
release private.

Git LFS upload was rejected because the account exceeded its LFS budget.
Large archives and the two copies of the oversized Daniel scene are therefore
supplied through release archives. No LFS budget or visibility was changed.

This packages the completed work and its evidence. Figma remains unvalidated,
source comparisons have documented residual errors, and rerendering needs the
pinned third-party dependencies installed for the target computer.
