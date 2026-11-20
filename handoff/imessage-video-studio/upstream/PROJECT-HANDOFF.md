# Context for a new local Codex session

The user wants a complete local production library for iMessage motion videos:
actual authored source, full measured scenes, assets, originals, finished videos,
frame analysis, reusable components, visual teaching references, UI sounds and
direction/research instructions. The skill must provide code and visual evidence,
not only prose or starter snippets.

Start with [AGENTS.md](AGENTS.md), [the skill](skill/imessage-motion-recreation/SKILL.md),
[LOCAL-LIBRARY.json](LOCAL-LIBRARY.json), [LOCATIONS.md](LOCATIONS.md), and
[the detailed contents/gaps audit](reports/SKILL-CONTENTS-AND-GAPS.md).
`python3 tools/sync_library.py` verifies tracked parts and restores the complete
files locally. `catalog/index.html` is the offline film/full-code viewer;
`inventory/index.html` and `inventory/ALL-FILES.csv` locate every payload file.

## Reference films

1. PhotonHQ: https://x.com/PhotonHQ/status/2110789854242218066
2. Daniel Tian: https://x.com/danieltian/status/2108261717600063915
3. Photon mini-app: https://x.com/daniel_tian1/status/2067327329161064688
4. Poke Apple Messages: https://x.com/interaction/status/2062575428213285352
5. Linq: https://www.linkedin.com/posts/elliottpotter_your-users-never-have-to-leave-imessage-again-activity-7477784121293950976-Dlap
6. Rene/gallery: https://launchvideos.gallery/videos/1724779c-9543-4a4e-bd12-bafceb1cc90f

All six original clips are already local. Do not download them again for normal
work. Focus on motion/graphic sections where a source contains live action.

## Working preferences and actual architecture

- Use multiple agents for independent substantial work when useful. Preserve
  ownership boundaries so parallel writers do not overwrite the same files.
- Document meaningful steps, defects, evidence, causes/hypotheses and changed
  variables. Do not repeat an unchanged failed attempt. Verify actual outputs.
- Small UI sounds matter: sending, tapping, selecting and real human typing must
  follow visible actions. Prefer documented licensed source effects when suitable;
  procedural/generated accents can fill gaps. Music is optional and secondary.
- Image generation is allowed when useful. Generated video is less preferred;
  the user's earlier limit was no more than two retries per generated clip.
- The six accepted films use full measured scenes plus five genuine shared
  adapters: Remotion, GSAP, HTML/SVG, native Motion Canvas and Pillow/FFmpeg.
  Per-example entry wrappers are included. Thirty independently handwritten
  standalone applications were not authored.
- Fourteen source studies, nine neutral editable components and nine motion
  starters form the teaching layer. Full source scenes cover the entire films.
  Historical numeric CSVs cover 7,499 aligned frames for accepted GSAP comparisons;
  named teaching windows cover 1,697 of those frames. Do not invent seventy effects
  or certify perfect identity from those counts.
- Known limits include residual visual error, a documented Poke 12-frame timing
  discrepancy, raster card interiors/outlined glyphs, a heuristic motif router,
  unvalidated Figma motion/export and target-machine dependency/playback checks.
  Read the audit for exact evidence and prioritized improvements.

For a new-company film, research its real product and UI from supplied/local
evidence and online primary sources when necessary. Write an evidence-backed
profile; inspect actual atlas images/full scenes; choose the story, components,
motion, copy and sound anchors; render and compare; deliver source, assets,
evidence, audio and video together. This is an agent workflow, not trained model
weights or an autonomous one-click film generator.

## Repository and local-machine setup

The user explicitly selected the private repository `tecxbro/imessagevideo` and
authorized replacing its previous contents. The prior README was preserved on
`backup/pre-library-2026-11-10`. Git LFS budget and Release-upload credential
failures led to the final ordinary-Git design: all 78 original 24 MiB-or-smaller
pieces and both small frozen ZIPs are tracked, while 12 complete ZIPs and two
oversized Daniel scene copies are losslessly reconstructed locally. See
[STORAGE.json](STORAGE.json) and [the offline sync report](reports/GITHUB-SYNC.md).
No Drive, Notion, LFS or Release download is required after cloning.

This cloud session did not control or install files on the user's Mac. To work
there, clone the repository, run the offline sync, and open that local folder in
a Codex session with local filesystem/terminal access. [MAC-SETUP.md](MAC-SETUP.md)
contains the steps. Browsing stored source/films works offline; new web research
and initial third-party dependency installation are separate operations.

Keep this repository private. Historical Drive IDs and older public-gallery
records remain provenance, not the primary library location. Existing source
and font licenses remain attached. A previous automatic-review rejection of a
different public source-site expansion does not block this explicitly authorized
private repository migration.
