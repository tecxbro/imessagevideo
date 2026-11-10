# Local offline viewer

Open [catalog/index.html](../catalog/index.html) from the complete library folder. It loads its video, original references, scene/analysis links, full renderer text and visual atlases from local files. It has no external script, font, analytics or remote-video dependency, and requires no Google Drive login. Its source panel embeds the same **nine complete renderer files**, with their byte lengths and SHA256 values, rather than excerpts.

The viewer contains six completed examples and five method choices, covering all thirty retained reference-audio movies. Each example also has a native player for the supplied original film, direct links to its full scene JSON, measured analysis and project README, and its selected local visual studies. The source panel reflects the actual shared-adapter architecture. It does not imply that five independent applications were written for each film. Figma remains an unvalidated prototype.

The visual designs and source film examples are separate from the nine neutral choreography starters and fourteen selected motion studies in the [local director explorer](../skill/imessage-motion-recreation/director/index.html). That explorer, including its visual atlas images, is also stored locally. The separate [audio archive](../resources/complete-ui-audio-source-v1/) retains the later UI-audio source, preview movies, timing/configuration and provenance; the thirty main viewer movies explicitly retain the supplied reference soundtracks.

## Paths and portability

- Viewer: `catalog/index.html`.
- Full measured projects and retained films: `projects/<archive-id>/imessage-recreations/`.
- Per-example results: `deliverables/<example-id>/<method>.mp4` inside each project.
- Original films: `references/<example-id>/source.mp4` inside each project.
- Scene, measured scan and project entrypoints: see the selected viewer links and `README-COMPLETE-EXAMPLE.md`.
- Full embedded code also exists in `skill/imessage-motion-recreation/scripts/engines/` and in each project's `engines/` directory.
- Visual atlases, components and neutral starters: `skill/imessage-motion-recreation/director/`.
- Backup source registry: `skill/imessage-motion-recreation/library/manifest.json`.

Keep the folder structure intact when copying the library to your computer. All operational viewer links are relative, so the top-level folder can move. If your desktop browser restricts local-file playback, run a local-only server from the library root with `python -m http.server 8765 --bind 127.0.0.1`, then open `http://127.0.0.1:8765/catalog/` in your browser. This command serves local files to your own machine; it does not publish a website. Reading retained resources is offline; installing render dependencies and researching a new company are separate operations.

## Validation and limits

[catalog/check_offline_catalog.py](../catalog/check_offline_catalog.py) checks that the six-film/five-method catalog is present, all nine embedded sources exactly match their retained bytes/hashes, inline JavaScript parses, referenced DOM IDs exist, no HTML `src`/`href` initiates an external request, and every static/dynamic local media/scene/analysis/source/atlas path resolves. Finished/original movie and scene sizes are checked against the accepted manifest. Run it again after any move or partial copy:

```bash
python catalog/check_offline_catalog.py
```

Its exact current result is [catalog/validation.json](../catalog/validation.json). A `pending-restoration` result lists the particular files still absent during restoration; a `pass` means all checked local paths resolve. This is a static/source/path validation, **not an interactive browser playback certification**. The managed environment's browser already rejected file navigation and its inherited-proxy loopback route; those restrictions were not bypassed. Native playback still depends on your own browser/player's codec and file-access support.

The reproducible offline transformation is [catalog/build_offline_catalog.py](../catalog/build_offline_catalog.py). It starts from the archived v3 viewer, preserves the complete selected source files and poster data, and replaces the public-video/Drive workflow with the already materialized local project paths. The original v3 ZIP remains unchanged in `archives/`.
