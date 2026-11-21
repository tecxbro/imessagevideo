# Use the complete library on your Mac

These steps put the complete private repository on **your Mac**. A normal Git clone includes all production bytes, including verified archive chunks. Run the one-time local assembly helper to recreate the full ZIPs and large scene files at their canonical paths. Commands run in your own Terminal and a local Codex session; work performed in the managed `/workspace` environment does not itself install anything on your computer.

## 1. Install the small setup prerequisites

You need Git, Python 3.11 or later, access to the private GitHub repository, and a browser or video player. Python runs the offline assembly, local lookup, verification and skill-install helpers; browsing the stored HTML/video does not need Python. No Git LFS, GitHub CLI, GitHub Release access or Google Drive connection is required.

If you already use Homebrew, install the missing tools with:

```bash
brew install git python
```

Otherwise install Git and Python through their normal installers. Confirm the tools are available in a new Terminal:

```bash
git --version
python3 --version
```

Use your normal Git HTTPS credential setup to clone this private repository with an account that has access. Complete any authentication prompt locally; do not paste passwords or tokens into this chat. After the clone, the assembly helper works entirely offline without an account connection. Keep the repository private.

## 2. Clone and assemble the large files locally

Choose a folder you intend to keep. For example:

```bash
mkdir -p ~/Projects
cd ~/Projects
git clone --branch codex-trial https://github.com/tecxbro/imessagevideo.git
cd imessagevideo
python3 tools/sync_library.py
```

Run each line separately and let assembly finish. The checkout contains ordinary readable code, assets, videos, fonts and evidence, plus all seventy-eight verified archive parts (each at most 24 MiB) under [archives/resource-parts/](archives/resource-parts/). Two smaller frozen snapshot ZIPs are tracked normally under [archives/](archives/). No separate large-file service is involved.

`python3 tools/sync_library.py` is a Python-standard-library, **fully offline** operation. It verifies the seventy-eight part SHA256 values, reconstructs the twelve complete ZIPs with exact archive hashes, then safely extracts their payloads and merges files that already match. It recreates the two identical full Daniel scene copies and any other missing canonical payload. It does not download anything or ask for a GitHub/Drive connection.

GitHub's single-file size limit prevents tracking the large full scene files and largest assembled ZIPs directly. Those assembled outputs are ignored as derived files; their complete bytes are already present in the tracked parts and the helper restores them exactly. Thus `git clone` has all source bytes, but **you still need to run the assembly command once** before every canonical path is available.

Leave enough disk space for Git's checkout/objects, tracked parts, assembled archive ZIPs and restored projects. Rendering later adds caches and outputs. Do not copy only the small skill folder and assume its large referenced scenes or archive snapshots came with it. [LOCAL-LIBRARY.json](LOCAL-LIBRARY.json) records the local archive and payload identities.

Check the checkout:

```bash
git status --short
python3 tools/library.py verify
```

For a full local payload-hash check:

```bash
python3 tools/library.py verify --all-files
```

That check can take longer because it reads the full inventory. If assembly reports a missing part, hash mismatch or conflicting existing file, resolve that specific error before treating the library as complete. A missing tracked part may indicate an incomplete copy/checkout; restore it from the repository. Preserve a conflicting local file rather than overwriting it blindly; read the helper's diagnostic and rerun assembly after resolving the cause. Repeating assembly without changing a failed input does not repair it.

## 3. Open the offline catalogue

From the cloned repository root:

```bash
open catalog/index.html
open inventory/index.html
```

The catalogue presents all six examples, original movies, five completed reconstruction methods, full shared renderer source and local evidence links. The inventory is the exact file lookup. You can also open [LOCATIONS.md](LOCATIONS.md) and [inventory/ALL-FILES.csv](inventory/ALL-FILES.csv).

For editable neutral starters and their visual references:

```bash
open skill/imessage-motion-recreation/director/index.html
```

Keep the whole repository folder intact. After the one-time synchronization, these operational viewers use relative local links and do not need Google Drive, Notion, external fonts or a generation API. The main five-method reconstruction previews retain the supplied reference soundtracks; the separately produced UI-audio versions and their provenance are in `resources/complete-ui-audio-source-v1/`.

If your browser restricts local-file pages, use a loopback-only server from the repository root:

```bash
python3 -m http.server 8765 --bind 127.0.0.1
```

Leave that Terminal running and open `http://127.0.0.1:8765/catalog/` in your browser. Use another tab for `http://127.0.0.1:8765/inventory/`. This serves files to your own machine; it does not publish the library. Stop it with Control-C when finished. If your computer's managed browser policy also blocks local servers, follow that device's permitted viewing setup rather than disabling its policy.

Actual video decoding, seeking, audio switching and volume behavior still need checking in your own browser/player. Static HTML/path validation is not a certification of your device's playback.

## 4. Make the skill available to your local agent

From the `codex-trial` repository root:

```bash
python3 tools/install_skill.py
```

The installer makes `$imessage-video-codex-trial` available across projects on your Mac. It links `~/.agents/skills/imessage-video-codex-trial` to this checkout's `skill/imessage-motion-recreation` directory. It reuses an older installation link to this same directory if one exists. Keep the checkout available and start a local Codex chat to select the skill.

For an application that reads another skill directory, choose its supported destination explicitly:

```bash
python3 tools/install_skill.py --dest /path/to/your/skills/imessage-video-codex-trial
```

Replace the example destination with the actual directory your application uses. Do not delete an existing skill just to make installation succeed; preserve it and choose/switch destinations deliberately. If you later move the checkout, update the link by using the helper's documented options or reinstalling to an appropriate unused destination. Do not remove the checkout while the link points into it.

In Codex on your Mac, start a **local** session and select/open the cloned `imessagevideo` folder. The repository's `AGENTS.md` directs agents to the local skill; you can also name the exact entrypoint in your prompt:

> Read `skill/imessage-motion-recreation/SKILL.md` and `LOCATIONS.md`. Use the local code, scenes, videos, visual studies and analysis in this repository. Inspect the relevant visuals before choosing motions. For a new company, research its actual product first, then write the shot plan, implement it and validate the rendered result.

A cloud Codex session still runs on its selected cloud machine; selecting a repository there does not make it a local session on your Mac.

## 5. Find a specific file without opening Drive

```bash
python3 tools/library.py list
python3 tools/library.py where photon
python3 tools/library.py where 04-poke
python3 tools/library.py find scene.json
python3 tools/library.py find frames.csv
python3 tools/library.py find ui-cues
```

`where` matches an example/archive ID, title or substring and prints core example paths. `find` searches filename/path substrings. All file locations are also in [inventory/ALL-FILES.csv](inventory/ALL-FILES.csv), with resource-pack roots in [LOCAL-LIBRARY.json](LOCAL-LIBRARY.json). [README.md](README.md) links all six complete projects and the resource archives.

## 6. Set up rendering only when you need it

The repository includes renderer **source and pinned dependency manifests**, not installed package directories, Python virtual environments, Chromium binaries or a tested Mac runtime image. The stored films and reference library can be viewed offline after the complete clone plus synchronization; rerendering requires setup first.

Five genuine implementations are available in source: Remotion React, GSAP, HTML/SVG, Python/Pillow + FFmpeg, and native Motion Canvas. Figma remains an unvalidated prototype. Start with the selected project's `README-COMPLETE-EXAMPLE.md`, the skill's [RUNNING.md](skill/imessage-motion-recreation/RUNNING.md), and the [engine instructions](skill/imessage-motion-recreation/scripts/engines/README.md). Use the project's `tools/render_example.py` after dependencies and font resolution are ready.

Browser methods need compatible Node packages, an actual Chromium executable and FFmpeg. Python rendering/audio need the pinned Python packages and their native dependencies; typography can also need Cairo/fontconfig and the recorded fonts. Linux-specific defaults such as `/usr/bin/chromium` are historical environment paths, not your Mac's executable location. Configure `CHROME_PATH` to the actual installed Mac executable when required, and test one frame before launching a full film render.

Dependency installation may need the internet once. After compatible packages, runtimes, fonts and all assets exist locally, rendering the stored scenes does not require a Drive connection or a media-generation API. Researching a new company still needs first-party online evidence unless you provide a complete local evidence pack.

Keep original assets' license terms. The private repository is storage, not a new font/media redistribution license. Read [SKILL-CONTENTS-AND-GAPS.md](reports/SKILL-CONTENTS-AND-GAPS.md) for the exact limits, current study/component coverage, historical comparison scope and remaining work.
