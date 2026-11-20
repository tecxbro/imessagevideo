# Poke location handoff

This is a measurement of the existing Poke source, used to test the workflow and hand a real motion to Direction and Motion. It contains the complete source analysis and a separate comparison with the previously accepted GSAP master. The master has 1,283 aligned frames and the same 42.809433-second picture clock as the original. It fails the default 2/255 per-frame RGB gate, with a film mean of 2.6103 and peak of 6.0337 at frame 793. It is historical baseline evidence.

| Source frame at 30000/1001 | Visible evidence |
| --- | --- |
| 412–414 | The question “where are you rn?” moves out of the composer area. It is readable at 413 at low opacity and clear at 414. |
| 449–450 | The conversation and device push toward the keyboard. The question stays visible while earlier message content leaves the crop. |
| 455–457 | Current Location appears in the keyboard suggestion row and becomes cleanly legible. |
| 485 | The Current Location label begins dimming while the same question remains visible. |
| 509–512 | Composer and keyboard exit downward. The question persists through the blank response area. |
| 513–514 | The response appears beneath and to the right of the question. The pin and Shared Location title are legible on 513. Palo Alto, CA is legible on 514. |

The visible question is the continuity anchor. It follows the camera, while the response area changes from keyboard control to blank space to a local map bubble. Use separate editable tracks for the location control, keyboard/composer, question and card. The magenta pin appears at f513. Its measured centroid is approximately (878, 697) and moves up by 57.8 coded pixels in the next frame, then by 20.5 more by f515. It is near (878, 590) at f519. Keep the pin attached to the card and continue the smaller vertical settling motion while the caption can be read. See [the full landmark series](pin-landmarks.csv). The source timings and crop gates are recreation measurements. An original edit can choose its own pacing.

```bash
R=skill/imessage-motion-recreation/recreate
SOURCE=projects/04-poke-complete-v1/imessage-recreations/references/04-poke/source.mp4
python3 "$R/recreate.py" inspect "$SOURCE" --frames 406:420,446:459,481:490,507:519 --out /tmp/poke-landmarks --sheet-width 280
python3 "$R/recreate.py" landmarks "$SOURCE" --plan review/imv-v3/recreate/poke/pin-track.json --out /tmp/poke-pin
```
