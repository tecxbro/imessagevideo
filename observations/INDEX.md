# Observer index

Independent observer for the multi-agent skill-improvement effort.
I watch how agents work AND what they deliver; I do not build.

## Layout

- `film-review/` — contact sheets + full-res frames of the six source
  films, with per-film notes (`README.md`). Basis for the unfamiliar pick.
- `unfamiliar-choice.md` — transfer-test film: **03-photon-mini**, with
  rationale and access rules. Mirrored at `handoffs/out/observer/`.
- `trial-protocol.md` — baseline-vs-revised A/B protocol: environments,
  budgets, preservation list, blind-grading rubric, pass bars.
- `early-findings.md` — running reconnaissance on the five builder
  worktrees and the library/skill itself.
- `attempts/` — one subdir per preserved attempt: trial legs
  (`attempts/baseline/`, `attempts/revised/`) plus notable builder
  attempts (`attempts/<worktree>-<slug>/`). Each holds a small
  `attempt-ledger.md` and whatever small artifacts are copied.
- `preserved/` — copied artifacts that are consequential and small
  (logs, JSONs, contact sheets, screenshots, first-render stills). For
  anything large or frozen-in-place, an entry in `preserved/LEDGER.md`
  records: absolute path, worktree, branch, commit hash, SHA-256, size,
  date, and why it matters — instead of a copy.

## Preservation convention

1. **Snapshot on firsts and on consequence.** First working export, first
   end-to-end render, and before/after of any fix that changes a visible
   result or a claimed metric. Routine WIP is not preserved.
2. Small files (< ~50 MB) → copy into `preserved/<date>-<worktree>-<slug>/`.
3. Large files → ledger entry with path + `git rev-parse HEAD` of that
   worktree + SHA-256 (`shasum -a 256`). Never alter the source worktree.
4. Commit hashes are taken unmodified — I never run git write operations
   in sibling worktrees; I only `git -C <wt> rev-parse HEAD` and
   `git -C <wt> status` to record state.
5. Every preserved item gets a one-line "why" so the final report can
   chain evidence without re-deriving context.

## Key facts pinned

- Base commit for baseline: `c49482a`.
- Ground truth for grading (observer-only): `projects/03-photon-mini-complete-v1/`
  — accepted scene, five deliverable MP4s, verification; plus
  `skill/.../director/analysis/03-photon-mini/frames.csv` (mean MAE 1.5265).
- My sparse checkout currently lacks that project; extend it with
  `git sparse-checkout add '/projects/03-photon-mini-complete-v1/'` when
  the trial runs (observer-side only — the trial agents must never see it).
