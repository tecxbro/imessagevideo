# Editable Messages-inspired conversation

An isolated extension to the director kit. This is authored choreography, **not a
native iOS renderer or a source-exact recreation**. It uses the existing shared
scene contract and HTML/SVG video engine; no screenshot is used as a UI layer.

## Run from the repository root

```sh
# One-time engine dependencies; no new dependency manifest is needed.
npm --prefix skill/imessage-motion-recreation/scripts/engines ci

node --test skill/imessage-motion-recreation/imessage-ui/components.test.mjs

# Export measured editable layers, the exact input and ownership/layout audit.
node skill/imessage-motion-recreation/imessage-ui/export.mjs --out work/ui

# Render the first demo or use any JSON conversation with the same contract.
node skill/imessage-motion-recreation/imessage-ui/export.mjs \
  --config skill/imessage-motion-recreation/imessage-ui/observer-trial.json \
  --out work/kiln --render yes

# Interactive source editor: open the printed server URL + the path below.
python3 -m http.server 8000 --bind 127.0.0.1
# /skill/imessage-motion-recreation/imessage-ui/index.html
```

FFmpeg must be on PATH. On macOS the exporter defaults to installed Google Chrome;
on Linux it defaults to `/usr/bin/chromium`. Set `CHROME_PATH` for another installed
Chromium. Measurements and render must use the same font environment. The exporter
uses the pinned Playwright already installed by the existing engines package.

## Editable boundaries

`components.mjs` exports `Message`, `Reaction`, `LinkPreview`, `PhotoStack`,
`AttachmentStack`, `ComposerState`, `wrapText`, `canvasMeasure`,
`validateConversation` and `buildConversation`. The latter returns `{scene,audit}`.
Pass `canvasMeasure(canvas.getContext('2d'))`; there is no silent approximate
production font-width fallback. Unit tests inject a deterministic width function;
actual exports measure Arial with Apple Color Emoji fallback in Chromium.

The JSON input contains:

- `participants`: unique stable IDs, names, initials, colors and exactly one `self`.
- `messages`: stable ID, `senderId`, arrival time `at`, editable `copy`, optional
  `link: {title,url,color}`, `cards`, or `photos: [{color,aspectRatio}]` + `caption`.
- `reactions`: on the target message, each with `ownerId`, `emoji`, and `at`.
  Compact emoji + initials badges touch the target bubble's top corner. Full
  owner identity is retained in the layer and audit. Color follows the reactor,
  **not** the message sender. Initials are a film ownership aid, not a claim
  about native Tapback presentation.
- `composer`: strictly increasing `{at,copy}` states, beginning at zero. A send
  state has empty copy and `sendMessageId`; the referenced self message must
  arrive at that exact time and equal the previous complete draft. Unmarked
  outgoing messages are allowed as earlier conversation history.
- `camera`: increasing `{at,x,y,scale}` poses in a 540×960 logical stage; the
  whole hierarchy transforms together. Optional `stageWidth` changes the
  framing aperture (height remains 16:9 portrait). Push-ins may intentionally crop the
  device, while transcript and attachment clips remain in local coordinates.
- `width`, `height`, `fps`, `duration`: output framing and frame-indexed timing.

Message text wraps to measured width, including explicit newlines and otherwise
unbreakable words. `Intl.Segmenter` preserves skin tones, joined emoji, and flags.
Emoji-only messages have no bubble and use larger type. Sender labels, avatar
initials, reaction names and copy remain separate editable text layers.

Camera motion never rewrites local message positions. A stationary transcript
clip contains a scrolling transcript; the screen owns an additional rounded
clip. The header and composer sit outside the transcript. The composer grows
from one to three lines, disables an empty send, clears on the marked send frame,
and has an optional attachment chip. Over-capacity composer/card/title copy
fails clearly rather than shrinking type or silently clipping it.

## Trials and evidence

`trial.mjs` is the first newly authored demo: three participants, four editable
story cards, two-sided reactions and camera motion. `observer-trial.json` is the
independent observer's unfamiliar kiln conversation, preserved verbatim in its
content: four participants, long URL preview, emoji-only message, unbreakable
word, three photo ratios, five owned reactions, a typed multiline send and a
1.6× camera push. Timing is newly authored because the observer supplied none.

`evidence/` preserves first exports, revised exports, their scenes and layout audits. These films
are intentionally silent: UI behavior is this assignment's boundary, not an
unscored claim of a finished audiovisual launch. Re-render commands above produce
new outputs without modifying that evidence.

## Sources and scope

- Existing component contract: `../director/component-contracts.md` and
  `../director/components.mjs`; inspected `../director/visuals/component-anatomy.png`.
- Keiki product evidence: <https://onkeiki.com/docs/cards> states that four or more
  cards arrive as a swipeable iMessage stack, while smaller sets may be collages.
  Its `story` card template is 690×920. Our editable artwork is independently
  authored, not a reproduction of Keiki screenshots. The observer's requested
  **three-photo** fanned stack is explicitly a film fixture, not proof of a
  native three-photo swipe gesture. The four-card demo slides only content under
  a stationary counter; it does not claim OS gesture timing.
- <https://onkeiki.com/docs/imessage-apps> describes app presentations and fallback
  behavior. No native app capability is inferred merely from these documents.
- Shared sheet-motion evidence:
  <https://github.com/tecxbro/imessagedemo/blob/main/.agents/skills/recreate-imessage-sheet-motion/SKILL.md>.
  This trial does not reproduce that sheet or infer native touch events.

**Device/OS disclosure:** 390×844 logical-point, iPhone 13-class proportions only.
Bubble metrics and timing are authored; they were not measured from an identified
iPhone or iOS release. Render target is desktop Chromium on macOS with Arial /
Apple Color Emoji, not the iOS system font. No native gesture, pixel-fidelity,
keyboard, accessibility, real messaging, remote attachment fetching or network
delivery behavior is claimed. Avatars and attachment placeholders are editable
geometry; no external photo or font license is implied.
