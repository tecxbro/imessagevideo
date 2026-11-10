# GitHub Release restoration and offline verification

[tools/sync_library.py](../tools/sync_library.py) restores the large resources from this private repository's GitHub Release without Git LFS or Google Drive. GitHub rejected the attempted LFS upload because the account exceeded its LFS budget. The release approach keeps ordinary code/media/evidence in Git and retains the original large archives and byte-identical binary parts as release assets.

## Commands

After cloning the repository, install the official GitHub CLI and authenticate with access to the private repository (`gh auth login`), then run:

```bash
python3 tools/sync_library.py
```

The helper resolves the repository root from its own location, so it can be run from another working directory. It reads [GITHUB-ASSETS.json](../GITHUB-ASSETS.json) and [LOCAL-LIBRARY.json](../LOCAL-LIBRARY.json), never a hard-coded machine path. The release manifest declares `repository` (or `repo`), `release_tag` (or `tag`), and assets with `file_name`, `path`, `bytes`, `sha256`, `role` and optional `archive_id`. Observed numeric `id`/`asset_id`/`github_asset_id` and GraphQL `node_id`/`github_node_id` are checked in the correct namespaces if supplied.

The normal workflow:

1. Validate relative paths, declared hashes and roles, unique asset names/paths, and agreement between the whole-archive and part records in the two manifests. Refuse an already-present corrupt archive, snapshot or part before any network access.
2. Read release metadata with the authenticated CLI's `gh api repos/<repository>/releases/tags/<tag> --method GET`. Require the observed tag, every declared asset name and byte count, and any declared asset IDs to match. No custom authentication or token handling is used.
3. Download **only the twelve whole archives and two frozen snapshots** using `gh release download <tag> --repo <repository> --pattern <exact-file-name> --dir <staging-directory> --skip-existing`. Validate each complete staged file's size/SHA256 before installing it. Existing files are never overwritten.
4. Split each verified whole archive according to `LOCAL-LIBRARY.json` to recreate all **seventy-eight original binary parts** locally. Every recreated part must match its declared size/SHA256. The individual parts also exist as GitHub Release assets, but the helper avoids downloading the same archive bytes twice.
5. Call the existing retained [safe materializer](../skill/imessage-motion-recreation/library/materialize.py)'s `extract` function into each declared `extracted_path`. Equal Git payloads are retained; missing files, including oversized measured scenes, are restored. Different existing source files cause failure instead of replacement. Per-pack checksum maps retain their separate `.library-receipts` filenames.
6. Read every archived member, validate CRC/internal checksums where present, and compare the extracted local file's size/SHA256. Unrelated local files are preserved.

Temporary staging directories are local and cleaned up after success or failure. The script never prints raw provider stderr, bearer download URLs or tokens. GitHub CLI credentials stay under the CLI's normal control. Provider IDs establish asset identity; whole-file SHA256 still establishes content identity.

## Offline checks

After restoration, this command is read-only and **never calls `gh` or the network**:

```bash
python3 tools/sync_library.py --verify-only
```

It requires every declared whole archive, frozen snapshot and binary part to be present, checks their complete size/SHA256, and checks every extracted archive member against its accepted bytes. It does not download, split, extract or repair files. Viewing and finding the restored code, films, analysis and assets does not require GitHub or Google Drive. Render dependencies and new-company research remain separate concerns.

If a local asset differs, the error identifies its local path. Move it aside or repair it deliberately, then rerun; the helper has no automatic destructive repair mode. If an extracted source file was edited, preserve the edit and resolve that difference deliberately before trying to refill the same project.

## Isolated test

```bash
python3 tools/sync_library.py --self-test
```

The isolated temporary fixture uses a fake `gh` executable implemented with the current Python interpreter. **No network calls or real uploads occur.** The passing test exercises fourteen integrity/safety checks:

- Complete download size/SHA256 checks and rejection of a corrupt remote file before installation.
- Exactly two fixture downloads (archive and snapshot); no duplicate part downloads.
- Byte-exact reconstruction of both fixture parts.
- Safe extraction into a partial Git checkout containing an equal pre-existing source file.
- Preservation of an unrelated user file.
- Offline verification with a deliberately nonexistent CLI command, proving no CLI/network dependency.
- Refusal of corrupt cached whole archives and parts without overwriting them or contacting the provider.
- Refusal of a changed user source file in normal and verification modes.
- Manifest traversal rejection before any fetch.
- Provider asset size, numeric REST ID and GraphQL node ID mismatch rejection.

`python3 -m py_compile tools/sync_library.py` also passes. A full real-library offline verification is run separately from the isolated fixture; the parent task records its observed result. This report does not claim a fresh network clone/download test until that test is actually performed.
