# Pinned source review

| Repository | Commit | Checkout and terms |
| --- | --- | --- |
| tecxbro/imessagevideo | c49482aec7b8ed0b840f97c61a5e5b860c4077b6 | `imessagevideo-history`, local shared clone of the supplied checkout. Keep this private. The sound asset library has its own licenses. |
| theswerd/imessage-ui | 1f132909792ff540501385f91d37ef20629c55b7 | `imessage-ui`. MIT for original project code and documents. Keep LICENSE and applicable THIRD_PARTY_NOTICES.md entries. Native Apple reference material and owned marks stay under the original terms. |
| tecxbro/imessagedemo | 807e86e03e4a7e95ae6954b4a8c4dd5e031854bc | `imessagedemo`. No repository-wide license file observed. Inspect architecture and reuse ideas with original implementation unless permission covers source. |
| heygen-com/hyperframes | 9813a6cbef97fffda70f5a147b87747f7e35a77b | `hyperframes`. Apache 2.0. Keep LICENSE, applicable CREDITS and local vendor notices. |
| per-simmons/launch-video-clone | 7e97ac6488eb61ca4d25affe7fc1da7cfb80b376 | `launch-video-clone`. MIT. Keep the copyright and permission text from LICENSE. |
| serenakeyitan/awesome-ai-clonable-launch-videos | 6a02fa07dfa5696ba3191dd905a06dbedc932e38 | `awesome-ai-clonable-launch-videos`. MIT for original curation, prompts and code. Its README reserves third-party films, previews, product UI, logos and branding to their respective owners. |

The base uses a validated geometry JSON with output-second keyframes. Preserve its projection while using the canonical zero-based frame clock for authored actions. HyperFrames `packages/core/src/fps.ts` uses an exact rational timebase and treats decimal rates as ambiguous. Its skill documents frame-seek determinism, layer lifetimes with an exclusive end, local assets, stable editable IDs and lazy routes.

The iMessage demo models playback independently of wall time and folds one canonical event stream into logical UI state and active visual cues. Its browser capture checks create a readiness receipt, enforce local asset handling and expose stable checkpoint names. The Message UI project confirms interactions separately from static snapshots and records provenance alongside measured checkpoints. The Serena catalog pairs creator attribution and source links with observed technique and playable references.

The launch-video-clone comparison produces matched stills and motion energy curves. Its common-duration sampling means a separate check must cover the complete candidate and reference endings. The voice-over timing subskill uses frame-numbered beat sheets, bounded intermediate WAVs, and a separate picture-preserving mux. Its lost-last-frames example is a reason to verify decoded frame count and the final presentation interval after muxing.

Historical Git refs in `imessagevideo-history`:

- `refs/sources/motion` points to a23bfb294fbc65739811a84f264ad306ca192fe1. The directory `skill/imessage-motion-recreation/director/motion-library/` has editable defaults, preview commands, and source-specific observed and inferred details.
- `refs/sources/conversation` points to b525e7e11279db836bbdd2ff4b1b8953b56b946f. The conversation component guide and tests cover font-dependent reflow, draft/send state, tapback parenting, independent scrolling/camera groups, and consecutive frame inspection.
- `refs/sources/sound` points to 69595dfa2ef588a59d1b0b4d5836817a49d0f809. The sound checker compares encoded packets and rational packet timestamps, then decodes the delivered AAC to validate cue templates and true peak. The trial has clean and deliberately late/missing cue checks.
- `refs/sources/pinch-hit` points to b303dde12ca8a314a36a7e70ed42e3e0f1605464. HANDOFF.md pins picture hashes and frames, records cold editorial findings, and shows an isolated twelve-frame timing revision.

Further research: the MIT `akamhy/videohash` at e407bb0b26de625a846c2700072efccd9eb44e9a documents re-encode and resize resilience but explicitly excludes partial-video matching. Its crop detection across multiple intervals is a reference for normalizing pillarbox or letterbox reposts. A temporal collection of frame hashes allows alignment across a title bump or trimmed repost. Test common UI palettes as hard negatives. The local FFmpeg build includes the MPEG-7 signature filter, which matches decoded video inputs and can emit signature files.
