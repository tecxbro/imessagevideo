# Motion library

The director CLI returns motion examples from a description of the moving layer and the layers that hold. Its [catalog](catalog.json) links the evidence, names the visible behavior and records the inferred mechanics. It searches offline using weighted English phrases. A result may ask for more detail or report no match.

Run from the checkout root with Node.js.

```bash
cli=skill/imessage-motion-recreation/director/cli.mjs
node "$cli" motion search 'Pictures glide under a venue name. The buttons stay in place.'
node "$cli" motion show place-photo-strip
node "$cli" motion preview place-photo-strip --out /tmp/place-motion.mp4
```

Open the MP4 in a media player. For a measured film, extract its original interval with `motion preview ID --source --out /tmp/source.mp4`. This uses FFmpeg and the source film resolved in the catalog.

| Editable example | Source interval | Moving preview |
| --- | --- | --- |
| Place photo strip | [Linq](https://github.com/tecxbro/imessagevideo/blob/c49482aec7b8ed0b840f97c61a5e5b860c4077b6/projects/05-linq-complete-v1/imessage-recreations/references/05-linq/source.mp4) frames 1091–1111 | [MP4](previews/place-photo-strip.mp4) |
| Conversation attachment stack | [Apple’s Messages guide](https://support.apple.com/guide/iphone/share-content-iphb66cfeaad/27/ios/27) | [MP4](previews/messages-attachment-stack.mp4) |
| Inline card to expanded sheet | [Photon Mini](https://github.com/tecxbro/imessagevideo/blob/c49482aec7b8ed0b840f97c61a5e5b860c4077b6/projects/03-photon-mini-complete-v1/imessage-recreations/references/03-photon-mini/source.mp4) frames 211–240 | [MP4](previews/inline-card-expand.mp4) |
| Portrait ring | [Gallery](https://github.com/tecxbro/imessagevideo/blob/c49482aec7b8ed0b840f97c61a5e5b860c4077b6/projects/06-gallery-complete-v1/imessage-recreations/references/06-gallery/source.mp4) frames 603–653 | [MP4](previews/avatar-ring-assemble.mp4) |

The strip moves as one clipped row. The stack moves and promotes individual overlapping attachments. The Apple guide describes grouped attachments and swiping after opening a stack. The preview stages an authored gesture in a stylized conversation.

## Replace and render

Copy the selected `defaults/ID.json` and change the fields listed by `motion show ID`. The renderer resolves local artwork paths from the config file’s directory. Use PNG, JPEG or self-contained SVG. Supply artwork at the intended tile ratio so it keeps its proportions. The strip and stack use near 16:10 tiles, the portraits are square, and the sheet uses one shared artwork asset. Long text can use explicit line breaks. Check it in the rendered frame.

The stack config accepts `swipes` from one to one fewer than the artwork count. Use four or more items to depict the native stack grouping described by Apple. Film timing, layer positions and editability live in [blocks.mjs](blocks.mjs). The defaults and the blind-trial artwork are original vector illustrations.

Install the [existing Pillow engine dependencies](../../scripts/engines/requirements.txt) in a Python 3.11+ virtual environment and put FFmpeg on PATH. For SVG support on macOS with Homebrew Cairo, use `export DYLD_FALLBACK_LIBRARY_PATH="$(brew --prefix cairo)/lib${DYLD_FALLBACK_LIBRARY_PATH:+:$DYLD_FALLBACK_LIBRARY_PATH}"` if Python cannot load Cairo. Use `--python` to select the virtual environment interpreter.

```bash
node "$cli" motion render place-photo-strip --config /path/to/edited.json \
  --python .venv/bin/python --out /tmp/edited-motion.mp4
```

The command also writes the canonical `.scene.json` beside the render and keeps the artwork paths relative to that file. Use `motion scene ID --config … --out …` to export the editable scene without encoding.
