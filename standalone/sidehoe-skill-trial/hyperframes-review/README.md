# Sidehoe recreation review

November 21, 2026. This is an editable comparison candidate. The source
is the supplied 2000 × 2000 `sidehoe.mp4`. The comparison baseline is
the [previous reconstruction](../finish/sidehoe.mp4).

- [Revised MP4](candidate/sidehoe.mp4) and [editable project](project/README.md)
- [Every aligned frame](review-final/native/index.html), [native RGB data](review-final/native/frames.csv), and [exact verdict](review-final/native/report.json)
- [HyperFrames report](review-final/hyperframes.json), [ranked screenshot sheet](review-final/hyperframes/worst.jpg), and [pinned reviewer source](vendor/hyperframes/UPSTREAM.md)
- [Three-way crop measurements](review-final/focus/metrics.csv) and [motion-library source measurements](motion-evidence/motion-observations.json)

## What changed in the render

- The profile badge now has independently spaced rear cards, curved
  portrait shapes, a layered heart and a moving focus and exposure.
  [4.24 s from the decoded exports](review-final/focus/f106-profile.png)
- The assistant reveal has separate perimeter, lighting, bevel depth,
  camera island and contact poses. Controls and contact disks have their
  own lighting and scale. [5.48 s](review-final/focus/f137-rim-ripple.png) ·
  [6.00 s](review-final/focus/f150-handset-hold.png)
- The two lines use measured ink boxes and local system type. The
  translucent hearts have separate tracks for position, rotation, size
  and opacity. [7.64 s](review-final/focus/f191-type-and-hearts.png) ·
  [8.36 s in motion](review-final/focus/f209-title-motion-blur.png)
- The inbox pins travel independently of the rows. During the Sofia
  handoff the phone hardware, interior and detached controls have
  independent motion and opacity. [2.12 s](review-final/focus/f053-inbox-scroll.png)
  · [14.20 s](review-final/focus/f355-sofia-handoff.png)
- The blue tile has a measured top and bottom during the approach and
  exit, a recessed cheek and editable numeral geometry. [24.40 s](review-final/focus/f610-tile-approach.png)
  · [24.48 s](review-final/focus/f612-tile-face.png) · [24.84 s](review-final/focus/f621-tile-tail.png)
- The cursor is visible from f625. It points down, turns through its
  sweep, approaches the independently placed Yes chip, then withdraws.
  [First visible frame](review-final/focus/f625-cursor-first-visible.png) ·
  [Descent](review-final/focus/f643-cursor-descent.png) ·
  [Sweep](review-final/focus/f663-cursor-sweep.png) ·
  [Contact](review-final/focus/f675-cursor-contact.png) ·
  [Withdrawal](review-final/focus/f694-cursor-withdrawal.png)

The final MP4 was built by rendering all frames from a clean copy of
the editable project. Its 56 scene events, authored mix, Foley and score
stems, and encoded AAC stream match the prior editable reconstruction.
The reference movie supplied the measurements. The project renders from
its own scene, artwork and sound code.

## Final encoded comparison

The source and candidate have 778 aligned decoded frames at 25 fps.
The ending is 31.12 seconds. The exact gate reports **FAIL**.
**0 of 778** frames have identical decoded RGB.
Mean absolute RGB channel error across the film fell from
**6.52 to 4.49**. The full-range encode reduced
the neutral paper error. The focused crops measure the remaining picture
differences directly.

| Matched crop | Seconds | Previous mean RGB error | Revised mean RGB error |
| --- | ---: | ---: | ---: |
| Inbox scroll | 2.12 | 15.73 | 4.54 |
| Profile badge | 4.24 | 17.37 | 12.57 |
| Handset lighting | 6.00 | 18.45 | 9.00 |
| Title and hearts | 7.64 | 44.07 | 16.28 |
| Blue tile | 24.48 | 11.19 | 5.69 |
| Cursor turn | 26.20 | 10.42 | 1.53 |
| Yes hold | 27.44 | 6.24 | 4.67 |

The worst whole-frame RGB error is at [f336](review-final/native/pairs/000336.jpg).
The phone and its contents still rise and blur differently as the Sofia
suggestion appears. The avatar faces and lavender surround differ in
the [profile cluster](review-final/native/pairs/000237.jpg). The cyan cap
and side shading on the [blue tile](review-final/focus/f612-tile-face.png)
and the first [cursor blur](review-final/focus/f625-cursor-first-visible.png)
remain visibly different. The revised [cursor sweep](review-final/focus/f663-cursor-sweep.png)
still differs as it crosses the handset rail.

HyperFrames reported mean SSIM 0.9550 → 0.9586
and a revised worst-cell fifth percentile of 0.7413.
Its verdict remains **FAIL**. It flags the transition at
[16.04 s](review-final/focus/f401-calendar-overlap.png) as missing.
The overlap is visible across [f400](review-final/focus/f400-calendar-before.png),
[f401](review-final/focus/f401-calendar-overlap.png) and
[f402](review-final/focus/f402-calendar-after.png), with a different
exposure trail in the calendar and outgoing text.

The first review step copied and verified 202 files from upstream
before the scene edits. The [pinned source manifest](vendor/hyperframes/SHA256SUMS)
and [baseline result](baseline/upstream.json) are retained. Both
reviewers ran against the muxed output linked above.

| Input | SHA-256 |
| --- | --- |
| Source | `f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327` |
| Previous MP4 | `0e971a4b6307eff5f53f8817ada0be5dea23695de4da0aaa8ccd1848bc55cbcc` |
| Revised MP4 | `feef03b636aa7810eb0fc6fd25f13030a4f87985a20029d92d8b55d931cfdff7` |

## Rerun

Follow the [project setup](project/README.md) and render from the editable
scene. Install the published HyperFrames CLI at version `0.9.77`.
From this folder run the two checks on the exact muxed MP4.

```sh
PYTHON=/path/to/render-environment/bin/python \
HYPERFRAMES=/path/to/hyperframes \
bash review.sh "$SOURCE" candidate/sidehoe.mp4 review-run

/path/to/render-environment/bin/python focus.py \
  "$SOURCE" ../finish/sidehoe.mp4 candidate/sidehoe.mp4 review-run/focus
```

The review exits with a failure status when a picture criterion fails.
The current output uses the upstream CLI with telemetry disabled. The
same-time crop command extracts both encodes and the source by zero-based
frame index before measuring at original size and making previews.
