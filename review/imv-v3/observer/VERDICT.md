# iMessage video v3.3.0 integration verdict

The package contains the central skill, shared frame clock, renderer source
and specialist workflows. The table identifies the checked specialist pins and
the commands run from the extracted skill unless a repository command is
shown. The released films are technically checked. Human listening and a
both fresh-agent blind runs are pending. This release joins the verified
Observer and six specialist heads in `codex-main`.

| Capability | Source commit | Command | Result | Remaining work |
| --- | --- | --- | --- | --- |
| Shared picture, event, UI and cue contracts | `6add29b`, `a7a70e7` | `python3 observer/imv.py smoke --method all --out /tmp/imv-renderers` | Pillow/FFmpeg, HTML/CSS/SVG, GSAP, Remotion and native Motion Canvas each produced 24 decoded frames with the named marker crossing at frame 12. The cue resolves to sample 24,120. All five also exported 30000/1001 with exact frame timestamps through 23023/30000. | Figma remains a prototype. |
| Central entry and skill packaging | `a7a70e7` plus this integration commit | `python3 observer/test_imv.py`, `python3 observer/package.py --verify PACKAGE.zip` | Ordinary reference, original brief, single motion, interaction, sound and intake requests select the intended route. The entry also recognizes requests about a moving heading, pinned pictures and a reading hold. The package and member checksums verify. A clean extract exported all five renderers with the event at f12. | Fresh intake and Direction/Recreation tests are pending. |
| Portable media | This integration commit | From the release root, `sha256sum -c MEDIA-SHA256SUMS`. From the skill, `node motion/cli.mjs preview --id heading-over-fixed-photos` and `node motion/cli.mjs render --id heading-over-fixed-photos --out /tmp/heading-preview.mp4 --method pillow` | Both ZIPs rebuild byte for byte. All 90 catalog Motion previews match their hashes, decoded clocks and event maps. Both project manifests and all 43 guide links pass. The standalone heading render matches the preview byte for byte with events at f20 and f51. The guide's Train retime command reproduces the separately verified mux. | Human listening is pending. |
| Recreation | `d5e3d43` Train retime, `de3c296` clean-runner handoff and `a8ee16a` packaged regression | At the handoff pin, `npm ci --prefix scripts/engines` and `bash recreate/verify-clean-runner.sh /tmp/recreate-clean-preflight`. Rebuild the retime using its [editable config](https://github.com/tecxbro/imessagevideo/blob/d5e3d43c578c1ef0215922ebe3066919512d8c39/review/imv-v3/recreate/sound-retime-test/README.md). | All 120 frames pass, with f119 at [60928,61440) on both 1/15360 clocks. The late selection fails at f74–77 and the truncated prefix fails for f110–119 and the ending. The retimed scene reproduces its revised silent MP4 and event map. | A reserved-film run is pending. |
| Direction | `84b87e0` handoff, `931fe2d` locked delivery and `1ba37bb` selected Sound A | From the Moon Cue project, `python3 direction/film/render.py --out /tmp/moon-picture.mp4` and `sha256sum -c SHA256SUMS` | The packaged project reproduces the silent lock byte for byte in isolation. The mux decodes all 360 original picture frames and passes all eight encoded cue checks. The two cold picture reviews and verified revision are recorded below. | An independent run of the second Keiki brief is pending. |
| Motion | `e022c94` with selector fix `05f2238` | `node --test motion/tests/*.test.mjs`, `node motion/cli.mjs select --brief REQUEST` and the [handoff commands](https://github.com/tecxbro/imessagevideo/blob/e022c94e3f06a98379c25ab4e7fde194ec4708a2/review/imv-v3/motion/v3.2/README.md) | All 68 tests passed. Snapshots selects `heading-over-fixed-photos`, and count-and-read selects `metric-count` with a numeric content file. The rendered counter matches the published SHA with action at f10 and hold at f55. Interaction independently reproduced both and confirmed the focused swipe at the final pin. | Native photo paging capture is pending. |
| Interaction | `ce1b5bd` | `python3 -m unittest ui.test_adapter` and `python3 -m ui.sequence_proof --out-dir /tmp/ui-sequences` | All four adapter tests passed. Seven 24 fps clips with original and edited keyboard-up send, Tapback scroll and photo paging, plus the labeled payment mock, reproduced all 22 artifact checksums. Motion independently reran the proof. | Physical-device evidence is pending for keyboard-up send, Tapback into scroll, native photo paging and the provider payment result. |
| Sound | `c57226b` latest, with Train retime `5e5a2a0` and Moon Cue retime `fb7a8de` | [North Quay replay](https://github.com/tecxbro/imessagevideo/blob/c57226bc6759f2b757f927e54600712480ca62ce/review/imv-v3/sound/north-quay/README.md) and [Train retime replay](https://github.com/tecxbro/imessagevideo/blob/5e5a2a077d29e605ee4c7a44037068d79edede9f/review/imv-v3/sound/recreation/owner-retime/README.md) | North Quay A, B and variable-rate remap reproduce their muxes and reports. Its stale confirmation fails 200 ms early. Train f84 preserves +432 samples, measures +0.021 ms, and fails −333.312 ms in the stale control. The earlier Moon Cue retime retains +2,880 samples at f275 and passes eight cues. | Human audition and new blind-cut scoring remain pending. |
| Fingerprints and Dataset archives | `bf7d0fa` intake and `f926ed4` fingerprint policy | `python3 datasets/imessage/prove.py`, `python3 observer/test_fingerprint.py` and `python3 tools/library.py where dataset` | The private transformed reserve was excluded by a visual match. Dataset passed six fail-closed cases, clean restore of both authorized fixtures, idempotent registration and corrupt-part rejection. The two archives register and restore through the local library. | Native and provider-confirmed captures are pending. Both GitHub Actions branch runs returned `startup_failure` before creating jobs. The weekly workflow remains inactive on the default branch. |

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
origin HTTP 000. A saved Default environment with an empty repository list
is runnable, but the current thread lacks the create-thread control needed
to launch a separate app-managed runner. The agents available in this chat
share the workspace. The Recreation and Direction blind runs are pending.
The restricted skill packets and three complete reference films are staged
privately. The references were screened against the base and visible
build branches. The second product brief is grounded in the first-party
Keiki docs. No reserved input was given to a tester. Only fingerprints
go to the Dataset intake. Use a different reserved film when retesting
after an actual failed run.

## Seven parent commits

Observer is the first parent. Each of the six specialist directories and
review trees matches its checked pin. Both Sound retimes and the variable
clock proof are retained.

| Specialist | Exact head |
| --- | --- |
| Observer | `d07bbae7c43cfcbf5182fff1a1d34e652a72c150` |
| Recreation | `d5e3d43c578c1ef0215922ebe3066919512d8c39` |
| Direction | `84b87e0d6971c9cec4136acea274c35391df40ab` |
| Motion | `e022c94e3f06a98379c25ab4e7fde194ec4708a2` |
| Interaction | `ce1b5bd13c893c117fb894d16152d63d1a11146b` |
| Sound | `c57226bc6759f2b757f927e54600712480ca62ce` |
| Dataset | `bf7d0fa6e63c9f65cf41b9d6001dac33eab2f15e` |
