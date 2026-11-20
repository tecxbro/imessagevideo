# Editable interaction sequences

The seven silent clips use the authored film skin at 402 × 720 and 24 fps.
Each clip has its own resolved event map and consecutive decoded frames.
The edited versions preserve the event IDs and replace the draft, reaction
target and mark, or attachment order. The coverage map separates what the
sequences prove from the remaining device capture requests.
[Full coverage map](../../../../skill/imessage-motion-recreation/ui/COVERAGE.md)

| Sequence | Editable inputs | Playable clips | Event maps | Consecutive frames |
| --- | --- | --- | --- | --- |
| Send with the keyboard up | [Original](../../../../skill/imessage-motion-recreation/ui/examples/send-keyboard.json) · [Multiline edit](../../../../skill/imessage-motion-recreation/ui/examples/send-keyboard-edited.json) | [Original](send-keyboard.mp4) · [Edit](send-keyboard-edited.mp4) | [Original](send-keyboard.events.json) · [Edit](send-keyboard-edited.events.json) | [Original](send-keyboard-frames.jpg) · [Edit](send-keyboard-edited-frames.jpg) |
| Tapback followed by scroll | [Original](../../../../skill/imessage-motion-recreation/ui/examples/tapback-scroll.json) · [Retargeted edit](../../../../skill/imessage-motion-recreation/ui/examples/tapback-scroll-edited.json) | [Original](tapback-scroll.mp4) · [Edit](tapback-scroll-edited.mp4) | [Original](tapback-scroll.events.json) · [Edit](tapback-scroll-edited.events.json) | [Original](tapback-scroll-frames.jpg) · [Edit](tapback-scroll-edited-frames.jpg) |
| In-thread photo swipe | [Original](../../../../skill/imessage-motion-recreation/ui/examples/photos-fixed-header.json) · [Reordered edit](../../../../skill/imessage-motion-recreation/ui/examples/photos-fixed-header-edited.json) | [Original](photos-fixed-header.mp4) · [Edit](photos-fixed-header-edited.mp4) | [Original](photos-fixed-header.events.json) · [Edit](photos-fixed-header-edited.events.json) | [Original](photos-fixed-header-frames.jpg) · [Edit](photos-fixed-header-edited-frames.jpg) |
| Payment test mock | [Mock input](../../../../skill/imessage-motion-recreation/ui/examples/payment-mock.json) | [Clip](payment-mock.mp4) | [Event map](payment-mock.events.json) | [Frames](payment-mock-frames.jpg) |

## Visible boundaries

- Send, 68 frames. At f17 the draft is visible. At f18 the composer clears
  while the new blue row first appears, then settles by f34 with its right
  edge at x384. The 208 px keyboard remains up throughout. The same row
  receives the delivery label at f47. The multiline edit also checks that
  the composer can resize independently of the keyboard.
- Tapback and scroll, 94 frames. The context surface starts opening at f14.
  It starts closing as the badge appears on `ready` at f34. The transcript
  scroll begins at f54 and settles at f65. Both the bubble and its badge
  move down 62 px. The edit moves the context and a different mark to
  `arrival`. The badge follows that row for the same 62 px.
- In-thread photos, 74 frames. Only the clipped attachment rail translates
  horizontally. Page text updates at f19 and the second photo settles by f26.
  The return starts at f44 and settles at f51. The two edits start on
  different photos and reach the opposite photo with stationary header and
  conversation geometry.
- Payment test mock, 108 frames. Card f14, approval sheet f34, dismissal
  starts f59 and ends at f66, simulated result f78. The same inline card
  owns the first and final states. [Payment provenance](PAYMENT.md)

The [decoded proof report](proof.json) records exact CFR timestamps, the
picture hashes, and pixel checks. The send checks compare the draft region
and outgoing seat before and after send, and measure maximum mean RGB drift
under the keyboard. The Tapback check compares each badge crop before scroll
and after the measured translation. The photo check measures both change
inside the rail and stability of the header. Small pixel deltas come from
the encoded picture.

## Reproduce

From a checkout with both UI and Observer integrated, run from
`skill/imessage-motion-recreation`. Use the repository's Python/Pillow and
FFmpeg runtime. The proof also uses NumPy and fontconfig with DejaVu Sans.

```sh
python3 -m unittest ui.test_adapter
python3 -m ui.sequence_proof --out-dir /tmp/ui-sequences
```

On the UI branch, use the pinned resolver from Observer with the same
command.

```sh
git fetch origin refs/heads/codex-video-v3/observer
git show f926ed417a128845a7912cc23edb632561f26cdd:skill/imessage-motion-recreation/contracts/timeline.py > /tmp/ui-timeline.py
python3 -m ui.sequence_proof --resolver /tmp/ui-timeline.py --out-dir /tmp/ui-sequences
```

Compile one editable input with the same adapter entry point that Recreation
uses. When editing the photo fixture, keep the JSON near its `assets/`
directory or update the relative paths.

```sh
python3 -m ui.adapter ui/examples/photos-fixed-header.json --out /tmp/ui-photo.scene.json
python3 scripts/engines/render_pillow.py --scene /tmp/ui-photo.scene.json --out /tmp/ui-photo.mp4
```

Run `sha256sum -c SHA256SUMS` in this folder to verify the submitted
artifacts. The captured reference videos stay in their source locations.

## Original photo sources

The unchanged photo bytes came from scikit-image v0.25.2 commit
`e8a42ba85aaf5fd9322ef9ca51bc21063b22fcae`. Its source notes credit the
Eileen Collins portrait to NASA and the DSCOVR launch photograph to SpaceX,
and identify both as public domain. These are editable attachment images.
[Portrait and rights](https://github.com/scikit-image/scikit-image/blob/e8a42ba85aaf5fd9322ef9ca51bc21063b22fcae/skimage/data/_fetchers.py#L382-L401) · [Launch and rights](https://github.com/scikit-image/scikit-image/blob/e8a42ba85aaf5fd9322ef9ca51bc21063b22fcae/skimage/data/_fetchers.py#L1032-L1052)
