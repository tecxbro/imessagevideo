# Finish the full recreation

Record what would disprove each shot before proposing a full render. Use an
inclusive window for each consequential property, including the entrance,
fastest change, held pose and exit when they differ. Record target values and
tolerances where they can be measured. Inspect intermediate frames to decide
where a shared transform or interpolated curve is justified.

## Run the repair loop

1. Use the decoded benchmark or first failed probe to test each written
   criterion. Preserve a failing artifact for the check. Keep an open list of
   every failed and unverified check across the film. An improvement in an
   error score leaves the original check open until it passes.
2. Identify the first boundary where the result diverges. Compare the source
   measurement to the scene's evaluated position, state or layer order at
   that frame. If the evaluated state is right, compare the asset or lossless
   composite to the reference before comparing it to the encode. Test the
   smallest change that establishes the cause.
3. Fix the responsible input or representation. Measure directly when a
   curve or shared layer misses the required window. Separate children or
   use explicit poses for independently changing geometry. Test a different
   asset or compositor when the isolated composite cannot meet the target.
   If a failure persists after a targeted retry, change the measurement or
   authoring method instead of repeating the same adjustment.
4. Check the failed window on the revised encode and the frames on either
   side. Recheck shots that share a changed layer, asset or renderer. Keep
   successful evidence for unchanged inputs during local repairs. On the
   complete revised encode, verify the planned checks against that file.

A full benchmark may be useful for finding failures. When the request is to
finish a recreation, keep the repair list open until every planned criterion
passes. If the work is blocked, identify the concrete missing input or
capability and the affected checks. Report a partial result as such.

## Lock and verify the review

Save the plan before authoring and use the same one across attempts. For a
repair, do this before changing the baseline. Record and recheck any necessary
plan revision against the baseline. Use SHA-256 for every hash below. A plan
has this shape, with all IDs and properties taken from the current film.

```json
{
  "reference_sha256": "<reference movie hash>",
  "comparison_checks_sha256": "<checks.json hash>",
  "frame_count": 120,
  "rgb_diagnostics": ["whole_frame_mae"],
  "shots": [
    {"id": "opening", "frames": [0, 119], "checks": {
      "panel-entry": {"frames": [26, 33], "region": "panel-entry", "target": "Panel absent at 26, visible at 27, settled at 33 at the measured bounds."},
      "last-hold": {"frames": [112, 119], "target": "Settled panel and copy stay legible through frame 119."}
    }}
  ]
}
```

The shot spans partition the whole film. A check's frames are the inclusive
window reviewed for that property. `comparison_checks_sha256` can be `null`
when using the comparator defaults. Mark a whole-frame, tile or named region
RGB check diagnostic only when its numeric result is informational. Clock,
geometry, audio and incomplete comparison failures block completion. A linked
`region` points to a check in the comparison settings covering the criterion's
entire window. Use one for each small visible UI component and critical motion
passage. Pixel equality always gates a one-to-one review.

```sh
python3 recreate/recreate.py compare "$REFERENCE" "$CANDIDATE" \
  --exact --crops --pairs --checks work/checks.json --out work/final-check
python3 recreate/recreate.py prepare-review --plan work/review-plan.json \
  --comparison work/final-check/report.json --out work/visual-review.json
```

Exit 1 from compare still writes the comparison and evidence. Start with the
failing regions and view each crop and adjacent frame pair. Keep the generated
hashes in the review JSON. Enter observations in `results` after opening the
evidence. Use a fresh review and comparison after every candidate change.

For the actual candidate, record `plan_sha256`, `candidate_sha256`, and
`results`. In `results`, key by shot ID and then check ID. Each reviewed check
contains `verdict` (`pass`, `fail`, or `unverified`), the inclusive `frames`
actually inspected, an `observation`, and an `evidence` file path relative to
the review JSON. For a reviewed failure, the evidence may cover the failing
portion. For a pass, it must cover the planned window. Omitted checks remain
unverified. Cite the precise crop, measurement or decoded pair in the
observation. Use a local artifact containing that evidence.

```sh
python3 recreate/recreate.py verify-review "$CANDIDATE" \
  --plan work/review-plan.json --review work/visual-review.json \
  --comparison work/final-check/report.json --out work/acceptance.json
```

In the default exact mode, exit 0 requires every decoded picture pixel and
every frame time including the final hold to match, plus every required
comparison and observed criterion to pass. Exit 1 lists open checks, shots
with differing pixels and required comparison failures.
Exit 2 means the inputs are invalid or belong to a different plan, checks file,
reference or candidate. Use `--scoped` only for a narrower target agreed with
the user or to reproduce a historical scoped review. It reports
`SCOPED_PASS` when that scope passes. Report the renderer, scope and actual
decoded equality result with the deliverable.
