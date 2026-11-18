# UI agent STATUS — branch `devin-agent-ui`, worktree `imv-wt/ui`

## Done

- **Evidence** (owned docs, citations inside):
  - `work/ui/behavior-evidence.md` — tapback anchoring, send lifecycle, phone-vs-world space, copy-length layout, verified anatomy
  - `work/ui/attachments-evidence.md` — Onkeiki card/iMessage-app doc claims vs footage; card arrival/expand/clip verified
  - `work/ui/priority-list.md` — 12-item credibility-damage ranking with v2 fix per item
  - `work/ui/unfamiliar-test.md` — stress test, defects, verdict
- **Components v2** in `work/ui/components/` (`components-v2.mjs` 476 lines, `textmetrics.mjs`):
  `MessageBubble` (auto-wrap/auto-height, measured tail, tail-on-last-run, group sender chrome, child-anchored tapback), `TapbackBadge`, `TypingIndicator`, `Composer` (full draft→send lifecycle incl. fill sweep + caret), `AppCard` (badge top-left, cash skin, caption/CTA, tail), `PhotoStrip` (clipped carousel), `DeviceFrame` (screen clip + Dynamic Island), `NavBar`, `VoiceMessage`, `DeliveryStatus`, `AppDrawer`, `Avatar`, `CameraRig`. Stable ids, `meta` exposes computed sizes for stacking.
- **Motion proofs** (html engine, real renders — not stills):
  `work/ui/components/previews/thread.mp4` (scroll+tapback+send lifecycle),
  `device.mp4` (camera move, screen rigid in frame, world props separate),
  `card.mp4` (arrival→expand morph, clip), `extras.mp4` (voice + drawer),
  `unfamiliar.mp4` (long names/emoji/3 photos/tapback/reply — passes, see test doc).
- **Handoffs**: `components.md` (usage + caveat table), `gesture-evidence.md` (verified vs inferred), this file.
- **Skill proposals**: `work/ui/skill-proposals/` (patch proposals, not applied — skill tree is not owned).

## Defects fixed during verification

- Path serialization emitted `M,27.2,0` comma-arrays → corrected segment handling for H/V/Z.
- Outgoing text overflowed bubble → real font metrics + corrected padding.
- Composer `+` rendered as black blob (open stroked path) → two filled rects.
- NavBar had no backdrop → translucent `#f2f2f7e6` + blur added.

## Open / honest gaps

- `stroke`-only paths (mic arc, send arrow) render correctly in html engine but depend on engine honoring `fill:'none'` — Pillow/Remotion/GSAP adapters not yet exercised with v2 output. **Verify per-engine before shipping a film.**
- Emoji parity across engines (Chrome=Apple, Pillow=Noto) — raster substitution path documented but not built.
- Photo "swipeable stack" (4+ images), other-party tapback side, long-scroll retention: unverified gaps, documented.
- `test-scene.mjs` builders are dev harness, not a stable API; sibling agents should import `components-v2.mjs` directly.

## For the observer/catalog agent

- Gesture evidence (verified vs inferred, film+frame citations): `handoffs/out/ui/gesture-evidence.md`.
- Do not cite Onkeiki docs as behavior truth — the card-stack and group-restriction claims are unverified/contradicted; see `attachments-evidence.md`.
