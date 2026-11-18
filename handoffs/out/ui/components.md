# Components v2 — iMessage UI kit for filmmakers

Source: `work/ui/components/components-v2.mjs` + `textmetrics.mjs`
Emit: scene JSON on the existing contract (`scripts/shared/SCHEMA.md`) — layers
`rect|circle|text|image|path|group`, source-pixel coords, output-second time,
`keyframes: {prop: [{t, value, ease}]}`.
Render proofs (html engine): `work/ui/components/previews/{thread,device,card,extras,unfamiliar}.mp4`

## Components

| Export | What it builds | Editable params (all optional except `id`) |
|---|---|---|
| `MessageBubble` | Wrapped, auto-height bubble: body path + measured comma-hook tail, wrap via canvas-measured SF Pro widths | `side`, `copy`, `fontSize`, `maxWidth`, `tail`, `tapback{emoji,from}`, `senderName`, `senderAvatar`, `fill`. `meta` = `{w,h,lines}` |
| `TapbackBadge` | Blue badge + emoji + two-bump tail toward its anchor | `emoji`, `from('me'|'them')`, `size`. Parent it inside the bubble/card group — it then rides every scroll/transform |
| `TypingIndicator` | Gray pill, 3 dots, sequential bounce (~0.9s loop) | `fontSize`, `t0`, `cycles` |
| `Composer` | `+` button, field, placeholder, mic, send circle (inside field, right end), typed copy, caret | `placeholder`, `typed`, `typeStart`, `sendT`, `typedSteps` (char-by-char reveal). Placeholder+mic end at `typeStart`, return at `sendT`; send-fill sweeps `#c2d2fd→#70a3ff→#007efe` |
| `AppCard` | App message: rounded surface + tail, app-icon badge overlapping top-left corner, media slot, title, caption, optional CTA pill | `skin('light'|'cash')` (cash = black card + white Pay pill), `badge{label,color,ink}`, `mediaChildren`, `mediaSrc`, `cta` |
| `PhotoStrip` | Image carousel inside a clipped rounded viewport (Linq restaurant-card pattern) | `images[{src,width}]`, `speed`, `t0`, `duration`, `gap`, `width/height` |
| `DeviceFrame` | Phone-space container: bezel, Dynamic Island, home bar, clipped `-screen` child group | `width`, `height`, `children` (go INSIDE `-screen`), `bezel`, `wallpaper` |
| `NavBar` | Back chevron, centered name + optional avatar, camera glyph, translucent backdrop | `name`, `avatar{initials,fill,src}`, `backdrop` |
| `VoiceMessage` | Bubble w/ play circle, ~44 seeded waveform bars, duration, optional transcript | `seconds`, `transcript`, `seed`, `side` |
| `DeliveryStatus` | Right-aligned gray `Delivered`/`Read h:mm` under last outgoing | `copy`, `anchorX`, `start` |
| `AppDrawer` | iOS 17 `+` app list (Photos/Apple Cash/Polls/Store…→Games grid) | `apps[{label,color,glyph}]`, `width` |
| `CameraRig` | Parent group carrying camera keyframes | `keyframes`, `originX/Y` — transform this, never child geometry |
| `Avatar` | Circle w/ initials or image | `initials`, `fill`, `src`, `size` |

## Scene-contract notes

- Import from `work/ui/components/`; builders return scene `group` layers — position them as siblings or inside `DeviceFrame`/thread groups.
- `MessageBubble` does real word-wrap + auto-height (canvas `measureText` width table embedded in `textmetrics.mjs`; fallback estimator offline). Do not hand-set width/height; read `meta.w/h` to stack siblings.
- Tapback = `tapback` param (child of the message group) or standalone `TapbackBadge` you parent yourself. Never emit it as a thread sibling — it must scroll with its message (verified linq f758-765).
- Tail rule: `tail:true` only on the last message of a consecutive same-side run. A card that ends a run carries the tail (`AppCard tail:true` default).
- Composer lifecycle: set `typeStart` + `sendT` once; the builder stamps every layer window. For a visible send, append the outgoing `MessageBubble` with `start = sendT` yourself — composer and thread are deliberately separate actors.
- `DeviceFrame` children are clipped to the screen. Transform the OUTER group (or `CameraRig`) for camera moves — hardware + screen move rigidly together (gallery f330-480).
- Card→panel expand is a morph on the same surface: fade/scale the card out while a panel group grows from its origin (proof in `card.mp4`).
- Emoji work inline in text under Chrome (Apple Color Emoji); Pillow renders Noto artwork. Keep emoji in copy; rasterize only for exact-match frames.
- Group chats: pass `senderName` + `senderAvatar`, and offset bubbles by the avatar gutter (`fontSize*2.3` used in test scenes).

## Caveat table

| Caveat | Detail |
|---|---|
| Font metric fidelity | Width table is canvas-measured system sans at 100px; exact iOS tracking can drift ~±1px/char at extreme sizes — re-render, don't guess |
| Emoji cross-engine | Chrome = Apple artwork; Pillow = Noto artwork. Pixel-parity requires `emojiImage` raster substitution (not yet built) |
| Tapback "them" side | Mirroring inferred — no film shows an other-party reaction |
| Long-scroll retention | Anchor verified over ~1 bubble-height scrolls; no film shows a tapback surviving a multi-screen scroll |
| Photo stack (4+ imgs) | Onkeiki's "swipeable stack" claim unverified in this library; `PhotoStrip` models the verified carousel instead |
| Typing cadence | Dot stagger (~0.15s offset) is stylized from footage, not sampled frame-exact |
| `AppDrawer` contents | App list/labels editable; filmed order (Photos→Cash→Polls→Store→Games) is the default |
| Send-flight gap | No film shows the bubble mid-flight out of the composer; v2 uses a cut + rise-in, matching filmed timing |
