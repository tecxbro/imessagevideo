# Sidehoe handset push and calendar handoff review

November 21, 2026. The prior column uses the
[title, tile, cursor and badge export](../detail-review/candidate/sidehoe.mp4).
The [revised export](candidate/sidehoe.mp4) was built from a clean copy of
the [editable project](project/README.md).

[Watch the same-time comparison](review/side-by-side.mp4) ·
[Step through all 778 frame pairs](review/native/index.html)

## Checked in the encoded export

Sofia’s push-in now registers the screen, earlier messages and keyboard
rows independently. The follow-up screen had three copies of the same
early defocus term. The renderer now applies one. The departing No and
Send? controls have measured positions, lettering bounds and colors.
The two incoming calendar bars now have separate positions, leading
and trailing blur widths, and pigments.

The motion library extracted and verified 31 source crops from the
handset, No control and calendar handoff. These observations provide the
native time and visible bounds. The source frames serve as review inputs
for the independently drawn artwork.
[Motion plan](review/motion-plan.json) ·
[Hashed source observations](review/motion/motion-observations.json)

| Time | Source comparison | Prior RGB error | Revised RGB error |
| --- | --- | ---: | ---: |
| 13.48 s | [Sofia push begins](review/focus/f337-sofia-push-in-entry.png) | 6.10 | 4.21 |
| 13.64 s | [Sofia messages and keyboard](review/focus/f341-sofia-largest-prior-mismatch.png) | 8.58 | 4.84 |
| 16.00 s | [Frame before handoff](review/focus/f400-calendar-before.png) | 3.00 | 2.62 |
| 16.04 s | [Calendar handoff](review/focus/f401-calendar-handoff.png) | 2.40 | 2.08 |
| 16.08 s | [Frame after handoff](review/focus/f402-calendar-after.png) | 1.94 | 1.79 |
| 26.48 s | [Follow-up keyboard focus](review/focus/f662-follow-keyboard-defocus.png) | 6.50 | 5.13 |

All 43 edited lossless frames improved on decoded whole-frame mean
absolute RGB error, measured on a 0–255 scale. The adjacent f342 went
from 4.570 to 4.578 after encoding. The title and hearts crop at 7.60 s
and the profile badge crop at 28.24 s remain open.
[Title screenshot comparison](review/focus/f190-attached-title-and-hearts.png) ·
[Badge screenshot comparison](review/focus/f706-attached-profile-badge.png)

## Full export verdict

**The published HyperFrames 0.9.77 diff passes.** It detects all six
reference cuts, with no missing or extra cuts. At 16.04 s the ratio of
the decoded gray change to the nearby median is 4.034 for the reference,
3.914 for the prior export and 4.039 for the revised export. Mean SSIM
is 0.9647. The review used the pinned upstream copy and published CLI,
and all 202 files in the vendor manifest verified.
[HyperFrames verdict](review/hyperframes.json) ·
[Reviewer source and license](../hyperframes-review/vendor/hyperframes/UPSTREAM.md)

**The exact native comparison fails.** All 778 frame indices, start
times and exclusive end times agree at 2000 × 2000 and 25 fps. Zero
frames are pixel-identical. Full-film mean RGB error fell from 3.779
to 3.740, and changed pixels fell from 1,275,079,862 to 1,271,640,663
across the sequence. The highest whole-frame error is 8.34 at f226,
where the portrait cluster still differs in disk geometry, hair and
expression. [Frame 226](review/native/pairs/000226.jpg) ·
[Native report](review/native/report.json) ·
[All frame measurements](review/native/frames.csv)

The revised mux decodes cleanly. The AAC stream, editable stems and
event map match the prior authored mix by hash. The silent side-by-side
video has 778 frames, runs 31.12 seconds and puts the source on the left.

Source SHA-256
`f821bb58cbdb265a75d572616d0da723e9cfb6de31e3db5f8a17d94dc15b5327`

Revised MP4 SHA-256
`4d762a949d57d7e0a3fae45da4dfee4e56f4379e996b449d391f52da25d5af4f`

## Rerun from this directory

Set `SOURCE` to the locked reference and use a fresh review directory.

```sh
PYTHON=/path/to/render-environment/bin/python HYPERFRAMES=/path/to/hyperframes bash review.sh "$SOURCE" candidate/sidehoe.mp4 review-rerun

/path/to/render-environment/bin/python focus.py   "$SOURCE" ../detail-review/candidate/sidehoe.mp4   candidate/sidehoe.mp4 review-rerun/focus
```
