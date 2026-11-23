/** Frame-indexed editable conversation. Times are authored output seconds. */
import {Avatar, CameraRig, group, rect, text} from './components.mjs';
import {easeValue, sampleTrack} from '../scripts/engines/common.mjs';
import {InlineAppCard, NativeAttachmentStack, NativePhotoCollage, PhotoStrip} from './conversation-media.mjs';

export {InlineAppCard, NativeAttachmentStack, NativePhotoCollage, PhotoStrip};

const DEFAULT_STYLE = {fontFamily: 'Arial, sans-serif', fontSize: 15, fontWeight: 400};
const INK = '#202127';
const BLUE = '#0b79ed';
const GRAY = '#e9e9ee';
const GUTTER = 15;
const ROW_GAP = 12;
const PAD_TOP = 15;
const PAD_BOTTOM = 13;
const HEADER = 68;
const FOOTER = 69;
const TYPE_PAD_X = 12;
const TYPE_PAD_Y = 7;
const clip = (width, height, radius = 0) => ({x: 0, y: 0, width, height, radius});
const key = (t, value, ease = 'hold') => ({t, value, ease});
const segmenter = new Intl.Segmenter(undefined, {granularity: 'grapheme'});
const graphemes = value => Array.from(segmenter.segment(value), entry => entry.segment);

/** Measure using the font and fallback stack of the actual exporter. */
export function wrapText(value, maxWidth, measureText, style = DEFAULT_STYLE) {
  if (!Number.isFinite(maxWidth) || maxWidth <= 0 || typeof measureText !== 'function') {
    throw new Error('Provide a positive wrap width and a text measurer');
  }
  const lines = [];
  for (const paragraph of String(value).split(/\r\n|\r|\n/)) {
    let line = '';
    let space = '';
    for (const token of paragraph.match(/\s+|\S+/gu) ?? []) {
      if (/^\s/u.test(token)) {
        space = line ? token : '';
        continue;
      }
      const next = line + space + token;
      space = '';
      if (measureText(next, style) <= maxWidth) {
        line = next;
        continue;
      }
      if (line) lines.push(line);
      line = '';
      if (measureText(token, style) <= maxWidth) {
        line = token;
        continue;
      }
      for (const char of graphemes(token)) {
        if (measureText(char, style) > maxWidth) throw new Error('A grapheme is wider than its text box');
        if (line && measureText(line + char, style) > maxWidth) {
          lines.push(line);
          line = '';
        }
        line += char;
      }
    }
    lines.push(line);
  }
  return lines;
}

function setAt(layer, property, t, value) {
  layer.keyframes ??= {};
  const track = layer.keyframes[property] ??= [key(0, layer[property])];
  if (track.at(-1).t === t) track.at(-1).value = value;
  else if (track.at(-1).value !== value) track.push(key(t, value));
}

function vector(id, d, fill = 'none', stroke = 'none', strokeWidth = 0) {
  return {id, type: 'path', d, fill, stroke, strokeWidth};
}

function oval(id, x, y, size, fill) {
  return {id, type: 'circle', x, y, width: size, height: size, fill};
}

function textLayout(value, width, style, measure) {
  const lines = wrapText(value, width - TYPE_PAD_X * 2, measure, style);
  const lineHeight = Math.ceil(style.fontSize * 1.25);
  return {
    text: lines.join('\n'),
    width: Math.min(width, Math.max(39, Math.ceil(Math.max(...lines.map(line => measure(line, style))) + TYPE_PAD_X * 2))),
    height: lines.length * lineHeight + TYPE_PAD_Y * 2,
    lineHeight,
  };
}

function tailPath(width, height, outgoing) {
  const cx = outgoing ? width : 0;
  const s = outgoing ? 1 : -1;
  return `M ${cx - 12 * s} ${height - 9} Q ${cx - 4 * s} ${height + 1} ${cx + 5 * s} ${height} Q ${cx} ${height - 4} ${cx - 1 * s} ${height - 12} Z`;
}

function tapback(id, value, anchorX, start, fontFamily) {
  const mark = value === 'heart'
    ? vector(id + '-mark', 'M 12 17 C 10 14.7 5.8 12.8 5.8 9.2 C 5.8 5.6 10.2 5.1 12 8 C 13.8 5.1 18.2 5.6 18.2 9.2 C 18.2 12.8 14 14.7 12 17 Z', '#ffc0d9')
    : text(id + '-mark', value, 12, 4, 13, {textAnchor: 'middle', fontFamily});
  const pop = [key(start, .72), key(start + .11, 1.12, 'easeOut'), key(start + .21, 1, 'easeInOut')];
  return group(id, anchorX, -10, [
    oval(id + '-dot-small', -3, 24, 3, BLUE), oval(id + '-dot', 0, 19, 6, BLUE),
    oval(id + '-badge', 0, 0, 24, BLUE), mark,
  ], {start, originX: 12, originY: 11, keyframes: {scaleX: pop, scaleY: pop}});
}

const mediaBuilders = {
  'photo-strip': PhotoStrip, 'native-stack': NativeAttachmentStack,
  'native-collage': NativePhotoCollage, 'app-card': InlineAppCard,
};

function prepareRow(message, {screenWidth, style, measure, frameOf, fps}) {
  const {id, side, text: copy, attachment, reaction, edit} = message;
  if (side !== 'incoming' && side !== 'outgoing') throw new Error(`Invalid side for ${id}`);
  if (copy !== undefined && (typeof copy !== 'string' || !copy.trim())) {
    throw new Error(`Provide nonempty message text for ${id}`);
  }
  if (copy === undefined && !attachment) throw new Error(`Provide text or an attachment for ${id}`);
  const outgoing = side === 'outgoing';
  const arrivalFrame = frameOf(message.at ?? 0);
  const arrival = arrivalFrame / fps;
  const fill = outgoing ? BLUE : GRAY;
  const mediaWidth = screenWidth - 2 * GUTTER;
  const maxWidth = Math.min(mediaWidth, Math.floor(screenWidth * .78));
  const left = width => outgoing ? screenWidth - GUTTER - width : GUTTER;
  const layouts = [];
  const parts = [];
  let bubble, body, tail, label, media;

  if (copy !== undefined) {
    const layout = textLayout(copy, maxWidth, style, measure);
    layouts.push({frame: arrivalFrame, ...layout});
    body = rect(id + '-body', 0, 0, layout.width, layout.height, fill, 15);
    tail = vector(id + '-tail', tailPath(layout.width, layout.height, outgoing), fill);
    label = text(id + '-copy', layout.text, TYPE_PAD_X, TYPE_PAD_Y, style.fontSize,
      {...style, lineHeight: layout.lineHeight, fill: outgoing ? '#ffffff' : INK});
    bubble = group(id + '-bubble', left(layout.width), 0, [tail, body, label]);
    parts.push(bubble);
  }
  if (edit) {
    if (!bubble || typeof edit.text !== 'string' || !edit.text.trim()) throw new Error(`Invalid edit for ${id}`);
    const frame = frameOf(edit.at);
    if (frame <= arrivalFrame) throw new Error(`Edit must follow its message for ${id}`);
    const layout = textLayout(edit.text, maxWidth, style, measure);
    layouts.push({frame, ...layout});
    const at = frame / fps;
    setAt(bubble, 'x', at, left(layout.width));
    setAt(body, 'width', at, layout.width);
    setAt(body, 'height', at, layout.height);
    setAt(tail, 'd', at, tailPath(layout.width, layout.height, outgoing));
    setAt(label, 'text', at, layout.text);
  }
  if (attachment) {
    const build = Object.hasOwn(mediaBuilders, attachment.kind) ? mediaBuilders[attachment.kind] : null;
    if (!build) throw new Error(`Unknown attachment kind for ${id}`);
    const width = attachment.width ?? Math.min(224, mediaWidth);
    if (width > mediaWidth) throw new Error(`Attachment width exceeds the screen for ${id}`);
    const swipes = attachment.swipes?.map(swipe => {
      const frame = frameOf(swipe.at);
      if (frame < arrivalFrame) throw new Error(`Swipe starts before attachment ${id}`);
      return {...swipe, at: frame / fps};
    });
    media = build({...attachment, id: id + '-attachment', x: left(width), width,
      y: layouts.length ? layouts[0].height + 5 : 0, swipes, fontFamily: style.fontFamily});
    if (layouts.length > 1) setAt(media, 'y', layouts[1].frame / fps, layouts[1].height + 5);
    parts.push(media);
  }
  let tapbackFrame;
  if (reaction) {
    const value = reaction.type;
    if (typeof value !== 'string' || !value.trim() || (value !== 'heart' && graphemes(value).length !== 1)) {
      throw new Error(`Use heart or one grapheme for the reaction on ${id}`);
    }
    tapbackFrame = frameOf(reaction.at);
    if (tapbackFrame < arrivalFrame) throw new Error(`Reaction starts before ${id}`);
    const anchor = width => left(width) + width - 14;
    const reactionLayer = tapback(id + '-tapback', value,
      anchor(layouts[0]?.width ?? media.width), tapbackFrame / fps, style.fontFamily);
    if (layouts.length > 1) setAt(reactionLayer, 'x', layouts[1].frame / fps, anchor(layouts[1].width));
    parts.push(reactionLayer);
  }

  const layer = group(id, 0, 0, parts, {start: arrival});
  if (arrival) layer.keyframes = {opacity: [key(arrival, .48), key(arrival + .14, 1, 'easeOut')]};
  const heightAt = frame => {
    const layout = layouts.length > 1 && frame >= layouts[1].frame ? layouts[1] : layouts[0];
    return (layout?.height ?? 0) + (media?.height ?? 0) + (layout && media ? 5 : 0);
  };
  return {message, layer, arrivalFrame, editFrame: layouts[1]?.frame, tapbackFrame, heightAt};
}

function projectTranscript(rows, viewportHeight, track, frameCount, fps) {
  const changedFrames = new Set(rows.flatMap(row => [row.arrivalFrame, row.editFrame]));
  const scrollLayer = group(track.id, 0, 0, rows.map(row => row.layer));
  let target = 0;
  let base = 0;
  let settle = [key(0, 0)];
  for (let frame = 0; frame < frameCount; frame++) {
    const time = frame / fps;
    const offset = track.offsetAt(time);
    base = sampleTrack(settle, time);
    if (frame === 0 || changedFrames.has(frame)) {
      let cursor = PAD_TOP;
      for (const row of rows) {
        if (row.arrivalFrame > frame) break;
        setAt(row.layer, 'y', time, cursor);
        cursor += row.heightAt(frame) + ROW_GAP;
      }
      const next = Math.min(0, viewportHeight - cursor - PAD_BOTTOM + ROW_GAP);
      if (frame === 0) base = next;
      if (next !== target) {
        // Show part of the arriving row immediately, then settle the transcript.
        if (next < base && offset === 0) base = Math.max(next, base - 19);
        settle = [key(time, base), key(time + .27, next, 'easeOut')];
        target = next;
      }
    }
    const y = Math.min(0, base + offset);
    setAt(scrollLayer, 'y', time, Math.round(y * 1000) / 1000 || 0);
  }
  return scrollLayer;
}

function scrollSampler(commands, frameOf, fps) {
  let end = 0;
  let from = 0;
  const moves = commands.map(({at, offset, duration = .42}) => {
    const start = frameOf(at) / fps;
    if (!Number.isFinite(offset) || offset < 0 || !Number.isFinite(duration) || duration < 0 || start < end) {
      throw new Error('Scroll windows must be ordered and non-overlapping. Use a nonnegative offset and duration.');
    }
    end = start + duration;
    const move = {start, end, from, to: offset};
    from = offset;
    return move;
  });
  return time => {
    let offset = 0;
    for (const move of moves) {
      if (time < move.start) break;
      if (time < move.end) {
        const progress = easeValue((time - move.start) / (move.end - move.start), 'easeInOut');
        return move.from + (move.to - move.from) * progress;
      }
      offset = move.to;
    }
    return offset;
  };
}

function makeComposer(id, width, y, rows, {style, measure, frameOf, fps}, events) {
  const fieldX = 47;
  const fieldWidth = width - fieldX - 13;
  const fieldBottom = 53;
  const shortHeight = 32;
  const tallHeight = 50;
  const draftStyle = {...style, fontSize: 14, lineHeight: 17, fill: INK};
  const input = text(id + '-input', '', 12, 7, draftStyle.fontSize, draftStyle);
  const placeholder = text(id + '-placeholder', 'iMessage', 12, 7, draftStyle.fontSize,
    {...draftStyle, fill: '#737782', opacity: 1});
  const field = rect(id + '-field', 0, 0, fieldWidth, shortHeight, '#ffffff', 16,
    {stroke: '#d8dbe3', strokeWidth: 1});
  const active = group(id + '-active', fieldWidth - 29, 4, [
    oval(id + '-send', 0, 0, 24, BLUE),
    vector(id + '-send-arrow', 'M 12 18 V 6.8 M 7 11.5 L 12 6.5 L 17 11.5', 'none', '#ffffff', 1.7),
  ], {opacity: 0});
  const idle = group(id + '-idle', fieldWidth - 25, 8, [
    vector(id + '-wave', 'M 0 7 V 11 M 3.8 4 V 14 M 7.6 1 V 17 M 11.4 4 V 14 M 15.2 7 V 11', 'none', '#868b95', 1.3),
  ], {opacity: 1});
  const fieldGroup = group(id + '-field-group', fieldX, fieldBottom - shortHeight,
    [field, input, placeholder, idle, active]);
  const sizeField = (at, height) => {
    setAt(fieldGroup, 'y', at, fieldBottom - height);
    setAt(field, 'height', at, height);
    setAt(active, 'y', at, height - 28);
  };
  let lastSend = -1;
  for (const {message, arrivalFrame} of rows) {
    if (message.typingFrom === undefined) {
      if (message.side === 'outgoing' && arrivalFrame > 0) lastSend = arrivalFrame;
      continue;
    }
    const firstFrame = frameOf(message.typingFrom);
    if (message.side !== 'outgoing' || !message.text || firstFrame >= arrivalFrame || firstFrame <= lastSend) {
      throw new Error(`Typing window must precede send without overlapping another draft for ${message.id}`);
    }
    const chars = graphemes(message.text);
    const writtenAt = index => firstFrame + Math.floor((arrivalFrame - firstFrame) * index / chars.length);
    let written = '';
    let previousDraft = '';
    for (let count = 0; count < chars.length;) {
      const frame = writtenAt(count);
      const first = count;
      while (count < chars.length && writtenAt(count) === frame) written += chars[count++];
      const t = frame / fps;
      const lines = wrapText(written, fieldWidth - 49, measure, draftStyle).slice(-2);
      const draft = lines.join('\n');
      setAt(input, 'text', t, draft);
      sizeField(t, lines.length > 1 ? tallHeight : shortHeight);
      if (previousDraft === draft) continue;
      events.push({frame, time: t, kind: 'typing', target: input.id, observed_character_delta: count - first});
      previousDraft = draft;
    }
    const first = firstFrame / fps;
    const send = arrivalFrame / fps;
    setAt(placeholder, 'opacity', first, 0);
    setAt(placeholder, 'opacity', send, 1);
    setAt(input, 'text', send, '');
    sizeField(send, shortHeight);
    setAt(active, 'opacity', first, 1);
    setAt(active, 'opacity', send, 0);
    setAt(idle, 'opacity', first, 0);
    setAt(idle, 'opacity', send, 1);
    lastSend = arrivalFrame;
  }
  return group(id, 0, y, [
    rect(id + '-bar', 0, 0, width, FOOTER, '#ffffff'),
    oval(id + '-plus-background', 13, fieldBottom - 29, 27, '#eef0f4'),
    vector(id + '-plus', 'M 26.5 31.5 V 43.5 M 20.5 37.5 H 32.5', 'none', '#626773', 1.5),
    fieldGroup,
    rect(id + '-home-indicator', width / 2 - 35, FOOTER - 7, 70, 3, '#30313a', 2),
  ]);
}

function makeHeader(id, width, participant, style, measure) {
  const x = width / 2 - 17;
  const nameStyle = {...style, fontSize: 13, fontWeight: 650};
  const name = wrapText(participant.name, width - 82, measure, nameStyle).join('\n');
  if (name.includes('\n')) throw new Error('Participant name does not fit the header');
  const person = participant.avatar
    ? group(id + '-avatar', x, 9, [{
      id: id + '-portrait', type: 'image', src: participant.avatar,
      width: 34, height: 34, preserveAspectRatio: 'xMidYMid slice',
    }], {clip: clip(34, 34, 17)})
    : Avatar({id: id + '-avatar', x, y: 9, size: 34, fill: '#d7e4f4',
      initials: participant.initials ?? participant.name.split(/\s+/u).slice(0, 2).map(word => graphemes(word)[0]).join('')});
  return group(id, 0, 0, [
    rect(id + '-surface', 0, 0, width, HEADER, '#f8f9fb'),
    vector(id + '-back', 'M 23 26 L 15 34 L 23 42', 'none', BLUE, 2.4),
    person,
    text(id + '-name', name, width / 2, 47, nameStyle.fontSize,
      {...nameStyle, textAnchor: 'middle', fill: INK}),
    rect(id + '-divider', 0, HEADER - 1, width, 1, '#e2e4eb'),
  ]);
}

function validateLayerIds(layers) {
  const seen = new Set();
  function walk(layer) {
    if (seen.has(layer.id)) throw new Error(`Duplicate scene layer id ${layer.id}`);
    seen.add(layer.id);
    layer.children?.forEach(walk);
  }
  layers.forEach(walk);
}

/** Compose editable layers and derive the composer, thread and cue states from one timeline. */
export function buildConversation({
  id = 'conversation', width = 960, height = 540, fps = 30, duration = 6,
  background = '#eceef2', phone = {}, participant, messages, scroll = [], camera = {},
  measureText, fontFamily = DEFAULT_STYLE.fontFamily, fonts,
} = {}) {
  if (!Number.isInteger(width) || !Number.isInteger(height) || width <= 0 || height <= 0 ||
      !Number.isFinite(fps) || fps < 1 || !Number.isFinite(duration) || Math.round(duration * fps) < 1) {
    throw new Error('Provide positive scene dimensions, fps and duration');
  }
  if (typeof measureText !== 'function') throw new Error('Provide a text measurer that shares the exporter font');
  const measure = (value, style) => {
    const pixels = measureText(value, style);
    if (!Number.isFinite(pixels) || pixels < 0) throw new Error('measureText must return a finite width in pixels');
    return pixels;
  };
  if (typeof participant?.name !== 'string' || !participant.name.trim() ||
      (participant.avatar !== undefined && (typeof participant.avatar !== 'string' || !participant.avatar.trim()))) {
    throw new Error('Provide a participant name and an optional image src');
  }
  if (!Array.isArray(messages)) throw new Error('Provide an array of messages');

  const frameCount = Math.round(duration * fps);
  const frameOf = time => {
    const frame = Math.ceil(time * fps - 1e-8);
    if (!Number.isFinite(time) || time < 0 || frame >= frameCount) {
      throw new Error(`Event falls outside the output timeline: ${time}`);
    }
    return frame || 0;
  };
  const phoneWidth = phone.width ?? 278;
  const phoneHeight = phone.height ?? 500;
  if (!Number.isFinite(phoneWidth) || phoneWidth < 180 || !Number.isFinite(phoneHeight) || phoneHeight < 200) {
    throw new Error('Phone viewport needs at least 180 × 200 design pixels');
  }
  const screenWidth = phoneWidth - 4;
  const screenHeight = phoneHeight - 4;
  const viewportHeight = screenHeight - HEADER - FOOTER;
  const style = {...DEFAULT_STYLE, fontFamily};
  const contexts = {screenWidth, style, measure, frameOf, fps};
  const rows = messages.map(message => prepareRow(message, contexts)).sort((a, b) => a.arrivalFrame - b.arrivalFrame);
  const scrollLayer = projectTranscript(rows, viewportHeight, {
    id: id + '-scroll', offsetAt: scrollSampler(scroll, frameOf, fps),
  }, frameCount, fps);

  const events = [];
  const mark = (frame, kind, target) => {
    if (frame !== undefined) events.push({frame, time: frame / fps, kind, target});
  };
  for (const row of rows) {
    if (row.arrivalFrame) mark(row.arrivalFrame, row.message.side === 'outgoing' ? 'message_send' : 'message_arrival', row.layer.id);
    mark(row.tapbackFrame, 'tapback', row.layer.id + '-tapback');
    mark(row.editFrame, 'message_edit', row.layer.id);
  }
  const phoneLayer = group(id + '-phone', phone.x ?? (width - phoneWidth) / 2,
    phone.y ?? (height - phoneHeight) / 2, [
      rect(id + '-case', 0, 0, phoneWidth, phoneHeight, '#30323a', 32),
      group(id + '-screen', 2, 2, [
        rect(id + '-screen-background', 0, 0, screenWidth, screenHeight, '#ffffff', 30),
        group(id + '-viewport', 0, HEADER, [scrollLayer], {clip: clip(screenWidth, viewportHeight)}),
        makeHeader(id + '-header', screenWidth, {...participant, name: participant.name.trim()}, style, measure),
        makeComposer(id + '-composer', screenWidth, HEADER + viewportHeight, rows, contexts, events),
      ], {clip: clip(screenWidth, screenHeight, 30)}),
    ]);
  const layers = [CameraRig({
    originX: width / 2, originY: height / 2, ...camera, id: id + '-camera', children: [phoneLayer],
  })];
  validateLayerIds(layers);
  const scene = {
    width, height, fps, duration: frameCount / fps, background, title: participant.name,
    source: {notes: 'Authored conversation timing. The phone and media poses are editable illustrative geometry.'},
    layers,
  };
  if (fonts) scene.fonts = fonts;
  events.sort((a, b) => a.frame - b.frame);
  return {scene, events};
}
