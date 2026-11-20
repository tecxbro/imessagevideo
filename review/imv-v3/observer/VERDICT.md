# iMessage video v3 integration verdict

The package contains the central skill, shared frame clock, renderer source
and specialist workflows. The table identifies the checked specialist pins and
the commands run from the extracted skill unless a repository command is
shown. The released films are technically checked. Human listening and a
fresh-agent blind run are pending.

| Capability | Source commit | Command | Result | Remaining work |
| --- | --- | --- | --- | --- |
| Shared picture, event, UI and cue contracts | `6add29b`, `a7a70e7` | `python3 observer/imv.py smoke --method all --out /tmp/imv-renderers` | Pillow/FFmpeg, HTML/CSS/SVG, GSAP, Remotion and native Motion Canvas each produced 24 decoded frames with the named marker crossing at frame 12. The cue resolves to sample 24,120. All five also exported 30000/1001 with exact frame timestamps through 23023/30000. | Figma remains a prototype. The build-room Dataset acknowledgment is pending. |
| Central entry and skill packaging | `a7a70e7` plus the integration commit | `python3 observer/test_imv.py`, `python3 observer/package.py --verify PACKAGE.zip` | Ordinary reference, original brief, single motion, interaction, sound and intake requests selected the intended route. The package and member checksums verify. | Fresh-agent verification is pending. |
| Recreation | `a8ee16a` | `bash recreate/example/prove.sh /tmp/recreate-train`, `python3 recreate/qa/adversarial.py --out /tmp/imv-recreate-qa` | The editable Train scene reproduces the accepted silent picture. All 120 frames pass, including the booking receipt and hold through f119. The late selection fails at f74–77. A zero-error 110-frame prefix fails for the missing f110–119 and ending. All 15 adversarial cases return their intended verdicts. | A reserved-film run is pending. |
| Direction | `db8c0ba` picture and `1ba37bb` selected Sound A | From the Moon Cue project, `python3 direction/film/render.py --out /tmp/moon-picture.mp4` and `sha256sum -c SHA256SUMS` | The project with pinned UI source reproduces the silent lock byte for byte in isolation. The mux decodes all 360 original picture frames. The two cold picture reviews and verified revision are recorded below. | An independent run of the second Keiki brief is pending. |
| Motion | `37b72e8` | `node --test motion/tests/*.test.mjs` and `node motion/cli.mjs scene --ids conversation-handoff,heading-over-fixed-photos,conversation-handoff --out /tmp/imv-sequence.json` | All 64 selector, sequence, and editable-output tests passed. The catalog contains 77 playable entries covering 75 distinct motions. The 95 reviewed MP4s all decoded. The two shot boundaries at f72 and f144 reset state, and the heading events at f92 and f123 have null UI. | The native photo paging capture is pending. Two plain-language selector misses have a verified explicit-ID fallback and a proposed patch sent to Motion. |
| Interaction | `5e2ff5a` | `python3 -m unittest ui.test_adapter`, `python3 -m ui.adapter ui/examples/conversation.json --out /tmp/station.scene.json`, `python3 observer/imv.py render /tmp/station.scene.json --out /tmp/station.mp4` | 136 frames at 24/1 with the reaction retained in state after scrolling. The independently edited draft clears at f19 and a retargeted f74 Wow follows its outgoing row during f80–87. | Physical-device evidence is pending for keyboard-up send, Tapback into scroll and native multi-photo paging. |
| Sound | `1ba37bb` | `python3 sound/example.py /tmp/imv-sound` and `python3 sound/quality_controls.py /tmp/imv-sound-quality` | Six sync cases and six audio-quality controls return their expected results. The selected Moon Cue mix passes eight decoded cues with 0.0 ms measured error and −4.14 dBTP. The four Train effects land within 0.021 ms of their intended offsets. The stale seat cue fails at +166.688 ms. | Human audition is pending. |
| Fingerprints and Dataset archives | `8f43aec` tool; integration commit for the current fingerprints | `python3 observer/test_fingerprint.py` and repository `python3 tools/sync_library.py --self-test` | Nine fingerprint checks pass, including resizing, re-encoding, cropping, padding, an overlay, and an intro with a trimmed tail. Offline archive restore passes the isolated synthetic fixture. | Dataset's intake rejection, requested captures, rights records and production archive registration are pending. The entry uses the Observer fingerprint workflow for now. |

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

A network-isolated workspace mounted only the extracted package and its
runtime, with an empty home and no GitHub access. In a neutral test, a
fresh Codex CLI created a thread and reached turn initialization. It
could not reach the model endpoint. The ordinary provider request is
blocked by the cloud proxy before authentication. Fresh agents in this
chat share the workspace and connector permissions. Blind runs are pending.
The inputs and restricted skill packets are staged privately. No reserved input was given to a tester. The second product brief is
private and grounded in the first-party Keiki docs. One complete, previously unused iMessage film is sealed. Two additional complete films remain pending after screening candidates for source overlap and coverage. Only fingerprints go
to the Dataset intake. Use a different reserved film
when retesting after an actual failed run.
