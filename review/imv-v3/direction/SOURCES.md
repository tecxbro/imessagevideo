# Direction source audit

Checked November 19, 2026. Each of the six build-room repositories was cloned into a separate workspace and checked out at its requested revision. The four older revisions were fetched and inspected in a second clone of the base repository. External source checkouts and render intermediates live outside the delivery tree.

| Pinned source | Technique carried forward | Provenance and reuse |
| --- | --- | --- |
| `tecxbro/imessagevideo` | Reuse the five frame-addressable renderers and the native scene contract. Preserve authored text, independently editable transforms and stable event IDs through revisions. Use the accepted films to check infrastructure and load example material when the current brief calls for it. | The team repository remains private. The base supplies the existing runtime and its original asset notices. [Base and final production map](https://github.com/tecxbro/imessagevideo/blob/c49482aec7b8ed0b840f97c61a5e5b860c4077b6/FINAL-PRODUCTION.md) |
| `theswerd/imessage-ui` | The incoming and outgoing tails belong to the last bubble in a cluster. The conversation scrolls under screen-fixed chrome. Preserve those boundaries when the picture camera moves and inspect the phone at the exported crop. | Ben Swerdlow and contributors, MIT. Fonts, brand assets, preview media and native captures have separate notices. [Pinned geometry notes](https://github.com/theswerd/imessage-ui/blob/1f132909792ff540501385f91d37ef20629c55b7/docs/development.md) · [Notices](https://github.com/theswerd/imessage-ui/blob/1f132909792ff540501385f91d37ef20629c55b7/THIRD_PARTY_NOTICES.md) |
| `tecxbro/imessagedemo` | Separate the authored conversation from display and capture. Drive before/after checkpoints from one playback clock so the same transcript can be validated, edited and rendered. An authored screen only demonstrates the documented behavior depicted on it. | The pinned tree has no root license file. Used as a private implementation reference. Upstream components retain their own provenance in the vendor lock. [Pinned authoring guide](https://github.com/tecxbro/imessagedemo/blob/807e86e03e4a7e95ae6954b4a8c4dd5e031854bc/README.md) · [Upstream lock](https://github.com/tecxbro/imessagedemo/blob/807e86e03e4a7e95ae6954b4a8c4dd5e031854bc/vendor/upstream/lock.json) |
| `heygen-com/hyperframes` | A timed composition derives every visible state from its frame. Keep each cut editable with stable IDs, local asset references and explicit duration. Borrow the review loop and timing convention independently of renderer choice. | HeyGen, Apache 2.0. [Composition contract](https://github.com/heygen-com/hyperframes/blob/9813a6cbef97fffda70f5a147b87747f7e35a77b/docs/concepts/compositions.mdx) · [License](https://github.com/heygen-com/hyperframes/blob/9813a6cbef97fffda70f5a147b87747f7e35a77b/LICENSE) |
| `per-simmons/launch-video-clone` | Use `scripts/sheet.py` on the actual encoded picture to see every frame around a defect. Keep the earlier cut as evidence. Separate a movement fix from an editorial fix by asking what changes for the viewer at the cut. The script ran on the neutral starter held below. | Pat Simmons, MIT. The evidence run uses the script directly from its checkout alongside its license. [Frame-sheet script](https://github.com/per-simmons/launch-video-clone/blob/7e97ac6488eb61ca4d25affe7fc1da7cfb80b376/scripts/sheet.py) · [License](https://github.com/per-simmons/launch-video-clone/blob/7e97ac6488eb61ca4d25affe7fc1da7cfb80b376/LICENSE) |
| `serenakeyitan/awesome-ai-clonable-launch-videos` | The pinned metadata distinguishes original post, retained media, excerpt status and original runtime. Check the actual source window before inferring an opening or an ending from a catalog clip. Select independent makers by the decision under study. | Serena’s curation, prompts and code are MIT. Third-party films, logos, previews and product UI stay with their owners. [Pinned metadata](https://github.com/serenakeyitan/awesome-ai-clonable-launch-videos/blob/6a02fa07dfa5696ba3191dd905a06dbedc932e38/data/videos.json) · [Rights and removal](https://github.com/serenakeyitan/awesome-ai-clonable-launch-videos/blob/6a02fa07dfa5696ba3191dd905a06dbedc932e38/CONTRIBUTING.md#rights-and-removal) |

## Earlier trials

- The motion catalog at `a23bfb294fbc65739811a84f264ad306ca192fe1` distinguishes a clipped local photo strip, a native conversation attachment stack, a sheet and an outer-camera move. Its preserved `message-wall` misroute for a carousel request supports describing what moves, what stays fixed and where the action happens before searching for a named motion. [Motion handoff](https://github.com/tecxbro/imessagevideo/blob/a23bfb294fbc65739811a84f264ad306ca192fe1/HANDOFF.md)
- The conversation at `b525e7e11279db836bbdd2ff4b1b8953b56b946f` ties drafts, message arrivals and reflow to one authored clock. The old long-copy fixture visibly overflows and leaves send active after clearing. Recheck the draft, arrival and crop together after an edit. [UI handoff](https://github.com/tecxbro/imessagevideo/blob/b525e7e11279db836bbdd2ff4b1b8953b56b946f/HANDOFF.md)
- The sound trial at `69595dfa2ef588a59d1b0b4d5836817a49d0f809` verifies both picture identity and cue behavior. Running `sound-trial/check_export.py` on the retained Pinch Hit mix against the pinned silent picture and final `qc.json` passed with matching video packets and timestamps, zero errors, −27.1 LUFS integrated and −5.0 dBTP. Those measurements describe the historical trial export. [Sound trial and checker](https://github.com/tecxbro/imessagevideo/tree/69595dfa2ef588a59d1b0b4d5836817a49d0f809/sound-trial)
- The Pinch Hit trial at `b303dde12ca8a314a36a7e70ed42e3e0f1605464` places an attention failure precisely. Its early cut returns to the already-understood conversation crop at frame 352 and waits another 18 frames for new information. The revision shows the second person’s decision and cuts from the send at frame 352 to the occupied chair at frame 374. Its isolated alternative moves twelve frames from the earlier hold to the outcome while retaining the fixed title. Carry forward the method of changing viewer information and testing time independently. [Editorial and moving cut evidence](https://github.com/tecxbro/imessagevideo/blob/b303dde12ca8a314a36a7e70ed42e3e0f1605464/trials/pinch-hit/README.md#the-two-wagers-and-what-changed)

An additional OpenTimelineIO checkout at `f6c34bc6c3337cdd27db77c983c6074130c1c91c` describes source, visible and parent timeline ranges. Use the final picture frame clock for Sound and record any clip-local range separately. Using an exclusive end makes adjacent cuts unambiguous. The investigation introduced no new runtime dependency. [Time-range conventions](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/f6c34bc6c3337cdd27db77c983c6074130c1c91c/docs/tutorials/time-ranges.md)

## Reproduced base renders

With Node 24.22.1, Chromium 156, Pillow 13.0.0 and FFmpeg 7.1.5, all five adapters independently rendered the neutral `conversation-handoff` starter. FFmpeg decoded each output in full. Each was H.264, 960 × 540, 30/1 fps, 120 frames. An encoded overview shows the accumulated draft at frame 42, the outgoing bubble by frame 56, and the incoming reply by frame 98. Those samples describe the base starter. The fictional booking text is unrelated to the Keiki film.

| Adapter | Fresh starter MP4 SHA-256 |
| --- | --- |
| GSAP, HTML/SVG and Remotion | `e43499f928bd9f383362b1bd16d1a5545a003707b946476b963bedf2fb51c245` |
| Motion Canvas | `f9071feab8a9caca280ad7df33b2f70f34b6942008797139c17158b9d2e42030` |
| Pillow/FFmpeg | `565add02f8a85be5965fd9cdaef0af89d5d4cc0fd5f64c90e30bb3cf11a7f464` |

Each adapter also rendered frame 645 of the accepted `04-poke` scene. All five 1440 × 1080 images show the selected Zareen’s row and blue check. HTML and GSAP matched byte for byte in that checkpoint. Remotion, Motion Canvas and Pillow generated distinct PNGs. This spot check covers the indicated frame.

FFmpeg also decoded all six retained GSAP silent picture masters in full. Their frame counts in project order were 655, 1,360, 1,260, 1,283, 1,458 and 1,483. The Poke file has a 30000/1001 cadence. The other five report 30/1. The first batch loop allowed FFmpeg to consume the pipe supplying filenames. The corrective run used `-nostdin` and checked all six.

From the hydrated repository root with the pinned runtime dependencies installed:

```sh
skill=skill/imessage-motion-recreation
work=$(mktemp -d)
node "$skill/director/cli.mjs" scene --motif conversation-handoff --out "$work/source.json"
for method in gsap html remotion; do
  node "$skill/scripts/engines/render.mjs" --method "$method" --scene "$work/source.json" --out "$work/$method.mp4" || exit 1
done
node "$skill/scripts/engines/render_motion_canvas.mjs" --scene "$work/source.json" --out "$work/motion-canvas.mp4"
python3 "$skill/scripts/engines/render_pillow.py" --scene "$work/source.json" --out "$work/pillow.mp4" --aa 2
for film in "$work"/*.mp4; do
  ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height,r_frame_rate,nb_frames -of csv=p=0 "$film"
  ffmpeg -nostdin -v error -i "$film" -f null - || exit 1
done
```

For the Poke checkpoint use `projects/04-poke-complete-v1/imessage-recreations/scenes/04-poke/scene.json` as the input and add `--frame 645` with a PNG output for each engine. See the repository’s runtime instructions for dependency setup.
