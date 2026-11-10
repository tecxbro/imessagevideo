# Offline restoration from tracked Git chunks

[tools/sync_library.py](../tools/sync_library.py) is the normal restoration tool. It uses **only local files and the Python standard library**. It does not use Git LFS, GitHub Releases, Google Drive, GitHub CLI, a token, subprocesses or network libraries.

The repository tracks ordinary code, media, fonts and evidence, plus all **seventy-eight original lossless binary parts** and the two small frozen snapshot ZIPs. The twelve assembled resource ZIPs and two oversized duplicate Daniel scene files are generated locally from those exact tracked bytes. They are not omitted source or externally hosted prerequisites.

## After cloning

With Python 3.11 or newer, run from the repository root:

```bash
python3 tools/sync_library.py
```

The helper locates the checkout with `Path(__file__).resolve().parents[1]`, so the library can move and the command can also be run from another working directory. It reads [LOCAL-LIBRARY.json](../LOCAL-LIBRARY.json) for the archive order, part order, relative paths, extracted destinations, exact byte counts and SHA256 values.

The normal workflow:

1. Validate all declared local paths, archive IDs, unique archive/part paths, hashes and summed part sizes. Stream-read and verify every required local part before writing anything. Also verify the two frozen snapshots and every already-present whole archive. Missing parts or corrupt existing files cause failure instead of automatic replacement.
2. For each missing whole ZIP, concatenate the declared parts **in manifest order** into a temporary file on the same local volume. Recheck each streamed part and the complete assembled archive's size/SHA256.
3. Install that verified archive atomically with a no-overwrite hard link. A different existing archive is never replaced. The volume must support local hard links; temporary staging is removed after success or failure.
4. Use the retained [safe materializer](../skill/imessage-motion-recreation/library/materialize.py)'s `extract` function into each declared `extracted_path`. Equal Git payloads stay intact; missing files, including oversized measured scenes and any archived ignored cache files, are restored. Different existing source files cause failure. Per-pack checksum maps retain their separate `.library-receipts` filenames.
5. Stream-read every ZIP member, verify its CRC and internal checksum map when present, and compare the extracted local file's size/SHA256. Unrelated local files are preserved.

The original frozen snapshots are checked against their recorded accepted values: `archives/imessage-motion-complete-skill-v3.zip` and `archives/release-verification-v3.zip`. A future explicit `snapshots` array in `LOCAL-LIBRARY.json` can supply additional local snapshot records without depending on historical provider metadata.

The script is idempotent: a repeated run verifies existing whole archives and equal payloads. It does not rewrite those accepted files. It has no destructive repair mode. If an existing local file differs, the error identifies the path; move it aside or repair it deliberately before rerunning. Preserve your source edits instead of asking the tool to overwrite them.

## Read-only offline checks

After normal restoration, run:

```bash
python3 tools/sync_library.py --verify-only
```

This mode performs **no writes and no network access**. It requires all twelve assembled archives, seventy-eight parts, two frozen snapshots and extracted archive members to be present and match their accepted content. It does not assemble, extract or repair. A fresh clone should run normal sync first because its generated whole ZIPs and oversized scenes have not yet been materialized.

Viewing and finding the retained code, films, analysis and assets is offline. Installing third-party render dependencies and researching a new company are separate operations; this helper does not claim to install those without the internet.

## Isolated integrity test

```bash
python3 tools/sync_library.py --self-test
```

The passing test uses isolated local fixture files and the actual retained extractor. It has no provider executable, authentication or network dependency. Fourteen checks cover:

- Byte-exact archive reconstruction from complete ordered parts, with part/whole size and SHA256 validation.
- Safe merging with an equal pre-existing Git source file and preservation of an unrelated user file.
- Idempotent repeated restoration.
- Verification mode preserving the complete local file set, content hashes and modification times.
- Refusal of corrupt cached archives, corrupt/missing parts and different source files without overwriting them.
- Refusal of a wrong joined archive hash before installation, with staging cleanup.
- Manifest and archive traversal rejection.
- Refusal of a corrupt frozen snapshot without replacement.

Python compilation also passes. The actual restored checkout completed **both normal offline sync and a separate read-only `--verify-only` run** successfully: **twelve archives, seventy-eight parts, two frozen snapshots, and all 14,161 extracted files verified**, with no network access or overwrite of different files. Its whole ZIPs were already present and correct, so that run assembled zero new ZIPs. Missing-ZIP assembly is proven by the isolated fixture; the normal-checkout result is not presented as a fresh-clone proof.

## Abandoned provider attempts

The LFS route was rejected because the GitHub account exceeded its LFS budget. The GitHub Release upload route then returned `HTTP 401 Bad credentials` on `uploads.github.com` despite ordinary Git/API access working. No alternate credentials or authentication workaround was attempted. Neither service is part of normal restoration.

The earlier release-based helper and its explanatory report are preserved solely as history in [reports/migration-source/](migration-source/): `sync_github_release.py` and `GITHUB-RELEASE-SYNC-ATTEMPT.md`. They describe the abandoned approach and are **not** the runnable normal-use instructions. The active tool and this report describe the final tracked-chunk architecture.
