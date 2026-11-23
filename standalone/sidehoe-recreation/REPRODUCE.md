# Reproducing the review

Use the isolated project packages for exports. Set `PYTHON` to a Python 3.11+ environment with Pillow and NumPy, and make FFmpeg with libx264 available on PATH. The renderer uses only the scene manifest, font, and Python modules in the project.

From the repository root, the original analysis and checks were run with these paths:

```sh
P=sidehoe-recreation
S=codex-trial/skill/imessage-motion-recreation
REF=/Users/darshan/Downloads/sidehoe.mp4

python3 "$S/recreate/recreate.py" analyze "$REF" --out "$P/measurements" --reuse
python3 "$S/recreate/recreate.py" compare "$REF" "$P/first/sidehoe.mp4" --checks "$P/checks.json" --out /tmp/sidehoe-first-check
python3 "$S/recreate/recreate.py" compare "$REF" "$P/revised/sidehoe.mp4" --checks "$P/checks.json" --out /tmp/sidehoe-revised-check
python3 "$P/tools/compare_visual.py" "$REF" "$P/revised/sidehoe.mp4" --windows "$P/evidence/windows.json" --out /tmp/sidehoe-visual
python3 "$P/tools/check_follow_contact.py" "$REF" "$P/revised/sidehoe.mp4" --out /tmp/sidehoe-visual/yes-contact.csv
python3 "$P/tools/resolve_contract.py" "$P/project/scene.json" "$S/contracts/timeline.py" /tmp/sidehoe-events.json
shasum -a 256 -c "$P/prebuild.sha256"
```

The checker returns 1 on the preserved visual gate failures in either edition. Its clock, display, EOF, and audio-start checks pass. The original source is required for the comparison commands. It is outside the portable projects.

From an empty folder:

```sh
unzip -q /path/to/sidehoe-recreation/revised/source.zip
cd project
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
PYTHON="$PWD/.venv/bin/python" ./export.sh exports cache
```

The file `evidence/clean-reopen.sb` records additional macOS sandbox constraints applied to the clean verification. The edit proof film uses local frames 0–28 corresponding to full-film frames 667–695.
