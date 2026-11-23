# Runtime and package verification

Use Python 3.11 or newer, FFmpeg and ffprobe on PATH. Pillow rendering
uses the packages pinned in [requirements.txt](../scripts/engines/requirements.txt).
Use a Python virtual environment and run the skill under that interpreter.
For text scenes, install your declared licensed fonts and the platform's
fontconfig utilities. Use relative font and image paths inside the editable
project.

From the extracted skill directory:

```sh
python3 -m venv /tmp/imv-python
/tmp/imv-python/bin/python -m pip install -r scripts/engines/requirements.txt
/tmp/imv-python/bin/python observer/imv.py smoke --out /tmp/imv-check
```

For HTML/SVG, GSAP, Remotion and Motion Canvas, install Node.js and Chromium.
Run `npm ci --prefix scripts/engines` and set `CHROME_PATH` to the installed
Chromium executable. Use the same Python runtime for the central command.

```sh
/tmp/imv-python/bin/python observer/imv.py smoke --method all --out /tmp/imv-renderers
```

This renders and fully decodes each MP4. The test checks the declared
rational frame rate, every frame timestamp, the final frame, and the change
in marker pixels between frames 11 and 12. It verifies the example's picture
clock. Check the geometry, text, assets and sound of each project separately.

To produce or inspect a skill ZIP:

```sh
python3 observer/package.py --out /tmp/imessage-motion-recreation-v3.zip
python3 observer/package.py --verify /tmp/imessage-motion-recreation-v3.zip
```

The ZIP carries source and a checksum for each included file. Runtime
dependencies, licensed production assets, full films, and the current
Dataset exclusion manifest are supplied separately from the ZIP.
