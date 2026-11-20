# Dataset verification

`python3 datasets/imessage/prove.py` ran locally with Python 3.12.14,
Pillow 11.3.0 and FFmpeg 7.1.5. The GitHub Actions workflow runs the same
command on Ubuntu 24.04 and Python 3.11.

| Check | Local result |
| --- | --- |
| Pinned Observer controls | All nine passed. Resized/re-encoded, cropped/padded/watermarked and intro/tail variants were excluded. |
| Intake exclusion | A generated exclusion was added to the three pinned production fingerprints. Its resized 30 fps re-encode had a different SHA-256 and was blocked by a visual match (exit 1). |
| Intake blocking | Missing rights, incorrect media hash, incorrect decoded PTS, absent approval, stale approval, and malformed exclusions returned exit 2. No registry was created for those controls. |
| Registration and clean restore | Registered the authorized chart. A retry reproduced the same receipt. Restored the chart and the offline payment test from a fresh, detached sparse worktree. The command re-decoded their exact frame ranges and reran the pinned gate. |
| Split archives | Lowered the part ceiling in the isolated test to exercise full reassembly and hash validation on small payloads. A corrupt part blocked restore. Production archives use a 24 MiB ceiling. |
| Payment fixture | Browser driver confirmed dialog and result states at every frame and same-card identity. FFmpeg fully decoded all 96 frames. Contact sheets covering the four boundaries confirmed card, approval, dismissal, and separate result. |
| Workflow | YAML validated with `actionlint` and `@action-validator/cli`. Both action pins were checked against their release tags. |

The fixture restore media hashes are recorded in the two registry manifests.
The QA chart archive SHA-256 is
`3d530d4634cf2aed1bab73a8f34ac2b4d3e1cc1d7e252b2e38abdab7aa3d812c`
and the offline payment archive SHA-256 is
`bb97f06de7319044cf3ab5de5b74cc165c7d1415c4dad9f97f66e8409ab68da2`.

The same proof also passed in a fresh shallow, sparse clone of the pushed
branch, including the on-demand Observer fetch.

The initial [GitHub-hosted branch run](https://github.com/tecxbro/imessagevideo/actions/runs/44834271982)
returned `startup_failure` before creating any jobs. GitHub declined a rerun
of that run. The diagnostic retry removes branch push path filtering and
keeps the weekly trigger and proof command.

The workflow has a branch push check and a Monday 16:23 UTC schedule.
Scheduled runs and manual dispatch depend on the workflow file reaching the
default branch. The scheduled proof checks committed material and produces
pass/fail evidence in its log. Capture acquisition and grants are handled
by the Dataset maintainer.

Observer can run a second transformed-match check using the privately held
input and the pinned Observer CLI in their isolated workspace. Share only
the status and match method. The public team proof uses the generated
exclusion and includes no reserve metadata or media.
