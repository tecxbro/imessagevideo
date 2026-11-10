# Historical migration attempts

These files document abandoned approaches and are not normal setup tools.

- Git LFS rejected the first object with an account-budget error. No billing
  setting or repository visibility was changed.
- A draft GitHub Release was created. Draft tags required release-list lookup;
  this older gh version also lacks `api --slurp`. Its upload endpoint then
  rejected the available credential with HTTP 401. No asset upload succeeded.
  The empty draft release was deleted by its observed ID, 440168960.
- The final library uses ordinary Git with the already verified 24 MiB parts.
  `tools/sync_library.py` performs purely local checksum-based reassembly.

The old plan and source are kept as history because the user requested all
authored work. Do not execute these superseded publisher/downloader prototypes
as a substitute for the current local workflow.
