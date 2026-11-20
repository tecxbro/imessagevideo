# Messages motion evidence

The evidence target is Messages on an **iPhone 17 Pro simulator running iOS 26.0 (23A343)**, with a 402 × 874 pt viewport. The kit uses its own film graphics. The device and OS describe the reference, and the comparisons assess event order, movement, anchoring, and persistence across that reference and the editable scene. [Pinned capture specification](https://github.com/theswerd/imessage-ui/blob/1f132909792ff540501385f91d37ef20629c55b7/references/SPEC.md)

## Native recordings

All frame indices are zero-based, in decoded display order. PTS is the presentation timestamp reported by FFprobe. The scene anchor is the frame at which the corresponding state event starts. The source capture has its own clock.

| Recording under `references/ios/motion/` | Decoded size and cadence | First relevant frame | What the frame sequence establishes |
| --- | --- | --- | --- |
| `send-60fps.mp4` | 804 × 1748, 2 px/pt copy, nominal 60 fps, 299 frames | 73 at 1.233333 s | At f72 the composer is populated. At f73 its send control and draft have cleared and the tinted shape starts at the composer. At f75–84 it contracts toward the trailing edge and begins to rise. At f98 the arriving row overshoots above its stable seat. At f114 it is settled. At f134–147 the earlier delivery label moves to the new row and the new row rises. The preceding message stays at the same y during that receipt handoff. This simulator send uses SMS green. |
| `longpress-60fps.mp4` | 804 × 1748, 2 px/pt copy, nominal 60 fps, 239 frames | 82 at 1.383333 s | An outgoing bubble is the target. The first local change appears at f82, the surrounding dimming begins at f83, the context menu is visible by f90, and reaction marks are visible in the rail by f102. At f117 the lifted bubble, action menu, and reaction rail are all visible. The target and its controls share an attachment point while the transcript behind them remains in place. |
| `search-open.mov` | 1206 × 2622, 3 px/pt, variable PTS, 126 frames | 44 at 3.900 s | iPhone list search was opened with the connected keyboard. The row list rises and fades, while the search field and trailing circle keep their positions. The trailing glyph changes in place. At about +267 ms, the empty search surface is showing. |
| `search-close.mov` | 1206 × 2622, 3 px/pt, variable PTS, 116 frames | 43 at 4.048333 s | Escape closes the search surface inside one recorded frame. The list is already partly visible and raised at onset, then falls into its seat over about 292 ms. The bottom bar remains anchored. |

The sequence findings come from paired checkpoints and adjacent-frame strips. The upstream send specification adds subpixel measurements, including a roughly 5 pt vertical overshoot and a ~690 ms settle. The apparent 2× evidence is a recording size. The simulator viewport and held screenshots are @3×. [Send and long-press specification](https://github.com/theswerd/imessage-ui/blob/1f132909792ff540501385f91d37ef20629c55b7/references/SPEC.md) [Search measurements](https://github.com/theswerd/imessage-ui/blob/1f132909792ff540501385f91d37ef20629c55b7/references/ios-search.md)

| Recording | SHA-256 |
| --- | --- |
| `send-60fps.mp4` | `23a9680f70a436a119b786334aeb88c70b59c083703ef273eb0cdad2be98cf8b` |
| `longpress-60fps.mp4` | `8e8f3cf3194c5afbfd796056be5d37eb9e50b366f9931d02f092160b3d76f2ec` |
| `search-open.mov` | `eaf91eed724d810de696106ee537a32b3f231bd7e147b5ccdbafb71cfefa7948` |
| `search-close.mov` | `ea79101cd93fef25e29f62be75a8c91a1a3dc2e7f9ebc2fb92abdeb8b1b6a934` |

The pinned source describes these recordings as fixture conversations for comparison and testing. Its native media notice preserves Apple ownership. Use the local upstream checkout for source pixels and keep the comparison output in local review storage. [Third-party notices](https://github.com/theswerd/imessage-ui/blob/1f132909792ff540501385f91d37ef20629c55b7/THIRD_PARTY_NOTICES.md)

## Run a comparison

From the repo root, use Python 3.11+, Pillow 10.1+, FFmpeg, FFprobe, jq, and the kit's DejaVu fonts. Set `NATIVE` to the absolute path of `references/ios/motion` in the pinned `theswerd/imessage-ui` checkout at `1f132909792ff540501385f91d37ef20629c55b7`. Put full-picture comparisons and their PNGs outside the Git worktree.

```sh
jq '.render.conversation' review/imv-v3/ui/send-motion-trace.json > /tmp/ui-send.json
(
  cd skill/imessage-motion-recreation
  python3 -m ui.adapter /tmp/ui-send.json --out /tmp/ui-send.scene.json
  python3 scripts/engines/render_pillow.py --scene /tmp/ui-send.scene.json --out /tmp/ui-send.mp4
)
python3 skill/imessage-motion-recreation/ui/compare.py \
  "$NATIVE/send-60fps.mp4" /tmp/ui-send.mp4 \
  --reference-frame 73 --render-frame 12 \
  --reference-label 'iOS 26.0 simulator · SMS' --render-label 'Editable scene' \
  --before 12 --after 80 --out-dir /tmp/ui-send-comparison
```

Choose the anchor from the scene's event map if you changed the conversation. The command expects at least 0.2 s before and 1⅓ s after both anchors. For the context menu, use `longpress-60fps.mp4` and source frame 82. For a timing-only comparison of native search open and close, pass them in that order with reference frame 44, render frame 43, descriptive labels for both sources, and `--after 34`. For search open versus the [field-notes render](../../../review/imv-v3/ui/field-notes-pillow.mp4), use `search-open.mov` at f44, the render at f14, and `--after 22`. The 35-frame paired export retains the event-relative timestamps and shows the list moving while the bottom controls stay in place. The film panel includes its output canvas margin.

- `comparison.mp4` runs both pictures against the same event-relative clock. Each panel keeps its aspect ratio and shows its original frame and PTS. A held frame can appear multiple times if the comparison clock is faster than the input or the original recording paused.
- `checkpoints.png` shows before, action, intermediate states, and the final comparison frame.
- `reference-consecutive.png` and `render-consecutive.png` contain adjacent decoded frames around the two anchors. They retain every frame in those ranges, including VFR frames the paired output can skip.
- `alignment.json` records both input hashes, both anchors, and every comparison pair. Use it to reproduce a mismatch by frame and timestamp.

The committed trace clips show measurements from the source beside the editable scene. To regenerate both traces, run from the repo root after setting `NATIVE`.

```sh
for interaction in send context; do
  jq '.render.conversation' "review/imv-v3/ui/${interaction}-motion-trace.json" > "/tmp/ui-${interaction}.json"
  (
    cd skill/imessage-motion-recreation
    python3 -m ui.adapter "/tmp/ui-${interaction}.json" --out "/tmp/ui-${interaction}.scene.json"
    python3 scripts/engines/render_pillow.py --scene "/tmp/ui-${interaction}.scene.json" --out "/tmp/ui-${interaction}.mp4"
    python3 -m ui.trace "$interaction" --native-dir "$NATIVE" --render "/tmp/ui-${interaction}.mp4" \
      --render-frame 12 --conversation "/tmp/ui-${interaction}.json" --out-dir /tmp/ui-traces
  )
done
```

## Comparison findings

The isolated send and context runs use 402 × 874 scenes exported through Pillow/FFmpeg at 24 fps. Paired comparison clips run at 60 fps and use the decoded source frames around each event. [Send motion trace](../../../review/imv-v3/ui/send-motion-trace.mp4) [Send measurements and hashes](../../../review/imv-v3/ui/send-motion-trace.json) [Context motion trace](../../../review/imv-v3/ui/context-motion-trace.mp4) [Context measurements and hashes](../../../review/imv-v3/ui/context-motion-trace.json)

| Interaction | Shared behavior | Approximation visible in the comparison |
| --- | --- | --- |
| Send | The event commits a new row at the composer and clears its draft. The row rises with a small overshoot. In the isolated render it fully appears above the field at f12 and reaches its first seat at f28, with an optical top around 4 px above that seat at f22. At f36 the receipt moves from the previous outgoing row to the new row. The new row rises 16 pt and the previous row stays in place. | The film row begins immediately above the field at its text-driven width. The native capture starts inside the field as a broad tinted shape and contracts. The short film transcript puts its new row higher than the native seat. |
| Long press | The selected message lifts independently and retains contrast as neighboring rows dim. The action panel and then the reaction controls appear. In the isolated render the selected row's optical top moves from 662 to 594 px. The track holds a 7 pt panel gap beneath the selected row throughout the lift and leaves other rows in their transcript positions. | The film uses its own combined panel and makes the lift distance depend on available space. The reference uses separate reaction and action surfaces and a backdrop blur. |
| Search | In the paired opening sequence both lists rise and fade with the bottom control in place. The native open and close clips provide the source clock for the return. | The film heading persists when the list leaves. The native heading fades with the rows and its trailing action changes glyph over several frames. A native indexed-result journey remains an evidence gap. |

The send trace's optical top and width include the visible green composer echo and tail. The context trace plots a fixed backdrop patch. Its mean RGB channel value is 252 at onset, 207 by f90, and 197 by f120. Use the local full-source comparison to check shape, opacity, and other features outside those measurements.

## Other sources and open capture requests

The repository's six `projects/*/imessage-recreations/references/*/source.mp4` videos are launch-film evidence. Source contacts sampled every 2 seconds show six distinct uses of message geometry and camera framing.

| Original film | Visible passages from the source contacts | Application to the kit |
| --- | --- | --- |
| Photon 2.0 | 8–14 s, service-specific bubble fields and title-led montage | Treat bubbles as independent objects for montage. |
| Daniel Tian | 4–8 s, composer to phone transcript. 22–32 s, group participants and cards | Keep sender identity and group adornments attached as transcript reflows. |
| Photon Mini Apps | 4–12 s, card to detail screen. 16–30 s, group thread, card content, full-screen transitions | Preserve attachment identity through inline and expanded presentation. |
| Poke | 4–10 s, bubbles, schedule and food choices. 16–30 s, map, restaurant cards and voice attachment | Make rich message payloads replaceable independently of cinema camera and transcript. |
| Linq | 8–18 s, travel cards and detail surfaces. 22–36 s, payment, game and menus | Treat product-specific cards and sheets as authored content. |
| Rene | 2–8 s and 16–26 s, conversation framed by phone hardware. 34–40 s, chat over live action | Keep the camera outside the screen layout so film framing can change independently. |

The project source cadence, camera and editing make those clips suitable for film grammar. Device and build provenance are unknown for those passages. [Launch-film source index](../../../PROJECT-HANDOFF.md)

The native source also offers held screenshots and a checkpoint ledger. The 402 pt iOS photo-picker example sends three separate bubbles in one picker action. A horizontal gesture inside a stacked attachment still needs a separate recording. The search captures demonstrate blank focus and return to the list. Opening an indexed result remains a capture request. [Photo capture manifest](https://github.com/theswerd/imessage-ui/blob/1f132909792ff540501385f91d37ef20629c55b7/references/ios/manifest.json) [Simulator checkpoints](https://github.com/theswerd/imessage-ui/blob/1f132909792ff540501385f91d37ef20629c55b7/references/ios/motion/simulator-checkpoints.json)

Apple's versioned guide documents direct replies, scheduled sends, media, polls, reactions and delivery surfaces. Apple also confirms group typing indicators, conversation backgrounds and group payments for iOS 26. These descriptions establish feature semantics. Frame timing, bounce curves and scroll ownership require recordings. [iOS 26 feature list](https://www.apple.com/newsroom/2025/06/apple-elevates-the-iphone-experience-with-ios-26/) [Send and reply](https://support.apple.com/guide/iphone/send-and-reply-to-messages-iph82fb73ba3/26/ios/26) [Unsend and edit](https://support.apple.com/en-gb/guide/iphone/iphe67195653/26/ios/26) [Audio messages](https://support.apple.com/en-bw/guide/iphone/iph2e42d3117/26/ios/26) [Read receipts](https://support.apple.com/guide/iphone/turn-read-receipts-on-or-off-iph5e713a045/26/ios/26) [Specific replies](https://support.apple.com/en-ie/104974)

| Starting state | Action | Ending state and layer check |
| --- | --- | --- |
| Visible draft with the software keyboard up on a physical iPhone in iMessage | Send a draft, with the whole keyboard and last two messages in frame | Draft clears, outgoing row settles and keyboard remains visible. Capture the later receipt if it appears. |
| Physical iPhone, a visible message in a long iMessage thread | Open the reaction picker, apply a Tapback, and scroll without a cut | Keep the marked bubble in frame so badge, message and fixed chrome can be tracked through scroll. |
| iMessage conversation open on two physical devices | Remote party types, pauses, sends a long multiline message | Typing indicator gives way to the same sender's row. Record the composer, previous last row, and receipts throughout. |
| Group iMessage conversation with two remote typists | Start both drafts, send one, then dismiss the second draft | Identify each typing indicator and watch how the first send affects the remaining indicator and transcript seat. |
| Long group transcript with reactions, an inline reply and keyboard hidden | Scroll back, pull sideways to reveal timestamps, and let go | Check which labels follow each row, which layers stay screen-fixed, and whether the app restores the same scroll anchor. |
| Native multi-photo message with multiple pages present | Swipe between pages, then open the next photo and dismiss | Confirm which region owns horizontal motion, the persistence of the page, and what happens to the conversation header and composer. |
| Outgoing text with a reaction near the screen edge | Long-press, select Edit, replace with longer copy, then undo send on another outgoing message | Follow message ID, receipt, attached reaction, reply references and transcript reflow through both actions. |
| Conversation list with a known matching indexed message | Tap search, type query, open a result and go back | Record search field, keyboard, the opened conversation's scroll position and whether query state survives. |
| Open conversation with composer at rest | Open plus tray, choose Photos, stage attachments, dismiss picker and reopen | Check ownership of the picker, keyboard, staged content and preserved draft. |
| Approved test payment request visible in a test thread | Open the payment UI, capture approval, dismiss, then wait for the provider result | Capture the pre-action card, approval surface, complete return to the thread, and authoritative test result. Record test-mode evidence and redact participant or provider secrets. |

The [standalone sequence kit](../../../review/imv-v3/ui/sequences/README.md)
demonstrates these three behavior checks from decoded authored frames with
edited inputs. The [payment evidence ledger](../../../review/imv-v3/ui/sequences/PAYMENT.md)
records observed editorial states and the test mock at each matching stage.
On November 20, 2026 Pacific time, the
[request to Dataset](https://github.com/tecxbro/imessagevideo/issues/7#issuecomment-7052500167)
asked for continuous footage and provenance for all four sequences.

For new evidence, retain the original file, device and exact build, logical viewport and pixel scale, capture method, source and reuse terms, SHA-256, and a frame or time window with rest before activation and after settlement. Record the input method, theme, text size setting, delivery service, and any external camera motion.
