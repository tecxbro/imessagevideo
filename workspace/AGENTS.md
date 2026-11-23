# Agent Instructions

## Render disk space and cleanup

- Before starting a large render batch, check free space on the volumes that will hold scratch files and exports. Allow room for both the expected intermediates and final exports.
- Reuse existing source assets. When creating additional checkouts of the same repository, use linked Git worktrees so they share its object store.
- Keep temporary frames, previews, and render intermediates in a dedicated scratch folder for each run. Keep source assets, final exports, and uncommitted work outside that folder.
- After verifying the final export, remove only the regenerable files created by that run in its scratch folder. Preserve source assets, final exports, and all uncommitted work, including untracked work in other checkouts.
- Measure the space used by the run before cleanup and the amount recovered by cleanup. Report both figures with the render handoff.
