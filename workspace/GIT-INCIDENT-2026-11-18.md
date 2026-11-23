# iMessage video trial incident

November 18, 2026 · GitHub repository [tecxbro/imessagevideo](https://github.com/tecxbro/imessagevideo)

## What happened

At about 8:08 a.m. Pacific, Activity Monitor showed 102 Git processes using roughly four CPU cores. The process tree showed 34 detached `git maintenance run --auto` jobs. Each had a `git repack` child and a `git pack-objects` worker. One sampled job had been running for over five hours. The morning cleanup sent a termination signal to the 34 workers, then verified that all 102 processes had exited. [Process snapshot and cleanup log](<../../../.codex/sessions/2026/11/18/rollout-2026-11-18T08-05-28-01a1ef67-ed28-7ba1-a2a0-1b7bc664413d.jsonl>)

Several trials started on the same Mac and tried to restore the same multi-gigabyte library. When full transfers stalled, runs tried partial clones, retries, and archive recovery. The older `imessagevideo-motion-catalog` partial clone accumulated 84 single-object packs between about 2:43 and 3:08 a.m. Pacific and had 213 packs at inspection. The timing points to on-demand fetches repeatedly triggering background repacking. The process snapshot captured the repack jobs after they detached, so the command that launched each job is unknown. [Git partial-clone documentation](https://git-scm.com/docs/partial-clone) · [Git maintenance documentation](https://git-scm.com/docs/git-maintenance)

Workspace isolation also broke down. Multiple runs started from the same parent directory and used the default `imessagevideo` clone path. One UI checkout disappeared during a commit. The logs establish when the directory went missing, and the cause is unconfirmed. A fresh checkout recovered the code, previews, and evidence. Two UI runs had targeted the same GitHub branch, so the recovered work and the other UI trial eventually landed together. [UI recovery log](<../../../.codex/sessions/2026/11/18/rollout-2026-11-18T02-07-41-01a1ee20-5e03-7c83-a71f-3aa03c28bab1.jsonl#L778>) · [Combined UI handoff](codex-ui/HANDOFF.md)

## Repositories and checkouts

The Codex runs used one existing private GitHub repository, `tecxbro/imessagevideo`. That repository was created on November 8 Pacific time. Every related Git origin checked pointed to that same repository. The top-level `imessage-video` folder is an empty local Git repository with no commits or remote. It contains six standalone checkouts and one linked worktree. The folder occupied about 34 GiB at inspection. [GitHub repository](https://github.com/tecxbro/imessagevideo)

| Local path under `imessage-video` | Role |
| --- | --- |
| `codex-catalog/` | Motion-catalog trial |
| `codex-direction/` | Creative-direction trial and parent Git store of the library worktree |
| `codex-direction-library/` | Linked worktree at the pinned starting commit |
| `codex-sound/checkout/` | Sound setup checkout at the starting commit |
| `codex-sound/work/` | Sound trial and final mix |
| `codex-ui/` | Combined UI work and verified film library |
| `ui-trial/` | Parallel UI trial before the merge |

Earlier sibling checkouts include `imessagevideo-motion-catalog`, `imessagevideo-observer`, `imv-recreation`, `imv-creative-direction`, and `imv-sound-edit`. Those paths include separate local work. The recreation checkout has an uncommitted Poke repair that moves the restaurant selection from archived frame 645 to source frame 633. The complete editable recreation and the independent unseen-film benchmark were unfinished. [Poke timing evidence](../imv-recreation/recreation/poke/README.md)

## GitHub cleanup and recovery

The five Codex trial branches below were backed up, then deleted together in one atomic GitHub push. A fresh remote listing confirmed all five were gone. The other 13 remote heads retained the same SHAs, including `main`, the Devin and OpenAI Dots branches, and the library branches. Local checkouts and working files remain available.

| Deleted branch | Archived tip | Deliverable |
| --- | --- | --- |
| `film-trials/codex-catalog` | `a23bfb294fbc65739811a84f264ad306ca192fe1` | Four editable motion examples and six renders. [Handoff](codex-catalog/HANDOFF.md) |
| `film-trials/codex-direction` | `b303dde12ca8a314a36a7e70ed42e3e0f1605464` | *Pinch Hit* picture, alternate cut, and hold test. [Handoff](codex-direction/HANDOFF.md) |
| `film-trials/codex-observer` | `262877b84fd153d8f6471a633ab71479cfe32d0d` | Cold-view notes on *Pinch Hit*. |
| `film-trials/codex-sound` | `69595dfa2ef588a59d1b0b4d5836817a49d0f809` | Final *Pinch Hit* mix, stems, and cue checks. [Handoff](codex-sound/work/HANDOFF.md) |
| `film-trials/codex-ui` | `b525e7e11279db836bbdd2ff4b1b8953b56b946f` | Reusable conversation and attachment components plus UI trial renders. [Handoff](codex-ui/HANDOFF.md) |

The [local Git bundle](.git/branch-backups/2026-11-18-codex-film-trials.bundle) contains all five tips and the 315 Git objects introduced after base commit `c49482aec7b8ed0b840f97c61a5e5b860c4077b6`. It needs that base on restore. All five tips and all 315 objects were verified by unpacking into a temporary object store before deletion. Its SHA-256 is `4129ed51da7648e75b51590a19cde035da826a9f28007c47cd5816aad72a82d1`. The bundle covers published Git history. Uncommitted work and ignored render files are in the local checkouts.

## Preventing a repeat

1. **Prepare and verify the library once per machine.** Pin the starting commit before dispatch. The `codex-ui` checkout had all 14,855 tracked file objects at that commit, and `python3 tools/sync_library.py --verify-only` passed offline for 12 archives, 78 parts, two snapshots, and 14,161 extracted files. Give the trials paths to that verified library. [Library verification tool](codex-ui/tools/sync_library.py)
2. **Give each trial one branch owner and separate paths for edits and renders.** Use linked worktrees so Git history and objects are shared. Keep reference inputs shared and read-only for trials. Copy a specific case into its worktree when it needs editing. [Git worktree documentation](https://git-scm.com/docs/git-worktree)
3. **Keep large transfers and repacks out of parallel runs.** If a trial's inputs are missing, finish the fetch in one setup job before launching workers. Disable automatic maintenance in the trial Git store with `git config --local maintenance.auto false`. Run any needed repack as one foreground job after the trials finish. The local guard is already set in the older `imessagevideo-motion-catalog` checkout. A controlled fetch on this Mac verified that the setting prevents Git from launching automatic maintenance. [Git configuration documentation](https://git-scm.com/docs/git-config#Documentation/git-config.txt-maintenanceauto)
