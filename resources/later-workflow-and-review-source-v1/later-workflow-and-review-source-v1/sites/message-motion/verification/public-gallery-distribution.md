# Public gallery repair

The original review used relative `references/...` and `deliverables/...` media URLs. Opening the HTML without the complete directory makes those files unreachable; an app's isolated HTML preview can also limit access. The user's exact failed preview could not be reproduced because the computer-use runtime failed before opening any page. This is an observed infrastructure limit, not a codec diagnosis.

The hosted replacement includes every referenced media file. All 30 reconstructed MP4s and six originals were checked with ffprobe: H.264 video, yuv420p, AAC audio, and a `moov` atom before `mdat` for progressive playback. Maximum individual video size is 13,989,115 bytes. Existing final pictures and soundtracks were reused byte for byte.

Design inspection used the public HTML/CSS of sundays.rsvp. The replacement draws on its warm ivory surfaces, restrained column grid, serif headings, neutral/chrome details, lime index markers and small pill controls. It uses original markup and graphics, system fonts, and stills extracted from the reconstructed films.

The gallery offers native controls and playsinline, no page-load autoplay, gesture-driven playback, explicit error messages with direct MP4 links, method changes that retain time, optional original comparison, single soundtrack playback, and Rene's source-to-output cut map. Only the chosen film loads; originals load on request. Every MP4 remains directly downloadable.

Eight Node checks cover normal and cut-mapped timing, invalid seeks, all five methods and all 42 media/poster paths, missing data, browser-policy and network error messages, duration formatting, and native mobile video markup. Two HTML entrypoints passed static link validation. Browser visual and interactive playback QA remains unverified because the available browser runtime failed with `the gaas-browser node_repl sandbox cannot be disabled`; no substitute browser runtime was launched.

The selected connected Site identity was created once and persisted in `.openai/hosting.json`. Public audience was set under the user's explicit instruction. The Sites workflow helper was absent from the executor and unavailable through skill resources, so ordinary Git plus a verified tar archive implements the required source/commit/archive contract. The repository credential is passed through hidden stdin, used only in process memory, and never written to Git configuration, files or logs.

The executor initially had only 155 MB free. Twenty-seven obsolete private candidate scene JSONs were losslessly archived as `.json.gz`, with raw SHA256 checks before unlinking originals and a restoration ledger in `research/historical-archives.json`. Current canonical scenes, native frame caches, original videos, final media and existing delivery ZIP were preserved.

The first source push was explicitly rejected by `artifacts_git_receive_pack_request_too_large`: 267,883,027 bytes against a 67,108,864-byte per-push limit. The server stated an identical retry would fail. The repair generated seven incremental local commits with at most 45,673,896 raw new bytes per batch, verified the final Git tree is identical to the original frozen tree, preserved the previous commit under an archive ref, and pushes each commit sequentially. Git delta window is set to zero for these already-compressed video assets, avoiding expensive unnecessary comparisons. Publication still uses the exact final pushed source state; the deployment archive bytes do not change because its complete source tree is identical.

The first bounded push was rejected locally before network transfer: a commit SHA source cannot infer a new remote branch from the short name `main`. The push refspec was corrected to `<commit>:refs/heads/main`. No repository state changed in that failed attempt.


## Transferable distribution workflow

1. Inspect actual media URLs and the environment where the review is opened. Relative asset paths require the complete directory. A generated HTML preview may have different file access from an ordinary browser. Do not call a codec broken just because a preview is blank.
2. Use a real HTTP origin for shared viewing. Preserve all media paths or generate a clean manifest; never upload only the HTML. Use fast-start H.264/yuv420p with AAC for ordinary MP4 delivery. Check each file rather than assuming an extension proves compatibility. Avoid re-encoding already-validated final media.
3. Use native controls and `playsinline`, start playback from a gesture, report rejected play promises, and provide direct MP4 links. Load only the active film and the optional comparison reference. Silence the reference by default.
4. Bind time mapping to the selected recreation, preserve current time across method switches, and test exact cut boundaries. Mark skipped source footage explicitly.
5. Read the selected hosting skill and use its native account/access/deployment tools. Persist one Site identity. Explicit public audience authorization permits setting public access; deployment alone does not imply changing audience. Keep credentials in memory and hidden stdin.
6. Keep the source tree, pushed commit, archive and deployed version aligned. If a per-push byte limit rejects a large media commit, split into incremental commits below that limit and push them in order. Qualify SHA push destinations as `refs/heads/<branch>`. Verify the final tree is unchanged. Do not retry an identical oversized push.
7. Confirm terminal deployment success and a literal production URL. Check unauthenticated page delivery and all MP4 byte-range responses against local bytes. Validate Content-Type, Content-Range and exact ranged bytes so seeking is actually supported. HTTP delivery is distinct from a browser decode/playback test.
8. When browser infrastructure fails before opening a page, record the exact failure, continue supported verification and publishing, and state that interactive playback was not retested. Do not replace the browser runtime or claim that static tests establish visual correctness.
9. Preserve earlier frozen ZIPs. An old local HTML can become a lightweight link/redirect to the successful hosted gallery while retaining its original bytes in a sibling archive. Record those post-delivery edits separately from earlier stage checksums.

Production results and the final URL are recorded separately after deployment completes, so a pending operation cannot be described as successful in a reusable instruction.
