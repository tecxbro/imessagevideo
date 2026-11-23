# Real-video regression suite

Use the source clips and test assets accompanying the verification report. The six archived originals were pinned to `c49482aec7b8ed0b840f97c61a5e5b860c4077b6` on `tecxbro/imessagevideo`. The unseen original was generated and held separately by the independent reviewer before the builder received the MP4.

Run from the skill directory with Node.js, FFmpeg, ffprobe and Python 3.11+ with Pillow, NumPy, fontTools, SciPy and CairoSVG. CairoSVG also needs a system Cairo library. Tesseract is optional and checks the literal text directly on decoded edit frames when installed.

Set `INPUTS` to the absolute path of the supplied inputs folder and `RUN` to a new absolute work directory. Keep the same library for all cases and a new output folder for each invocation.

```sh
mkdir -p "$RUN/library"
cp -R assets/library/. "$RUN/library/"
python3 -m unittest discover -s tests -v
python3 verification/real-video/recreate_unseen.py \
  "$INPUTS/unseen-complete.mp4" "$RUN/recreation" "$RUN/library" \
  --reviewer "Name of the person who actually reviewed the reconstruction"
python3 verification/real-video/linq_swipe.py "$INPUTS" "$RUN/linq" "$RUN/library"
python3 verification/real-video/direction_and_edit.py \
  "$RUN/concert" "$RUN/library" "$INPUTS/linq-fixed-swipe.mp4"
python3 verification/real-video/verify_edit.py \
  "$RUN/concert" "$INPUTS/linq-fixed-swipe.mp4" "$RUN/edit-evidence"
```

`recreate_unseen.py` compares every frame and rejects a two-frame delay, a shortened ending and stripped audio. It rerenders from the copied editable project, then repeats the exact request in a new process against the persistent library. The two chimes are synthesized separately. The registration expects a named review after the reviewer has seen the submitted work.

The Linq donor contains original frames 1088–1134 inclusive. This is the fixed-heading passage after the lead-in camera movement. The alternate photos have credits alongside the inputs. The 480 × 360 recognition excerpt covers original frames 1020–1229 inclusive. Recognition of that excerpt is a candidate identity, which the accompanying review aligns independently on the source clock.

For the catalog, the companion reviewer runner `review/audit_catalog.py` opens the 77 seed previews, exports their editable files, rerenders each in a fresh process and generates comparison reports and frame strips. Review the resulting strips against each entry's documented movement, anchors and ending. The test pack includes the reviewed results.

```sh
python3 /path/to/evidence/review/audit_catalog.py "$PWD" "$RUN/catalog" --workers 3
python3 scripts/learn.py --library "$RUN/library" replay toggle-thumb-then-tint \
  --out "$RUN/switch.mp4" --project "$RUN/switch-editable"
python3 scripts/learn.py --library "$RUN/library" replay tether-extend-then-pivot-dock \
  --out "$RUN/tether.mp4" --project "$RUN/tether-editable"
```

Reopen each learned project's saved command in `replay.json` in a fresh process from that directory and compare to its library preview on the same native clock. Consult the known source and sound tolerances in each evidence report instead of comparing MP4 container bytes across systems.
