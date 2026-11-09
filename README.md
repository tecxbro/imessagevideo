# iMessage video reconstruction work

**Status: incomplete. These are working reconstructions and evidence, not verified1:1 copies.**

The request was six references implemented separately in Figma Motion, Remotion and GSAP:18 film/method implementations. The delivered work contains only3 full implementations in that requested matrix (Figma01, Remotion03, GSAP06), plus4 Python/Pillow fallback films.15 requested combinations remain unstarted. This repository records that gap explicitly.

## Start here

- [Method-by-method status](docs/methods-matrix.md)
- [Confirmed failures and evidence](docs/failure-evidence.md)
- [Installed reconstruction skill source](skills/reconstruct-message-motion/SKILL.md)
- [Original action journal](process/steps.md)
- [Visual diagnosis](motion-root-causes.html)
- [Original delivery/review report](reconstruction-report.md)

The prior review labels in process/ and project QA files are historical and scoped to their named frames/hashes. The later diagnostics identify real remaining bugs; a former scoped pass does not mean visual identity or smooth motion throughout.

## What is in this repository

- projects/: editable source for all six delivered films and the additional native Figma snapshot.
- skills/: the actual portable installed reconstruction skill and provenance.
- diagnostics/: root-cause, dense consecutive-frame measurements, plots and controlled single-frame tests.
- videos/: the seven delivered exports.
- comparisons/: six complete frame-index-aligned reference/rebuild comparison films.
- references/: the six original analysis inputs, marked as references rather than authored work.
- evidence/ and process/: measurements, review results, logs, dependency manifests and packaging utilities.
- archives/: an index of additional persisted recovery/experiment artifacts; they are not counted as completed requested-method implementations.

Some large binary payloads may be stored as reconstructable chunks. The media manifest and materialization command are added with the source import; the small bootstrap commit alone is not the complete export.

## Rendering

See [START-HERE.md](START-HERE.md) for each project entry point. Supply licensed local SF Pro fonts as documented; proprietary SF Pro binaries and installed node_modules are excluded. The dependencies are pinned in package.json/package-lock.json and project requirements files. Browser renderers default to one rendering worker where the tested full export required it.

## Reusable skill

[Reconstruct Message Motion](https://chatgpt.com/skills?skill_id=6af0ae97bf208191a10bf98ae79a5337) is installed. Its actual10 source files are copied under skills/reconstruct-message-motion/ with hashes and original commit218e6f6. The skill describes a workflow; its existence and helper tests do not prove that the18 requested reconstructions were completed or that the movies meet1:1 fidelity.

## Source preservation

Rene preserves original live action/audio only at source frames1049–1229 inclusive, following the instruction to leave live action alone. Graphics outside that interval are authored. Original footage appears separately in references/ and comparison evidence; it is never presented there as a newly authored reconstruction.