/** Portable editorial recipes added after a fresh content-reuse trial. */

const SOURCE = 'skill/imessage-motion-recreation/motion/packs/attention.mjs';
const source = note => ({kind: 'authored', ref: SOURCE, range: [0, 2.4], note});
const smooth = p => {
  const x = Math.max(0, Math.min(1, p));
  return x * x * (3 - 2 * x);
};
const at = (frame, total) => frame / total;
const format = new Intl.NumberFormat('en-US', {maximumFractionDigits: 0});

function changingValues(values) {
  const [start, end] = values;
  if (values.length !== 2 || !values.every(n => Number.isSafeInteger(n) && Math.abs(n) <= 1e9) || start === end) {
    throw new Error('Metric count needs two different whole-number endpoints from −1,000,000,000 to 1,000,000,000');
  }
  return [start, end];
}

function metric(ctx) {
  const [start, end] = changingValues(ctx.content.values);
  const {frameCount} = ctx;
  const panel = ctx.rect('metric-panel', 63, 38, 374, 211, '#f5f8f6', 22, {stroke: '#cbded6', strokeWidth: 1});
  const name = ctx.text('metric-label', ctx.content.copy, 99, 74, 18, {fill: '#35524a', fontWeight: 600});
  const points = [];
  let previous;
  for (let n = 0; n < frameCount; n++) {
    const progress = n / (frameCount - 1);
    const next = Math.round(start + (end - start) * smooth((progress - .13) / .65));
    if (next !== previous) {
      points.push([n, format.format(next)]);
      previous = next;
    }
  }
  const length = Math.max(format.format(start).length, format.format(end).length);
  const fontSize = Math.min(64, Math.floor(390 / length));
  const digits = ctx.text('metric-value', points[0][1], 98, 103, fontSize, {fill: '#11694e', fontWeight: 700});
  digits.keyframes = {text: points.map(([frame, value]) => ({
    t: frame / ctx.fps, value, ease: 'hold',
  }))};
  const unit = ctx.text('metric-unit', ctx.content.detail, 100, 195, 15, {fill: '#35524a'});
  ctx.stage.children.push(panel, name, digits, unit);
  ctx.event('count-begins', at(points[1][0], frameCount), digits.id, 'metric.count.begin');
  ctx.event('final-value-held', at(points.at(-1)[0], frameCount), digits.id, 'metric.count.hold');
}

function decodeText(ctx) {
  const alphabet = Array.from('ACDEFHKMNPRSTUVWY234578');
  const segmenter = new Intl.Segmenter(undefined, {granularity: 'grapheme'});
  const chars = Array.from(segmenter.segment(ctx.content.title), part => part.segment);
  if (!ctx.content.title.trim() || chars.length > 24) throw new Error('Use a phrase of 1–24 graphemes');
  const surface = ctx.rect('decode-panel', 28, 66, 444, 152, '#152744', 16);
  const spacing = Math.min(35, 398 / chars.length);
  const onset = Math.ceil(ctx.frameCount * .15);
  const readable = Math.ceil(ctx.frameCount * .63);
  const slots = chars.map((character, index) => {
    const x = (index - (chars.length - 1) / 2) * spacing;
    const glyph = ctx.text('decoded-glyph-' + index, '', x, 0, Math.min(37, Math.floor(spacing * 1.2)),
      {textAnchor: 'middle', fill: '#eff3fc', fontWeight: 700});
    const poses = [[0, '', 'hold']];
    for (let frame = onset; frame < readable; frame += 3) {
      const count = Math.floor(chars.length * (frame - onset) / (readable - onset));
      const code = (frame * 11 + index * 13) % alphabet.length;
      const unresolved = alphabet[code] === character ? alphabet[(code + 1) % alphabet.length] : alphabet[code];
      const value = index < count || /\s/.test(character) ? character : unresolved;
      poses.push([at(frame, ctx.frameCount), value, 'hold']);
    }
    poses.push([at(readable, ctx.frameCount), character, 'hold']);
    ctx.track(glyph, 'text', poses);
    return glyph;
  });
  const text = ctx.group('decoded-title', 250, 117, slots);
  ctx.stage.children.push(surface, text);
  ctx.event('scramble-start', at(onset, ctx.frameCount), text.id, 'label.decode.begin');
  ctx.event('title-readable', at(readable, ctx.frameCount), text.id, 'label.decode.readable');
  ctx.label(ctx.content.detail);
}

function gutter(ctx) {
  if (!ctx.content.title.trim() || ctx.content.title.length > 28)
    throw new Error('Use a center label of 1–28 characters to fit the gutter');
  const backdrop = ctx.rect('gutter-backdrop', 24, 36, 452, 208, '#e2ecec', 15);
  const text = ctx.text('gutter-label', ctx.content.title, 250, 130, Math.min(18, Math.floor(235 / Math.max(1, ctx.content.title.length))),
    {fill: '#20443e', textAnchor: 'middle', fontWeight: 700, opacity: 0});
  ctx.track(text, 'opacity', [[0, 0], [.43, 0], [.72, 1, 'easeOut']]);
  const panels = [0, 1].map(i => {
    const x = 24 + i * 226;
    const id = i ? 'right-panel' : 'left-panel';
    const group = ctx.group(id, x, 36, [ctx.image(id + '-photo', 0, 0, 226, 208,
      {photo: i, preserveAspectRatio: 'xMidYMid slice'})], {clip: {x: 0, y: 0, width: 226, height: 208, radius: 13}});
    ctx.track(group, 'x', [[0, x], [.21, x], [.73, x + (i ? 78 : -78), 'easeInOut']]);
    return group;
  });
  ctx.stage.children.push(backdrop, text, ...panels);
  ctx.event('split-begins', .22, panels[0].id, 'panel.gutter.open');
  ctx.event('center-readable', .73, text.id, 'panel.gutter.settle');
  ctx.label(ctx.content.detail);
}

function fan(ctx) {
  const midpoint = 250;
  const pinY = 225;
  const covers = [
    {id:'leaf-left', color:'#c46b68', to:-29}, {id:'leaf-right', color:'#597eaa', to:29},
    {id:'leaf-center', color:'#d8b36b', to:0},
  ];
  for (const [i, leaf] of covers.entries()) {
    const body = ctx.rect(leaf.id + '-surface', 0, 0, 100, 163, leaf.color, 12);
    const art = ctx.group(leaf.id + '-art-window', 8, 8,
      [ctx.image(leaf.id + '-art', 0, 0, 84, 106, {photo: i, preserveAspectRatio:'xMidYMid slice'})],
      {clip: {x:0, y:0, width:84, height:106, radius:8}});
    const group = ctx.group(leaf.id, midpoint - 50, pinY - 143, [body, art], {originX: 50, originY: 143});
    if (leaf.to) ctx.track(group, 'rotation', [[0, 0], [.20, 0], [.64, leaf.to, 'easeInOut']]);
    ctx.stage.children.push(group);
  }
  ctx.stage.children.push(ctx.rect('fan-pin', midpoint - 5, pinY - 5, 10, 10, '#f6e9d6', 5));
  ctx.event('leaves-open', .21, 'leaf-left', 'swatches.open');
  ctx.event('fan-settled', .64, 'fan-pin', 'swatches.settle');
  ctx.label(ctx.content.detail);
}

export const entries = [
  {
    id: 'metric-count',
    title: 'Count between totals in place',
    moves: 'Only the numeric value steps through intermediate whole numbers, then the final value holds.',
    fixed: 'The heading, metric label, optional unit and field stay in place.',
    notice: 'Readable growth or reduction on one comparable measure while the label retains its meaning.',
    fits: 'Count one metric up or down between known endpoints without scrolling its digits.',
    avoid: 'An odometer needs rolling glyphs. Use a still when only a final value is supported.',
    intents: ['Count a single number up in place and hold the total', 'Make the number tick up with the label fixed', 'Count down to a final number with fixed title'],
    editable: ['heading','copy','detail','values'],
    example: 'motion/examples/metric-hold.json',
    defaults: {heading:'A growing delivery total', copy:'Completed trips', detail:'trips this week', values:[620,1280]},
    source: source('Adapted from a fresh, Pillow-authored volunteer count reuse. The editable canonical recipe preserves the value trajectory and event timing.'),
    build: metric,
  },
  {
    id: 'text-scramble-resolve',
    title: 'Resolve shifting glyphs to one fixed title',
    moves: 'Unsettled character slots change while their positions stay fixed, then resolve into a readable title left to right.',
    fixed: 'The title field, heading and camera hold steady.',
    notice: 'A title changes from unreadable to definite without moving the reading position.',
    fits: 'A short decode, establishment or reveal where delayed legibility is intentional.',
    avoid: 'Keep accessibility-critical or instructional text readable from its first frame.',
    intents: ['Scramble the title glyphs and resolve into a legible word', 'Reveal a code by decoding changing characters in place'],
    editable: ['heading','title','detail'],
    defaults: {heading:'Signal received', title:'CLEAR TO OPEN', detail:'Read the final title'},
    source: source('Authored from the editorial motion pack’s deterministic glyph progression.'),
    build: decodeText,
  },
  {
    id: 'center-gutter-open',
    title: 'Part two images to reveal the center',
    moves: 'Two separate picture planes slide outward in opposite directions and open a gutter for a label.',
    fixed: 'The original frame and revealed text stay centered.',
    notice: 'Two distinct views make room for a shared conclusion between them.',
    fits: 'The pair and the central conclusion should remain simultaneously visible.',
    avoid: 'A wipe replaces one field with another. Use that for an in-place before/after comparison.',
    intents: ['Part two panels outward like curtains to reveal a label in the gap', 'Open a center gutter between photos'],
    editable: ['heading','title','detail','photos'],
    photoCount: {min:2,max:2},
    defaults: {heading:'Two routes', title:'Same destination', detail:'Two views stay visible'},
    source: source('Authored from the editorial pack’s split-plane reveal.'),
    build: gutter,
  },
  {
    id: 'hinged-swatch-fan',
    title: 'Fan and hold swatches around a shared pin',
    moves: 'The outer leaves rotate in opposite directions around a common pin and stop in a standing fan.',
    fixed: 'The center leaf, visible pivot, heading and camera are fixed.',
    notice: 'The surfaces are variants of the same collection and share a single attachment point.',
    fits: 'Reveal three material or visual samples simultaneously around an anchored pivot.',
    avoid: 'A stack swipe removes a top item. Use it when only one item should be active at a time.',
    intents: ['Fan swatches outward around a pin','Rotate outer cards around one shared pivot and keep the middle still'],
    editable: ['heading','detail','photos'],
    photoCount: {min:3,max:3},
    defaults: {heading:'Finish options', detail:'Three swatches, one collection'},
    source: source('Authored from the composition pack’s pinned fan of three individually editable cards.'),
    build: fan,
  },
];
