# iMessage video v3.2.1 integration verdict

The package contains the central skill, shared frame clock, renderer source
and specialist workflows. The table identifies the checked specialist pins and
the commands run from the extracted skill unless a repository command is
shown. The released films are technically checked. Human listening and a
both fresh-agent blind runs are pending. This release is on the Observer
branch. The final seven-head integration requires the remaining specialist
proofs.

| Capability | Source commit | Command | Result | Remaining work |
| --- | --- | --- | --- | --- |
| Shared picture, event, UI and cue contracts | `6add29b`, `a7a70e7` | `python3 observer/imv.py smoke --method all --out /tmp/imv-renderers` | Pillow/FFmpeg, HTML/CSS/SVG, GSAP, Remotion and native Motion Canvas each produced 24 decoded frames with the named marker crossing at frame 12. The cue resolves to sample 24,120. All five also exported 30000/1001 with exact frame timestamps through 23023/30000. | Figma remains a prototype. |
| Central entry and skill packaging | `a7a70e7` plus this integration commit | `python3 observer/test_imv.py`, `python3 observer/package.py --verify PACKAGE.zip` | Ordinary reference, original brief, single motion, interaction, sound and intake requests selected the intended route. The package and member checksums verify. A clean extract exported all five renderers with the event at f12. | Fresh intake and Direction/Recreation tests are pending. |
| Portable media | This integration commit | From the release root, `sha256sum -c MEDIA-SHA256SUMS`. From the skill, `node motion/cli.mjs preview --id heading-over-fixed-photos` and `node motion/cli.mjs render --id heading-over-fixed-photos --out /tmp/heading-preview.mp4 --method pillow` | Both ZIPs rebuild byte for byte. All 90 Motion previews match their catalog hashes, decoded lengths, rates and event maps. The standalone Motion render matches the preview byte for byte and resolves f20 and f51. Both editable project manifests pass. The extracted guide's 20 links resolve. Four other movies, four images and 24 WAVs decode. | See Motion's selector results below. |
| Recreation | `de3c296` clean-runner handoff and `a8ee16a` packaged regression | At the handoff pin, `npm ci --prefix scripts/engines` and `bash recreate/verify-clean-runner.sh /tmp/recreate-clean-preflight`. From the release, `bash recreate/example/prove.sh /tmp/recreate-train`. | The editable Train scene reproduces the silent picture byte for byte in isolation. All 120 frames pass. On both clocks f119 spans ticks [60928,61440) at 1/15360. The late selection fails at f74–77 and the truncated prefix fails for missing f110–119 and the ending. | A reserved-film run is pending. |
| Direction | `84b87e0` handoff, `931fe2d` locked delivery and `1ba37bb` selected Sound A | From the Moon Cue project, `python3 direction/film/render.py --out /tmp/moon-picture.mp4` and `sha256sum -c SHA256SUMS` | The packaged project reproduces the silent lock byte for byte in isolation. The mux decodes all 360 original picture frames and passes all eight encoded cue checks. The two cold picture reviews and verified revision are recorded below. | An independent run of the second Keiki brief is pending. |
| Motion | `51fff53` | `node --test motion/tests/*.test.mjs`, `node motion/cli.mjs select --brief REQUEST` | All 64 selector, sequence and editable-output tests passed. The catalog contains 77 playable entries covering 75 distinct motions. Earlier sequence proof reset state at f72 and f144, with heading events at f92 and f123. | Two requests returned `action: missing`: “Leave the snapshots pinned while the title travels over them” and “Show a count climb to the real total then give the statistic time to read”. Motion has the reproduction and proposed fix. Native photo paging capture is pending. |
| Interaction | `5e2ff5a` | `python3 -m unittest ui.test_adapter`, `python3 -m ui.adapter ui/examples/conversation.json --out /tmp/station.scene.json`, `python3 observer/imv.py render /tmp/station.scene.json --out /tmp/station.mp4` | 136 frames at 24/1 with the reaction retained in state after scrolling. The independently edited draft clears at f19 and a retargeted f74 Wow follows its outgoing row during f80–87. | Physical-device evidence is pending for keyboard-up send, Tapback into scroll and native multi-photo paging. |
| Sound | `5c26dce` replay, `fb7a8de` retime and `1ba37bb` original A | [Clean replay commands](https://github.com/tecxbro/imessagevideo/blob/5c26dce493a9fadade4f84126f5b970c9e9fe5a9/review/imv-v3/sound/RELEASE-RECHECK.md) | All six sync checks and six quality cases passed their expected verdicts. All eight retimed cues passed. The audience landmark moved from f270 to f275, retaining +2,880 samples (+60 ms). The stale mix fails 208.333 ms early. Both regenerated timing reports matched the checked-in JSON byte for byte. | Human audition and new blind-cut scoring remain pending. |
| Fingerprints and Dataset archives | `f926ed4` manifest and `8f43aec` tool | `python3 observer/test_fingerprint.py` and repository `python3 tools/sync_library.py --self-test` | Nine fingerprint checks pass, including resizing, re-encoding, cropping, padding, an overlay, and an intro with a trimmed tail. All three reserved films match their own fingerprints and clear the other two. The two latest references match their re-encodes. Offline archive restore passes the isolated synthetic fixture. Dataset acknowledged the intake gate. | Dataset's intake rejection, requested captures, rights records and production archive registration are pending. The entry uses the Observer fingerprint workflow for now. |

## Picture review and sound measurements

In the first cold picture review, the reviewer identified the missing moon
prop, the message asking where it was, the reply pointing to a red tin and
the crescent over the rabbit. At f56–180 the Stage Crew label suggested a human
reply. Direction put “Keiki agent · iMessage” on the phone from f56, kept the
stars and tin in sight at f148–152 and cut to the sharp tabletop at f153.
The second cold reviewer followed the answer and identified the crescent
by f172 and its return to the stage from f216, with the payoff legible
before the end card fades in at f308. The lid moves before the hand enters
around f174, making its opening visually implicit. Both reviews used
decoded frames. The [boundary strip](evidence/direction-lock-strip.png)
shows the revised cuts.

The [Recreation frame sheet](evidence/recreation-contact-sheet.png) includes
the authored request at f30, drawer f56, selection f74, receipt f89 and
the final four frames. The [complete result](evidence/recreation-final.json)
and [truncation control](evidence/recreation-truncated.json) record the clocks
and comparison spans.

Sound checks independently decoded the muxed video and AAC. Cue timing,
packet integrity, PCM differences and peaks are measured. Human audition
remains pending. Earlier library playback was checked independently by
fully decoding 30 renderer exports from the six accepted source projects.

## Blind-run status

A filesystem-isolated preflight used an empty home and no GitHub credentials.
Both the Codex responses endpoint and the OpenAI Responses API failed at the
cloud proxy before authentication. Curl returned exit 56, proxy HTTP 403 and
origin HTTP 000. The agents available in this chat share the workspace.
The Recreation and Direction blind runs are pending.
The restricted skill packets and three complete reference films are staged
privately. The references were screened against the base and visible
build branches. The second product brief is grounded in the first-party
Keiki docs. No reserved input was given to a tester. Only fingerprints
go to the Dataset intake. Use a different reserved film when retesting
after an actual failed run.

## Seven-head integration gate

The release is an Observer-branch update. The `codex-main` branch awaits
Motion's updated selector proof and Dataset's intake rejection, archive
registration and independent rerun. The currently checked specialist heads
are below.

| Specialist | Exact head |
| --- | --- |
| Recreation | `de3c296ea49298fbc596de0298a6588d9c683fd6` |
| Direction | `84b87e0d6971c9cec4136acea274c35391df40ab` |
| Motion | `51fff53c936c3f2fb83566f69880e0a7a826570e` |
| Interaction | `5e2ff5a765dd105b5bdebb51bcfbe2a803e3bb71` |
| Sound | `5c26dce493a9fadade4f84126f5b970c9e9fe5a9` |
| Dataset | Awaiting a published head and production archive manifest |
