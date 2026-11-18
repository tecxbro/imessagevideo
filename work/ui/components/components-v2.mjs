/** Editable UI components v2 — evidence-grounded rebuild of director/components.mjs.
 * Same scene-contract output (see scripts/shared/SCHEMA.md): plain layers, stable ids.
 * Metrics verified against 05-linq / 04-poke source frames + measured scenes; see
 * work/ui/behavior-evidence.md for citations.
 *
 * Geometry constants below are normalized to fontSize where marked `·fs`.
 */
import {textBox, measureLine} from './textmetrics.mjs';

export const TOKENS = Object.freeze({
  paper: '#ffffff',
  ink: '#000000',
  muted: '#8e8e93',
  blue: '#3581f4',          // measured dominant outgoing fill (linq scene + f750)
  blueAlt: '#007efe',       // measured alternate (linq early shots, send button)
  incoming: '#e6e6e6',      // measured incoming fill
  line: '#d1d1d6',
  caret: '#0088ff',         // measured composer caret
  font: '-apple-system, "SF Pro Text", "Helvetica Neue", Arial, sans-serif',
});

const safeId = id => {
  if (typeof id !== 'string' || !/^[-a-zA-Z0-9_]+$/.test(id)) throw Error('Use a unique simple component id');
  return id;
};
const rect = (id, x, y, width, height, fill, radius = 0, extra = {}) =>
  ({id, type: 'rect', x, y, width, height, fill, radius, ...extra});
const circle = (id, x, y, d, fill, extra = {}) =>
  ({id, type: 'circle', x, y, width: d, height: d, fill, ...extra});
const text = (id, value, x, y, size = 17, extra = {}) =>
  ({id, type: 'text', text: String(value), x, y, fontSize: size, fontFamily: TOKENS.font, fill: TOKENS.ink, ...extra});
const group = (id, x, y, children, extra = {}) =>
  ({id: safeId(id), type: 'group', x, y, children, ...extra});
const path = (id, d, fill, extra = {}) => ({id, type: 'path', d, fill, ...extra});
export {rect, circle, text, group, path};

/** Single-path bubble body INCLUDING the tail hook (traced from the measured scene's
 *  outgoing polygon, normalized). Tail sits on the bottom corner ~0.68·fs in from the
 *  side edge, dips ~0.12·fs below the bottom edge, with the concave bite above it.
 *  side: 'outgoing' = tail bottom-right; 'incoming' = bottom-left. */
export function bubbleBodyPath(w, h, r, side = 'outgoing') {
  const fs = r / 1.15;                        // recover font scale from radius convention
  const k = r * 0.5523;                        // circle-approx cubic constant
  const tailIn = Math.min(0.82 * fs, w * 0.2); // pinch inset from tail-side edge
  const tipIn = Math.min(0.68 * fs, w * 0.18); // tip inset from tail-side edge
  const tipDrop = 0.115 * fs;
  const biteTop = h - 0.42 * fs;
  // Build the outline in "tail on right" space, then mirror x for incoming.
  const segs = [
    ['M', r, 0],
    ['H', w - r],
    ['C', w - r + k, 0, w, r - k, w, r],
    ['V', h - r],
    // bottom-right corner arc — but stop short into the tail pinch
    ['C', w, h - r * 0.45, w - r * 0.28, h - 0.55 * fs - r * 0.2, w - tailIn, biteTop],
    // concave bite: edge runs nearly straight down
    ['C', w - tailIn - 0.4, biteTop + 0.13 * fs, w - tailIn - 0.3, h - 0.22 * fs, w - tailIn + 1.2, h - 0.14 * fs],
    // convex hook down-right to the tip
    ['C', w - tipIn - 0.18 * fs, h - 0.06 * fs, w - tipIn - 0.06 * fs, h + tipDrop * 0.55, w - tipIn, h + tipDrop],
    // tip nub return
    ['C', w - tipIn + 0.04 * fs, h + tipDrop, w - tipIn + 0.08 * fs, h + tipDrop * 0.8, w - tipIn - 0.12 * fs, h + tipDrop * 0.45],
    // rejoin bottom edge
    ['C', w - tipIn - 0.25 * fs, h + 0.04 * fs, w - tipIn - 0.4 * fs, h - 0.01 * fs, w - tipIn - 0.55 * fs, h],
    ['H', r],
    ['C', r - k, h, 0, h - r + k, 0, h - r],
    ['V', r],
    ['C', 0, r - k, r - k, 0, r, 0],
    ['Z'],
  ];
  const mirror = side === 'incoming';
  const fx = v => mirror ? w - v : v;
  return segs.map(([cmd, ...nums]) => {
    if (cmd === 'Z') return 'Z';
    if (cmd === 'H') return `H ${fx(nums[0]).toFixed(2)}`;
    if (cmd === 'V') return `V ${nums[0].toFixed(2)}`;
    const out = [];
    for (let i = 0; i < nums.length; i += 2) out.push(fx(nums[i]).toFixed(2), nums[i + 1].toFixed(2));
    return `${cmd} ${out.join(' ')}`;
  }).join(' ');
}
const cubicSeg = (p0, p1, p2, p3) =>
  `C ${p1[0]} ${p1[1]}, ${p2[0]} ${p2[1]}, ${p3[0]} ${p3[1]}`;

/** Tapback badge — a small bubble with emoji, anchored to a parent bubble/card corner.
 *  Verified anatomy (linq f750, poke f410): badge ~1.1:1, same blue for YOUR reactions,
 *  two descending tail bumps on the side toward the reactor's screen edge.
 *  from='me' → top-right corner, bumps point down-right; 'them' → top-left, down-left. */
export function TapbackBadge({id, x = 0, y = 0, size = 30, emoji = '👍', from = 'me'}) {
  safeId(id);
  const h = size, w = size * 1.12, r = size * 0.42;
  const rightSide = from === 'me';
  const bump1d = size * 0.3, bump2d = size * 0.14;
  const b1x = rightSide ? w - bump1d * 0.9 : -bump1d * 0.1;
  const b2x = rightSide ? w + bump1d * 0.15 : -bump1d * 0.15 - bump2d;
  return group(id, x, y, [
    circle(id + '-bump1', b1x, h - bump1d * 0.35, bump1d, TOKENS.blue),
    circle(id + '-bump2', b2x, h + bump1d * 0.5, bump2d, TOKENS.blue),
    rect(id + '-badge', 0, 0, w, h, TOKENS.blue, r),
    text(id + '-emoji', emoji, w / 2, h * 0.16, size * 0.58, {textAnchor: 'middle'}),
  ], {originX: rightSide ? w * 0.25 : w * 0.75, originY: h});
}

/** Message bubble v2: real word-wrap + auto height + measured radius/tail.
 * Params: side, copy, fontSize, maxWidth, tail (last-of-run only — verified rule),
 * tapback {emoji,from}, senderName, senderAvatar {src|initials,fill}, fill, textFill.
 * Children ids: -body, -copy, -name, -avatar*, -tapback. meta.{w,h,lines} attached. */
export function MessageBubble({
  id, x = 0, y = 0, side = 'outgoing', copy = 'Can you book it?', fontSize = 17,
  maxWidth = 260, tail = true, tapback = null, senderName = null, senderAvatar = null,
  fill, textFill, padX, padY, lineHeight,
}) {
  safeId(id);
  if (!['incoming', 'outgoing'].includes(side)) throw Error('Invalid message side');
  padX = padX ?? Math.round(fontSize * 0.72);
  padY = padY ?? Math.round(fontSize * 0.5);
  const box = textBox(copy, fontSize, maxWidth - padX * 2, lineHeight);
  // +4% width margin: if the runtime font is wider than the metric table (e.g. Arial
  // fallback), the bubble still contains its text. Slightly wide reads as iOS padding.
  const w = Math.max(Math.ceil(box.maxLineWidth * 1.04 + padX * 2), fontSize * 2.2);
  const h = Math.ceil(box.height + padY * 2);
  const r = Math.min(h / 2, fontSize * 1.15);
  const color = fill ?? (side === 'outgoing' ? TOKENS.blue : TOKENS.incoming);
  const ink = textFill ?? (side === 'outgoing' ? '#ffffff' : TOKENS.ink);
  const nameH = senderName ? fontSize * 0.95 : 0;
  const bodyLayer = tail
    ? path(id + '-body', bubbleBodyPath(w, h, r, side), color)
    : rect(id + '-body', 0, 0, w, h, color, r);
  const inner = group(id + '-msg', 0, nameH, [bodyLayer,
    text(id + '-copy', box.lines.join('\n'), padX, padY - fontSize * 0.1, fontSize,
      {fill: ink, lineHeight: box.lineHeight})]);
  const children = [inner];
  if (senderName) children.unshift(text(id + '-name', senderName,
    (side === 'incoming' ? padX * 0.4 : w - padX * 0.4), 0, fontSize * 0.7,
    {fill: TOKENS.muted, textAnchor: side === 'incoming' ? 'start' : 'end'}));
  if (senderAvatar) {
    const d = fontSize * 1.65, ax = side === 'incoming' ? -d - 6 : w + 6, ay = nameH + h - d;
    if (senderAvatar.src) children.push({id: id + '-avatar', type: 'image', src: senderAvatar.src, x: ax, y: ay, width: d, height: d});
    else children.push(group(id + '-avatar', ax, ay, [
      circle(id + '-avatar-disc', 0, 0, d, senderAvatar.fill ?? '#d8e2f0'),
      text(id + '-avatar-i', senderAvatar.initials ?? '?', d / 2, d * 0.28, d * 0.34, {textAnchor: 'middle', fontWeight: 600}),
    ]));
  }
  if (tapback) {
    const from = tapback.from ?? 'me';
    const badgeW = fontSize * 1.9, tx = from === 'me' ? w - badgeW * 0.72 : -badgeW * 0.28;
    children.push(TapbackBadge({id: id + '-tapback', x: tx, y: nameH - fontSize * 0.55,
      size: fontSize * 1.7, emoji: tapback.emoji ?? '👍', from}));
  }
  const g = group(id, x, y, children);
  g.meta = {w, h: h + nameH, r, lines: box.lines, overflow: box.overflow};
  return g;
}

/** Typing indicator — gray pill, 3 dots bouncing in sequence. Verified presence at the
 *  incoming position before replies (danieltian ~f185-230, photon-mini). Duration ~0.9s loop. */
export function TypingIndicator({id, x = 0, y = 0, fontSize = 17, t0 = 0, cycles = 2}) {
  safeId(id);
  const h = fontSize * 1.7, w = fontSize * 3.1, d = fontSize * 0.5;
  const gap = (w - d * 3) / 4, dots = [];
  const period = 0.9, rise = d * 0.55;
  for (let i = 0; i < 3; i++) {
    const dot = circle(id + '-dot' + i, gap + i * (d + gap), (h - d) / 2 + d * 0.15, d, '#8e8e93');
    const kf = [{t: 0, value: (h - d) / 2 + d * 0.15}];
    for (let c = 0; c < cycles; c++) {
      const t = t0 + c * period + i * 0.15;
      kf.push({t, value: (h - d) / 2 + d * 0.15},
        {t: t + 0.25, value: (h - d) / 2 - rise, ease: 'easeOut'},
        {t: t + 0.55, value: (h - d) / 2 + d * 0.15, ease: 'easeIn'});
    }
    dot.keyframes = {y: kf};
    dots.push(dot);
  }
  const g = group(id, x, y, [rect(id + '-pill', 0, 0, w, h, TOKENS.incoming, h / 2), ...dots]);
  g.meta = {w, h};
  return g;
}

/** Composer — verified state machine (linq v19-intro-composer):
 *  empty: placeholder + mic visible, no send. typing: placeholder+mic END at first char,
 *  caret tracks end, send circle fades in INSIDE field right end (~3-frame blue sweep).
 *  send: typed clears, mic+placeholder return; the outgoing bubble is a SEPARATE layer —
 *  this builder only owns composer chrome, never duplicates the sent message.
 *  `typedSteps` = number of staggered prefix layers for char-by-char typing (0 = instant). */
export function Composer({
  id, x = 0, y = 0, width = 430, height = 36, placeholder = 'iMessage',
  typed = '', typeStart = 0, typeEnd = null, sendT = null, typedSteps = 6,
}) {
  safeId(id);
  const plusD = height * 1.0;
  const fieldX = plusD + 8, fieldW = width - fieldX;
  const children = [];
  children.push(circle(id + '-plus', 0, 0, plusD, '#ffffff',
    {shadow: {x: 0, y: 1, blur: 3, color: '#00000022'}}));
  children.push(group(id + '-plus-glyph', 0, 0, [
    rect(id + '-plus-h', plusD * 0.3, plusD / 2 - plusD * 0.028, plusD * 0.4, plusD * 0.056, '#3c3c43', plusD * 0.02),
    rect(id + '-plus-v', plusD / 2 - plusD * 0.028, plusD * 0.3, plusD * 0.056, plusD * 0.4, '#3c3c43', plusD * 0.02)]));
  children.push(rect(id + '-field', fieldX, 0, fieldW, height, '#ffffff', height / 2,
    {stroke: TOKENS.line, strokeWidth: 0.5, shadow: {x: 0, y: 1, blur: 4, color: '#0000001c'}}));
  // Verified state windows: placeholder+mic exist while field is empty; they END at
  // typeStart (first char) and return at sendT. Send exists only while text exists.
  const typing = typeStart > 0 && typed !== '';
  children.push(text(id + '-placeholder', placeholder, fieldX + height * 0.35, height * 0.26,
    height * 0.42, {fill: TOKENS.muted, end: typing ? typeStart : undefined}));
  if (sendT !== null) children.push(text(id + '-placeholder-post', placeholder,
    fieldX + height * 0.35, height * 0.26, height * 0.42, {fill: TOKENS.muted, start: sendT}));
  // mic icon (drawn minimal: capsule + stem + arc), same empty-state windows
  const micX = fieldX + fieldW - height * 0.72, micW = height * 0.16;
  const micChildren = [
    rect(id + '-mic-capsule', micW * 0.5, 0, micW, micW * 1.55, '#8e8e93', micW / 2),
    {id: id + '-mic-arc', type: 'path',
      d: `M ${-micW * 0.5} ${micW * 1.1} Q ${-micW * 0.5} ${micW * 2.2} ${micW * 0.5} ${micW * 2.2} Q ${micW * 1.5} ${micW * 2.2} ${micW * 1.5} ${micW * 1.1}`,
      fill: 'none', stroke: '#8e8e93', strokeWidth: micW * 0.22},
    rect(id + '-mic-stem', micW * 0.9, micW * 2.2, micW * 0.2, micW * 0.5, '#8e8e93', micW * 0.1),
    rect(id + '-mic-base', micW * 0.55, micW * 2.7, micW * 0.9, micW * 0.22, '#8e8e93', micW * 0.11),
  ];
  children.push(group(id + '-mic', micX, height * 0.2, micChildren,
    {end: typing ? typeStart : undefined}));
  if (sendT !== null) children.push(group(id + '-mic-post', micX, height * 0.2,
    micChildren.map(c => ({...c, id: c.id + '-post'})), {start: sendT}));
  // send control inside field's right end — exists only while text exists.
  // Measured fill sweep #c2d2fd→#70a3ff→#007efe over ~3 frames at appear time.
  const sendD = height * 0.78, sendX = fieldX + fieldW - sendD - height * 0.11, sendY = (height - sendD) / 2;
  const sendStart = typing ? typeStart + 0.03 : null;
  const sendFill = circle(id + '-send-fill', 0, 0, sendD, TOKENS.blueAlt);
  if (sendStart !== null) sendFill.keyframes = {fill: [
    {t: 0, value: TOKENS.blueAlt},
    {t: sendStart, value: '#c2d2fd', ease: 'hold'},
    {t: sendStart + 0.033, value: '#70a3ff'},
    {t: sendStart + 0.07, value: TOKENS.blueAlt}]};
  const sendGroup = group(id + '-send', sendX, sendY, [
    sendFill,
    {id: id + '-send-arrow', type: 'path',
      d: `M ${sendD * 0.5} ${sendD * 0.24} L ${sendD * 0.5} ${sendD * 0.72} M ${sendD * 0.26} ${sendD * 0.42} L ${sendD * 0.5} ${sendD * 0.24} L ${sendD * 0.74} ${sendD * 0.42}`,
      fill: 'none', stroke: '#ffffff', strokeWidth: sendD * 0.075},
  ], sendStart === null
      ? (typed ? {} : {opacity: 0})
      : {start: sendStart, end: sendT ?? undefined});
  children.push(sendGroup);
  // typed copy — either one layer (instant) or staggered prefix layers (char typing)
  if (typed) {
    if (typeStart > 0 && typedSteps > 0) {
      const chars = [...typed];
      const dur = (sendT ?? typeEnd ?? typeStart + 1) - typeStart;
      const stepT = Math.max(dur / Math.min(chars.length, typedSteps), 0.033);
      const n = Math.min(chars.length, typedSteps);
      for (let i = 0; i < n; i++) {
        const upto = Math.ceil((i + 1) / n * chars.length);
        children.push(text(id + '-typed-' + i, chars.slice(0, upto).join(''),
          fieldX + height * 0.35, height * 0.26, height * 0.42,
          {start: typeStart + i * stepT, end: i === n - 1 ? (sendT ?? undefined) : typeStart + (i + 1) * stepT}));
      }
    } else {
      children.push(text(id + '-typed', typed, fieldX + height * 0.35, height * 0.26,
        height * 0.42, {start: typeStart > 0 ? typeStart : 0, end: sendT ?? undefined}));
    }
    if (sendT !== null) children.push(rect(id + '-caret', fieldX + height * 0.35 + measureLine(typed, height * 0.42) + 2,
      height * 0.24, 1.6, height * 0.52, TOKENS.caret, 0, {end: sendT}));
  }
  const g = group(id, x, y, children);
  g.meta = {w: width, h: height};
  return g;
}

/** App card — measured anatomy: rounded surface + app-icon badge overlapping TOP-LEFT
 *  corner + content area + caption/CTA + optional tail hook (it IS an incoming message).
 *  skin: 'light' (default) | 'cash' (black card, white pill CTA — Apple Cash pattern). */
export function AppCard({
  id, x = 0, y = 0, width = 240, mediaHeight = 0, title = 'Your booking',
  caption = 'Tap for details', cta = null, badge = null, mediaSrc = null,
  tail = true, skin = 'light', fontSize = 17, mediaChildren = [],
}) {
  safeId(id);
  const dark = skin === 'cash';
  const surface = dark ? '#1b1b1b' : '#ffffff';
  const inkColor = dark ? '#ffffff' : TOKENS.ink;
  const captionY = mediaHeight + fontSize * 1.1;
  const ctaH = cta ? fontSize * 2.0 : 0;
  const h = mediaHeight + (title ? fontSize * 1.5 : 0) + (caption ? fontSize * 1.35 : fontSize * 0.7) + ctaH + fontSize * 0.6;
  const r = Math.min(fontSize * 1.6, h * 0.5);
  const children = [];
  if (tail) children.push(path(id + '-surface', bubbleBodyPath(width, h, r, 'incoming'), surface));
  else children.push(rect(id + '-surface', 0, 0, width, h, surface, r));
  const body = children.splice(0);
  const inner = group(id + '-card', 0, 0, body);
  children.push(inner);
  if (mediaSrc || mediaChildren.length) {
    const strip = group(id + '-media', 0, 0,
      mediaSrc ? [{id: id + '-img', type: 'image', src: mediaSrc, x: 0, y: 0, width, height: mediaHeight}] : mediaChildren,
      {clip: {x: 0, y: 0, width, height: mediaHeight, radius: r}});
    inner.children.push(strip);
  }
  let ty = mediaHeight + fontSize * 0.55;
  if (title) { inner.children.push(text(id + '-title', title, fontSize * 0.85, ty, fontSize, {fill: inkColor, fontWeight: 600})); ty += fontSize * 1.35; }
  if (caption) { inner.children.push(text(id + '-caption', caption, fontSize * 0.85, ty, fontSize * 0.8, {fill: dark ? '#c7c7cc' : TOKENS.muted})); ty += fontSize * 1.25; }
  if (cta) {
    inner.children.push(group(id + '-cta', fontSize * 0.85, ty, [
      rect(id + '-cta-pill', 0, 0, width - fontSize * 1.7, ctaH, dark ? '#ffffff' : TOKENS.blueAlt, ctaH / 2),
      text(id + '-cta-label', cta, width / 2 - fontSize * 0.85, ctaH * 0.28, fontSize * 0.9,
        {fill: dark ? '#000000' : '#ffffff', textAnchor: 'middle', fontWeight: 600}),
    ]));
  }
  if (badge) {
    const d = fontSize * 2.1;
    children.unshift(group(id + '-badge', -d * 0.28, -d * 0.3, [
      circle(id + '-badge-disc', 0, 0, d, badge.color ?? '#ffffff', {stroke: TOKENS.line, strokeWidth: 0.5}),
      badge.src
        ? {id: id + '-badge-img', type: 'image', src: badge.src, x: d * 0.18, y: d * 0.18, width: d * 0.64, height: d * 0.64}
        : text(id + '-badge-i', badge.label ?? 'A', d / 2, d * 0.3, d * 0.38, {textAnchor: 'middle', fontWeight: 700, fill: badge.ink ?? TOKENS.ink}),
    ]));
  }
  const g = group(id, x, y, children);
  g.meta = {w: width, h};
  return g;
}

/** Photo strip — images translate X inside a clip while chrome stays fixed.
 *  Verified: restaurant card photos scroll left under fixed title/Directions/tabs
 *  (linq f1050-1150). images: [{src,width}] laid left→right; t0/duration & speed drive
 *  the x keyframes. Renders as its own clipped group — compose inside AppCard media slot. */
export function PhotoStrip({id, x = 0, y = 0, width = 240, height = 90, images = [], gap = 6, speed = 30, t0 = 0, duration = 4}) {
  safeId(id);
  let cx = 0;
  const kids = images.map((img, i) => {
    const iw = img.width ?? height * 1.4;
    const layer = {id: `${id}-img${i}`, type: 'image', src: img.src, x: cx, y: 0, width: iw, height,
      keyframes: {x: [{t: t0, value: cx}, {t: t0 + duration, value: cx - speed * duration}]}};
    cx += iw + gap;
    return layer;
  });
  const g = group(id, x, y, kids, {clip: {x: 0, y: 0, width, height, radius: height * 0.16}});
  g.meta = {w: width, h: height, contentWidth: cx - gap};
  return g;
}

/** Device frame — phone-space container. Verified: screen content is rigidly attached
 *  to the hardware through camera transforms (gallery f330-480); keep children inside
 *  `-screen` and transform the OUTER group with a CameraRig. */
export function DeviceFrame({id, x = 0, y = 0, width = 300, height = 620, children = [], bezel = '#0b0b0f', wallpaper = '#ffffff'}) {
  safeId(id);
  const outerR = width * 0.155, bw = width * 0.032, screenR = outerR - bw * 0.8;
  const islandW = width * 0.28, islandH = width * 0.062;
  return group(id, x, y, [
    rect(id + '-bezel', 0, 0, width, height, bezel, outerR),
    group(id + '-screen', bw, bw, [
      rect(id + '-wallpaper', 0, 0, width - bw * 2, height - bw * 2, wallpaper, 0),
      ...children,
    ], {clip: {x: 0, y: 0, width: width - bw * 2, height: height - bw * 2, radius: screenR}}),
    rect(id + '-island', (width - islandW) / 2, height * 0.017, islandW, islandH, bezel, islandH / 2),
    rect(id + '-home', width * 0.36, height - bw - 5, width * 0.28, 4, '#ffffff88', 2),
  ]);
}

/** Conversation nav bar — back chevron, centered avatar+name, right camera icon.
 *  Kept separate from DeviceFrame so it can pin to any screen top. */
export function NavBar({id, x = 0, y = 0, width = 300, name = 'Muse', avatar = null, fontSize = 15, backdrop = '#f2f2f7e6'}) {
  safeId(id);
  const h = fontSize * 3.2;
  const kids = [
    rect(id + '-bg', 0, 0, width, h, backdrop, 0, {blur: backdrop.length > 7 ? 8 : 0}),
    text(id + '-back', '‹', fontSize * 0.7, h * 0.28, fontSize * 1.9, {fill: TOKENS.blueAlt}),
    text(id + '-name', name, width / 2, h * 0.42, fontSize * 0.95, {textAnchor: 'middle', fontWeight: 600}),
    // facetime-style camera glyph (simple rounded body + lens nub)
    group(id + '-cam', width - fontSize * 1.9, h * 0.42, [
      rect(id + '-cam-body', 0, 0, fontSize * 1.25, fontSize * 0.85, TOKENS.blueAlt, fontSize * 0.18),
      {id: id + '-cam-lens', type: 'path',
        d: `M ${fontSize * 1.28} ${fontSize * 0.28} L ${fontSize * 1.62} ${fontSize * 0.1} L ${fontSize * 1.62} ${fontSize * 0.75} L ${fontSize * 1.28} ${fontSize * 0.57} Z`,
        fill: TOKENS.blueAlt},
    ]),
  ];
  if (avatar) kids.splice(1, 0, group(id + '-avatar', width / 2 - fontSize * 0.75, h * 0.02, [
    circle(id + '-avatar-disc', 0, 0, fontSize * 1.5, avatar.fill ?? '#d8e2f0'),
    text(id + '-avatar-i', avatar.initials ?? '?', fontSize * 0.75, fontSize * 0.42, fontSize * 0.55, {textAnchor: 'middle', fontWeight: 600}),
  ]));
  kids.push(rect(id + '-rule', 0, h - 0.5, width, 0.5, TOKENS.line));
  const g = group(id, x, y, kids);
  g.meta = {h};
  return g;
}

/** Voice message bubble — play circle + waveform bars + duration. Bar profile measured
 *  from 04-poke p0310-wave-*: ~4-5px bars, radius 2-2.5, heights 18-72 at its scale. */
export function VoiceMessage({id, x = 0, y = 0, fontSize = 17, seconds = 4, side = 'incoming', transcript = null, seed = 7}) {
  safeId(id);
  const bars = 40, barW = fontSize * 0.16, gap = fontSize * 0.14;
  const playD = fontSize * 1.9, pad = fontSize * 0.6;
  const stripW = bars * (barW + gap);
  const w = pad * 2 + playD + gap * 2 + stripW + fontSize * 1.6;
  const h = fontSize * 3.2;
  const rng = (() => { let s = seed; return () => (s = (s * 16807) % 2147483647) / 2147483647; })();
  const children = [
    rect(id + '-body', 0, 0, w, h, side === 'outgoing' ? TOKENS.blue : TOKENS.incoming, Math.min(h / 2, fontSize * 1.15)),
    circle(id + '-play', pad, (h - playD) / 2, playD, side === 'outgoing' ? '#ffffff' : TOKENS.blueAlt),
    {id: id + '-play-glyph', type: 'path',
      d: `M ${pad + playD * 0.38} ${h / 2 - playD * 0.22} L ${pad + playD * 0.7} ${h / 2} L ${pad + playD * 0.38} ${h / 2 + playD * 0.22} Z`,
      fill: side === 'outgoing' ? TOKENS.blue : '#ffffff'},
  ];
  const stripX = pad + playD + gap * 2, mid = h / 2 - fontSize * 0.1;
  for (let i = 0; i < bars; i++) {
    const bh = fontSize * (0.45 + rng() * 1.5);
    children.push(rect(`${id}-wave-${i}`, stripX + i * (barW + gap), mid - bh / 2, barW, bh,
      side === 'outgoing' ? '#ffffffcc' : '#8e8e93', barW / 2));
  }
  children.push(text(id + '-dur', `0:${String(seconds).padStart(2, '0')}`,
    w - pad - fontSize * 1.35, h - fontSize * 1.15, fontSize * 0.68,
    {fill: side === 'outgoing' ? '#ffffffcc' : TOKENS.muted}));
  const g = group(id, x, y, children);
  if (transcript) g.children.push(text(id + '-transcript', transcript, 2, h + fontSize * 0.5,
    fontSize * 0.8, {fill: TOKENS.muted}));
  g.meta = {w, h};
  return g;
}

/** "Delivered" / "Read 2:41 PM" — right-aligned status under last outgoing bubble.
 *  anchorX = absolute x the label's right edge aligns to (thread right margin). */
export function DeliveryStatus({id, y = 0, copy = 'Delivered', fontSize = 17, anchorX = 300, start = 0}) {
  safeId(id);
  return text(id, copy, anchorX, y, fontSize * 0.72,
    {fill: TOKENS.muted, textAnchor: 'end', start});
}

/** App drawer — the "+" sheet: light panel, handle, app rows (icon + label).
 *  Verified list order in linq f95-135: Photos, Apple Cash, Polls, Store, then scroll. */
export function AppDrawer({id, x = 0, y = 0, width = 300, apps = [
  {name: 'Photos', color: '#e7f3ff', ink: '#347ff3'},
  {name: 'Apple Cash', color: '#1b1b1b', ink: '#ffffff'},
  {name: 'Polls', color: '#f2a544', ink: '#ffffff'},
  {name: 'Store', color: '#347ff3', ink: '#ffffff'},
], fontSize = 15, maxRows = 4}) {
  safeId(id);
  const rowH = fontSize * 3.1, h = rowH * Math.min(apps.length, maxRows) + fontSize * 2.6;
  const kids = [
    rect(id + '-sheet', 0, 0, width, h, '#f6f6f8', fontSize * 1.4),
    rect(id + '-handle', width / 2 - fontSize * 1.2, fontSize * 0.55, fontSize * 2.4, fontSize * 0.3, '#c4c7cc', fontSize * 0.15),
  ];
  apps.slice(0, maxRows).forEach((app, i) => {
    const ry = fontSize * 1.7 + i * rowH;
    kids.push(group(id + '-app-' + i, fontSize * 0.9, ry, [
      circle(id + '-app-' + i + '-icon', 0, 0, fontSize * 2.2, app.color),
      text(id + '-app-' + i + '-glyph', app.glyph ?? app.name[0], fontSize * 1.1, fontSize * 0.62, fontSize * 0.95, {textAnchor: 'middle', fill: app.ink, fontWeight: 600}),
      text(id + '-app-' + i + '-name', app.name, fontSize * 2.9, fontSize * 0.7, fontSize * 1.05, {fontWeight: 500}),
    ]));
  });
  const g = group(id, x, y, kids, {clip: {x: 0, y: 0, width, height: h, radius: fontSize * 1.4}});
  g.meta = {h};
  return g;
}

/** CameraRig — unchanged contract from v1: parent transform for world-space moves. */
export function CameraRig({id = 'camera', children = [], keyframes = {}, x = 0, y = 0, originX = 480, originY = 270}) {
  return group(id, x, y, children, {originX, originY, keyframes});
}

/** Avatar — same as v1 plus optional photo src. */
export function Avatar({id, x = 0, y = 0, size = 42, initials = 'JD', fill = '#d8e2f0', src = null}) {
  safeId(id);
  return group(id, x, y, src
    ? [{id: id + '-photo', type: 'image', src, x: 0, y: 0, width: size, height: size}]
    : [circle(id + '-disc', 0, 0, size, fill),
       text(id + '-initials', initials, size / 2, size * 0.27, size * 0.34, {textAnchor: 'middle', fontWeight: 600})]);
}

export const COMPONENTS_V2 = Object.freeze([
  {name: 'MessageBubble', purpose: 'Auto-wrap bubble: measured radius/tail, tapback, group sender chrome', parameters: ['copy', 'side', 'fontSize', 'maxWidth', 'tail', 'tapback', 'senderName', 'senderAvatar']},
  {name: 'TapbackBadge', purpose: 'Reaction badge anchored to a parent corner — child of the message group', parameters: ['emoji', 'from', 'size']},
  {name: 'TypingIndicator', purpose: 'Three-dot incoming pill with sequenced bounce', parameters: ['fontSize', 't0', 'cycles']},
  {name: 'Composer', purpose: 'Field lifecycle: placeholder+mic → typed+send → clear; char-by-char typedSteps', parameters: ['placeholder', 'typed', 'typeStart', 'sendT', 'typedSteps']},
  {name: 'AppCard', purpose: 'App message card: top-left app badge, media slot, caption, CTA pill, tail', parameters: ['width', 'title', 'caption', 'cta', 'badge', 'mediaSrc', 'skin']},
  {name: 'PhotoStrip', purpose: 'Horizontally scrolling images clipped under fixed chrome', parameters: ['images', 'speed', 'gap', 'duration']},
  {name: 'DeviceFrame', purpose: 'Phone-space container: bezel, island, clipped screen group', parameters: ['width', 'height', 'children']},
  {name: 'NavBar', purpose: 'Conversation chrome: back, avatar+name, camera icon', parameters: ['width', 'name', 'avatar']},
  {name: 'VoiceMessage', purpose: 'Play button + measured-profile waveform + duration + transcript', parameters: ['seconds', 'side', 'transcript', 'seed']},
  {name: 'DeliveryStatus', purpose: 'Delivered/Read label right-aligned under last outgoing', parameters: ['text', 'fontSize', 'anchorX']},
  {name: 'AppDrawer', purpose: '"+" app list sheet rows (Photos/Apple Cash/Polls/Store…)', parameters: ['apps', 'maxRows', 'fontSize']},
  {name: 'Avatar', purpose: 'Initials or photo disc', parameters: ['size', 'initials', 'fill', 'src']},
  {name: 'CameraRig', purpose: 'Parent transform, separate from local UI layout', parameters: ['children', 'keyframes', 'originX', 'originY']},
]);
