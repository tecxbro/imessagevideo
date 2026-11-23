# Observer-run test for an unseen film

Use two clean sessions with the same source movie, editor, brief, model, reasoning level, asset policy and approved asset bundle, machine class, and time/token/render limits. Freeze those details, pinned engine hashes and the acceptance thresholds before either session starts. Run in isolated directories with the source plus only the allowed inputs visible. Exclude the fixture's solution, labels, previous attempts, curated render, and evaluator data. Neither builder sees the other run. Both can view the original throughout.

The control receives the skill from the recorded base SHA. The treatment receives the skill and new verification aid from the tested commit. Both receive the same renderer, system instructions, and task prompt. Do not include this branch's worked examples or Poke patch in the builder packets. If a clean asset pack cannot be prepared without leaking the answer, the fixture remains pending.

Use a shared brief with a concrete editor and acceptance bar, for example:

> Reconstruct the supplied full movie in the requested editor. Deliver an editable project, finished export, and evidence of timing, visual differences, independent sound, and editability. Use only the supplied approved assets or independently created assets. Keep the first complete export and record each later attempt.

The observer assigns masked labels after freezing first complete exports and privately records which is which. Review first attempts before feedback. Use the same grading criteria, feedback allowance, and time budget. Hide treatment labels, builder notes that identify the skill, and change logs until the observer locks grades. Supply anonymized layer-edit instructions separately when checking editability. Grade first and final exports and log reviewer time independently.

| Dimension | Evidence the observer records |
| --- | --- |
| Decoded identity | Dimensions, orientation, count, rational cadence or PTS mapping, final hold, all-frame residuals, native local differences, and whether decoded pixels are identical |
| Interaction | Event ID, first divergent frame, source and candidate onset/settle, reading hold, local layering/masking, camera alignment and unaffected controls |
| Sound | Provenance, independent cue match, audio/picture offset, audible differences, channel/peak/duration checks and any unavailable listening |
| Editability | Verify live text and event timing by modifying one of each, reopening the project, exporting again and decoding the changed result. Record any bounded raster assets or hybrid steps. |

For each attempt freeze the export and file hashes. Record `masked_run_id, attempt, stage, elapsed_s, local_renders, full_renders, interventions, reviewer_minutes, event_id, first_divergence_frame, cause, changed_variable, outcome`. Count renders that ran, including failed renders. Record what triggered each human intervention. Preserve tool timings and separate machine execution from reviewer time.

Compare iteration and elapsed time at the same preset quality bar. Name the exact film, editor, commits, grades and budget. Poke is a known-defect regression. Public development references are useful for debugging the workflow and must be excluded from the blind claim.
