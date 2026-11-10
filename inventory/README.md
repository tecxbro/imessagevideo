# Complete offline inventory

Open [index.html](index.html) for local search. [ALL-FILES.csv](ALL-FILES.csv) and [ALL-FILES.json](ALL-FILES.json) contain every inventory row. The same JSON is available compressed in [ALL-FILES.json.gz](ALL-FILES.json.gz). Filtered lists: [code and scene data](CODE.csv), [videos](VIDEOS.csv), [analysis](ANALYSIS.csv), [audio](AUDIO.csv), [images/vectors/fonts](ASSETS.csv).

Every stable authored/library file is listed with its actual relative path, current absolute path, byte count, complete streaming SHA256 and role flags. Complete scene JSON is code/data, not a missing separate application. Category is a single convenient label; roles overlap, so an HTML comparison can appear in both code and analysis. Filtered lists include duplicate archival copies and do not claim unique authored works.

Archive fragments under `archives/resource-parts/` are retained, explicitly labelled duplicates of assembled archive bytes. Directory entries themselves are not payload files. Symlinks are listed as metadata without following them outside the library. No network requests, external scripts, fonts or account are required to browse this index.

Generated inventory files list their own paths with `metadata-only-generated-index`, omitting their sizes and hashes to prevent a recursive self-checksum cycle. `.git` internals, installed dependency/cache directories and credential filenames are excluded. Temporary in-progress writes are excluded. Every observed exclusion and any unstable file is listed in [summary.json](summary.json); these are explicit scope boundaries, not hidden omissions. Historical absolute paths inside old research/scan reports remain original provenance labels; use the inventory's `relative_path` to locate restored files.

Generate a fresh snapshot after the library has stopped changing:

```bash
python3 tools/build_inventory.py
python3 tools/build_inventory.py --verify
```

These commands run from the library root; the helper derives that root from its own location, so it also works after the whole folder is moved. `--root /another/library` is available for explicit inspection. Verification checks every stored payload hash and flags added/missing/changed files; generated indexes are checked for existence, not self-hashed. Rebuild the inventory after intentional edits. No Python packages beyond the standard library are used.
