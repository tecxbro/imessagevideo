# iMessage film trial handoff

Start with the [skill](../../../skill/imessage-motion-recreation/SKILL.md). For local examples, first assemble the pinned library with `python3 tools/sync_library.py` (Python 3.11+). The project links below include the reproduction commands and the limits of each editable project.

| Work | Playable output or evidence | Editable inputs and reproduction |
|---|---|---|
| Motion catalog | [Three Linq clips and Solstice adaptation](motion-catalog/) | [Search, extract, adapt and render](../../../skill/imessage-motion-recreation/director/motion-catalog.md). The observer measured 19/20 rail steps within ±4 px; the specialist measured 20/20. The attachment-stack example is contrast-only. |
| Messages UI | [First cuts, reviewed film, scenes and audits](imessage-ui/); [live-editor proof](https://app.devin.ai/sessions/ae3fac8a5f2e4b16b5151ecfe48e0c97?testRecording=59981e93-b152-40b3-b18d-880c1e62dc54) | [Editable conversation and editor](../../../skill/imessage-motion-recreation/imessage-ui/README.md). Native iOS device and gesture fidelity were not verified. |
| Original direction | [Check In v3 picture](../../../projects/devin-direction-checkin-v1/renders/v3-final.mp4); Tally first, final and edit in the companion bundle | [Project, first cuts, review and render commands](../../../projects/devin-direction-checkin-v1/README.md). [Direction rationale](../../../projects/devin-direction-checkin-v1/direction/RATIONALE.md) covers the unseen Tally brief. |
| Sound and editing | Check In delivery master in the companion bundle | [Score, stems and provenance](../../../trials/sound-editing/README.md); [master recipe, hashes and decoded cue check](../../../trials/sound-editing/checkin-v3/delivery/README.md). |
| Poke recreation | [Before/after onset reports and targeted repair](../../../trials/poke-selection-onset/README.md) | [Source-backed reconstruction playbook](../../../skill/imessage-motion-recreation/references/reconstruction-playbook.md); the timing detector supports, but does not replace, native-frame review. |
| Readwise recreation | First export, reviewed 4K revision, JSON-only edit and observer recheck in the companion bundle | [Editable project and replay](../../../trials/readwise-openclaw/project/README.md), [timeline and retries](../../../trials/readwise-openclaw/LOG.md), [event inventory](../../../trials/readwise-openclaw/analysis/events.md), [hashes and probes](../../../trials/readwise-openclaw/exports/). |

The companion artifact bundle is attached to the private integration handoff
in the [integration session](https://app.devin.ai/sessions/7d0e60349ee84fee8bed08abe40381a7).
The externally delivered media are not tracked. Its `SHA256SUMS` identifies the
files and can be checked with `shasum -a 256 -c SHA256SUMS` from the bundle root.

## Independent observer verdict

Quoted from the [observer's report](https://app.devin.ai/sessions/896d66f9e62e4c5dbca2a7e932dfafec):

- **Recreation:** the revised skill did NOT improve the sealed hold-out test (B 13.39 vs A 11.41 MAE, n = 1 per arm). B was faster and its review was safer. The specialist's open Readwise trial produced a strong result, but it was not blind and was built from baseline c49482a, so it doesn't measure the revision.
- **Catalog, UI and direction:** clear wins. Blind retrieval and adaptation work, the UI substitution passes after repair, and both original-direction films pass on picture. Tally shows the direction route generalises to an unseen brief, with house-style repetition.
- **Sound:** the defect detector is strong when a reference exists (9/9) but weak without one (3/9). Every first-pass mix shipped at −34 to −40 LUFS and needed a delivery master. Add a loudness gate to the skill.
- **Overall:** the integrated skill is a net improvement for retrieval, UI and original direction, and unproven for recreation fidelity.

The [anonymized holdout index](holdout-evidence-index-anon.md) pins both skill
revisions and the trial artifacts. Trial B took about 19.5 minutes versus
26.5 for A, with one review pass versus two, but failed 83 of 129 detected
onsets at the final ±2-frame gate. It did not include the later sound and
Readwise-driven updates. The observer holds the sensitive artifacts separately;
no holdout media, source identity or raw trial logs are in Git or the bundle.
The sound trials used computational checks, not human listening.
