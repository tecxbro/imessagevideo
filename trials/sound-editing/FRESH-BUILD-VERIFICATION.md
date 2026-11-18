# Fresh-checkout trial routes

Tested from two newly checked-out detached worktrees of branch head `aa9f3015a2a3c0131ea435735a5b15c7a27fd446`, with this candidate's directory-creation fixes applied before building. No media, cue references, venv or synchronized library payloads were copied from the working checkout. Both worktrees created their own venv with the exact README package versions and ran the documented offline library sync and kit copies. Only candidate source/doc files were overlaid; fresh v3 `references/` and `delivery/` were explicitly asserted absent before the first builds.

- `/Users/devin/repos/imessagevideo-fresh-sound`: complete root README route, then v3 and separate delivery-master README routes. Root commands regenerate Poke/Check In UI,304 references and all named treatments; perform all11 clean delivery checks, Poke damage/check/score/repair/check/score, Check In damage/check/score, native-frame evidence, opening investigation, tests and inventory.
- `/Users/devin/repos/imessagevideo-fresh-checkin`: independent bootstrap and Check In README route, instantiating its documented `LABEL` placeholder for T-M8 and T-V2. The root route separately checks production and comparison for both labels. This confirms that the standalone Check In route no longer invokes a random-label builder against committed keys.

`tools/verify_readme_routes.py` executes the fenced shell commands with tracing, interpreting only the explicitly expected damaged-check exit1 and optional label placeholders. Full output is retained under `results/fresh-build/`. It does not regenerate or delete the production checkout's historical metadata. Historical copied-source/library READMEs are not separate newly authored trial reproduction routes.

## Results (verbatim excerpts)

Bootstrap, independently in both worktrees:

```text
"status": "pass",
"mode": "offline-chunk-sync",
"archives": 12,
"parts": 78,
"extracted_files_verified": 14161,
"network_used": false,
"existing_different_files_overwritten": false
```

Root restorer and clean checks:

```text
Validated/restored 304 pinned cue references; named exports restored when missing
pass: picture_match=True, cues=34, defective=0, extras=0
pass: picture_match=True, cues=25, defective=0, extras=0
pass: picture_match=True, cues=21, defective=0, extras=0
```

All11 root clean checks pass: Poke UI-only plus production/comparison across three Poke and two Check In labels. Strict damaged results are expected nonzero exits:

```text
fail: picture_match=True, cues=34, defective=8, extras=1
Repaired 9 findings in 10 regions; video packets unchanged; no key or clean stem read
pass: picture_match=True, cues=34, defective=0, extras=0
fail: picture_match=True, cues=21, defective=5, extras=1
```

Fresh Poke score9/9; repaired key defects0/9 remaining; fresh Check In score6/6. Both damage scores have zero misses/false positives and0-sample timing errors. This reproduces the declared checker results, **not** strict mathematical absence in the old extra-click window: the independent observer's residue finding remains a known repair limitation in `REPAIR-AND-OBSERVER.md`.

Fresh v3 and delivery-master checks each report:

```text
pass: picture_match=True, cues=35, defective=0, extras=0
```

Both have0-sample cue offsets. Fresh production hash is the original `ad3ff5e7…`; fresh delivery hash is `467aa6447505a7521335831f2ceb0e1e0b68dbe406bb4c007810b3fd7082f2c5`, byte-identical to the primary master. Delivery loudnorm:−16.13LUFS,−1.29dBTP,20.7LU LRA. Both preserve packet SHA `3bc70fbb…`.

Fresh existing suites:

```text
Ran 7 tests in 0.005s
OK
Ran 3 tests in 0.000s
OK
Ran 3 tests in 0.013s
OK
Ran 3 tests in 0.019s
OK
Ran 4 tests in 0.000s
OK
```

New nested-output tests in the fresh worktree:

```text
Ran 3 tests in 0.022s
OK
```

Final delivery tests in the fresh worktree:

```text
Ran 3 tests in 0.116s
OK
```

## Failures retained and corrections

1. Integrator's genuine v3 failure: missing ignored `references/` on a fresh checkout. The builder now creates it. Shared JSON/PCM/mux exporters and Poke damage output/key paths also create parents before writing. Overwrite protections remain intact.
2. Check In README previously suggested `build_scores.py`, which intentionally refuses its committed key. Replaced that command with the receipt-based restorer; no key deletion or relabeling is needed.
3. Initial **test harness**, not a builder, supplied its shell program on stdin; the native-frame extractor's FFmpeg consumed later shell lines. The root route reached frame extraction after all media/check/damage/repair steps, then failed. Changed the harness to a script file with closed stdin. First resume lacked shell variables and exited127; fixed variable restoration, then continued at `evidence_sheets.py` without rebuilding passed products. `root-initial.txt`, `root-resume-first.txt` and `root-complete.txt` retain these results. An earlier harness version duplicated the Check In build block while instantiating both labels; both executions passed. Placeholder expansion now duplicates only blocks actually containing `LABEL`.
4. The initial new limiter unit test incorrectly expected an impulse to survive the up/downsampling filter unchanged. Its .18963/.1 ratio differs from ideal1.99526 because of resampling, not limiting or delay. Corrected the new test to assert linear gain relative to the zero-gain **same filter chain**, while retaining exact impulse timing and hot-signal limiting tests. The stale pre-correction test ran at the end of the first fresh delivery route; the final test file was copied and rerun in that worktree, passing3/3. No master/check was rerun because its inputs were unchanged.

These are local reproducibility results, not a claim that Devin Review passed or that the audio was human-auditioned.
