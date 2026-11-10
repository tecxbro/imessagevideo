# Complete archives and original transport parts

All seventy-eight original 24 MiB-or-smaller transport parts are tracked in
ordinary Git under `resource-parts/`. Their complete bytes, filenames and hashes
are recorded in `../LOCAL-LIBRARY.json`. The two small frozen skill/release ZIPs
are also tracked directly. No LFS, release download, Drive or Notion is needed.

Run `python3 tools/sync_library.py` from the repository root. The offline helper
verifies every tracked part, rebuilds all twelve original ZIPs byte-for-byte,
checks each whole SHA256 and safely extracts/merges the complete projects. It
restores the two oversized copies of Daniel's full scene and any archive-only
cache members. Every original file's bytes are preserved in Git; fourteen large
derived files are reassembled rather than stored as over-limit GitHub blobs.

GitHub rejected LFS upload because the account exceeded its LFS budget. Its
release-upload endpoint rejected the available credential. The unused empty
draft release was removed; historical prototypes are documented under
`../reports/migration-source/`. The final setup uses ordinary Git only.

Keep the repository and its release private. Existing font/source licenses are
preserved; their inclusion does not create a new redistribution license.
