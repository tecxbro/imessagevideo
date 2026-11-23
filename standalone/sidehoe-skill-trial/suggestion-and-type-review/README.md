# Sidehoe suggestion and lettering review

November 21, 2026. The [candidate MP4](candidate/sidehoe.mp4) was rendered from a clean
copy of the [editable project](project/README.md).

[Watch the source and candidate side by side](review/side-by-side.mp4) ·
[Step through all 778 matched frame pairs](review/native/index.html)

## Edits

- At f343–351, Sofia’s reply and suggestion use separate antialiased
  outlines and tails. The No and Send? controls use their own measured
  bounds and fill colors.
- The incoming message lines use measured positions, font weight, color
  and focus. The follow-up’s outgoing message uses an editable vertical
  cyan gradient through f671–693.

The Motion library supplied 39 native source crops across 4 tracks.
All crop hashes, dimensions and presentation times verified.
Editing the suggestion, Send? label, first reply and outgoing gradient
in a clean copy changed their visible regions.
[Motion observations](review/motion/motion-observations.json) ·
[Editability evidence](review/editability.json)

| Source time | Matched screenshots | Previous mean RGB error | Revised mean RGB error |
| --- | --- | ---: | ---: |
| 13.68 s | [Frame before the suggestion adjustment](review/focus/f342-sofia-closeup-entry.png) | 4.57 | 4.57 |
| 13.72 s | [Suggestion and controls enter](review/focus/f343-sofia-suggestion-and-controls-enter.png) | 4.77 | 4.07 |
| 13.80 s | [Suggestion before the previous largest mismatch](review/focus/f345-sofia-suggestion-before-largest-mismatch.png) | 4.85 | 4.00 |
| 13.84 s | [Sofia’s suggestion and controls](review/focus/f346-sofia-suggestion-and-controls-held.png) | 5.11 | 4.17 |
| 13.88 s | [Next suggestion frame](review/focus/f347-sofia-next-suggestion-frame.png) | 5.08 | 4.32 |
| 14.04 s | [Last edited close-up frame](review/focus/f351-sofia-closeup-end.png) | 4.92 | 3.87 |
| 14.08 s | [Frame after the suggestion adjustment](review/focus/f352-sofia-pullback-entry.png) | 4.59 | 4.59 |
| 27.16 s | [Outgoing bubble gradient and incoming text](review/focus/f679-follow-outgoing-gradient-and-incoming-type.png) | 5.60 | 4.39 |
| 27.24 s | [First reply and held cursor](review/focus/f681-follow-first-reply-and-cursor-hold.png) | 5.81 | 5.25 |
| 27.68 s | [Follow-up conversation withdrawing](review/focus/f692-follow-up-conversation-withdrawing.png) | 4.05 | 3.73 |

Each row compares the same crop and frame from the three encoded files.
[Selected crop bounds and metrics](review/focus/metrics.csv) ·
[Previous candidate](../camera-and-message-review/README.md)

## Final MP4 review

**Exact comparison failed.** The final mux decodes cleanly, and all 778 frame indices,
presentation times and exclusive end times match at 2000 × 2000 and 25 fps.
Whole-film mean RGB error moved from 2.834 to 2.817.
The reviewer found 0 pixel-identical frames. The last frame differs by
23 pixels. The highest remaining whole-frame RGB error is 4.93
at f34 (1.36 s).
[Exact verdict](review/native/report.json) ·
[All frame measurements](review/native/frames.csv) ·
[Highest-error frame](review/native/pairs/000034.jpg)

At 13.84 s, the reply and suggestion silhouettes are closer.
The letter edges, message composer and residual pink edge on the
suggestion still visibly differ. In the follow-up, the bottom of the
outgoing bubble is closer in color and the white lettering still differs.
The withdrawing cursor crop at f694 has a small increase in decoded
error even though its lossless frame matches the previous render.
[Withdrawing cursor](review/focus/f694-follow-cursor-native-hull.png) ·
[Title and hearts at 7.60 s](review/focus/f190-attached-title-and-hearts.png) ·
[Profile badge at 28.24 s](review/focus/f706-attached-profile-badge.png)

**HyperFrames 0.9.77 passed its visual thresholds.** Its mean SSIM moved from
0.9718 to 0.9720. All six cuts aligned at
5.36, 6.40, 8.52, 16.04, 27.72 and 30.80 s. All 202 files in the official reviewer
copy verified against its manifest.
[HyperFrames report](review/hyperframes.json) ·
[Ranked comparison sheet](review/hyperframes/worst.jpg) ·
[Pinned reviewer and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

All 32 edited frames improved before encoding and in the decoded MP4. The other 746
lossless frames, authored audio stems, audio cue map and AAC stream match the
previous candidate by hash.
[Lossless measurements](review/stage-metrics.json)

Source SHA-256  
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Candidate MP4 SHA-256  
`4254f47524715c1df2257be5ac761a7e36137acd3f9deabe41cd3daee6973fb4`

## Rerun the review

Set `SOURCE` to the locked source and use a fresh review directory.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" "$PWD/candidate/sidehoe.mp4" "$PWD/review-rerun"

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../camera-and-message-review/candidate/sidehoe.mp4 \
  candidate/sidehoe.mp4 review-rerun/focus
```
