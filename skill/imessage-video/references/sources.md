# Recognize a source before recreating it

Run from the skill folder. An explicit library path takes precedence over `IMESSAGE_VIDEO_MOTION_LIBRARY` and the bundled default `assets/library`. Use the same directory with the director and the learning tools.

```sh
python scripts/sources.py identify supplied.mp4 --library /path/to/motion-library
```

| Source result | Meaning | What to do |
|---|---|---|
| `known` | The full input SHA-256 matches one registered original. | Read the match's `coverage`, `editable_project`, `reconstruction` and `recipe_ids`. |
| `candidate` | An ordered series of sampled picture signatures matches one or more sources. | Check the suggested time windows, adjacent native frames, edits, captions and soundtrack. Keep every plausible match until the ambiguity is resolved. |
| `new` | No registered source or sufficiently distinctive sequence matched. | Analyze the supplied material. Very short, near-static, cropped, reordered or speed-changed clips can also produce this result. |

Time windows are approximate, half-open intervals measured from the beginning of each input. Sampling runs twice per second. Visual recognition requires multiple distinct frame signatures aligned across time. It does not compare sound.

## Existing work

The six archival identities derive from `video-sources.csv` and `upstream/LOCAL-LIBRARY.json` in the original dataset pack. Their visual signatures were computed from all six SHA-verified original movies. Each seed points to a pinned project, source, measured scene, GSAP master and archived source-comparison report. Daniel's full scene is reconstructed from Git-tracked parts with `python3 tools/sync_library.py` in the original checkout. For an exact source match, open the master, compare the relevant range with the supplied original, and load the scene and its dependencies before commissioning new work. The repository documents residual differences, baked artwork and separate sound versions. Check the audio brief before selecting a master.

| Coverage | Meaning |
|---|---|
| `archived-reconstruction` | A historically inspected project, scene, master and audit are linked. Verify the downloaded hashes before editing. |
| `verified-local-reconstruction` | A named review identified an editable project and distinct master. Both files and the source-bound comparison report passed their stored checksums on lookup. Inspect sound separately. |
| `verified-recipes-only` | Recipe evidence covers the associated motion spans. The remaining film still needs measurement or reconstruction. |
| `associated-artifacts-unavailable` | The source identity remains registered. Recover or re-verify the changed or missing local work before reuse. |

## Register newly verified coverage

First promote each learned span through `scripts/learn.py`. Its recipe must identify the registered film by exact clip checksum or by `source.original_sha256` when it covers an excerpt. For a complete local reconstruction, run `scripts/frames.py` on the original and the independent rendered master. Set the timing and visual tolerances and add `--check-audio` if the source contains audio. Review the picture and listen to the mix. Place the editable project, master and report inside the chosen library. A project can be a self-contained editable archive.

Create a named review receipt. Include either verified recipe IDs, a complete verified reconstruction, or both. Paths below are relative to the chosen library. The source hash is for the entire input film.

```json
{
  "verdict": "pass",
  "reviewed_by": "reviewer identifier",
  "source_sha256": "<original film SHA-256>",
  "recipe_ids": ["new-motion-id"],
  "reconstruction": {
    "editable_project": {"path": "projects/demo/project.zip", "sha256": "<file SHA-256>"},
    "master": {"path": "projects/demo/master.mp4", "sha256": "<file SHA-256>"},
    "comparison": {"path": "projects/demo/comparison/report.json", "sha256": "<file SHA-256>"}
  }
}
```

```sh
python scripts/sources.py register original.mp4 --library /path/to/motion-library \
  --id demo-film --title "Demo film" --verification review.json
```

Registration checks the source, promoted recipes, referenced files and comparison inputs. A successful run atomically publishes `films/<id>.json`. A retry returns `changed: false`. Later reviews can add recipe IDs or a verified local reconstruction to the same source. Seed extensions retain the archival links. Replacing an existing local master or editable project with different bytes requires a separate revision workflow.

## Bind an existing seed to a new film

When the source uses a bundled motion, measure the exact interval against a fresh replay. The command adapts the existing recipe, extracts the requested native frames from the supplied source, then checks every frame of the full crop and each named moving region. Pass the action region in replay coordinates. The optional `--crop X,Y,W,H` selects a source region before comparison. `--content FILE.json` supplies the seed's editable fields.

```sh
python scripts/sources.py bind-seed supplied.mp4 --id supplied-film --title "Supplied film" \
  --recipe photos-under-fixed-heading --frames 12:84 --roi rail:45,95,620,250 \
  --max-mae 8 --reviewed-by reviewer-name --library /path/to/motion-library
```

Here frames 12–83 are included. Choose tolerances suited to the actual footage. A mismatched interval, geometry, source cadence or motion outside tolerance fails before registration. A pass returns a token binding the source SHA-256, frame range, crop, ROI, exact compiled scene, independently rendered preview and extracted comparison clip. Film lookup lists the matching seed IDs and their verified windows. Additional films and intervals can reuse the same motion ID. Bindings live at `film-bindings/<token>` and do not create new motion catalogue entries. These comparisons cover picture timing and pixels. Review the audio separately.
