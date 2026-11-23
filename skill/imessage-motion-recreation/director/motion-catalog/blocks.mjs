import fs from 'node:fs';
import {ActionButton, AppCard, AppIcon, Avatar, Composer, MessageBubble, PhoneFrame, TOKENS, group, rect, text} from '../components.mjs';
import {getMotion} from './registry.mjs';

const designRate = 30;
const sizes = {
  'daniel-typing-to-reply': [640, 360],
  'poke-choice-to-outgoing': [640, 460],
  'mini-anchored-rich-card': [640, 460],
  'linq-conversation-to-app': [640, 460]
};
const neutralBlue = '#256795';
const railId = 'linq-restaurant-photo-strip';

function imageTile(id, src, x, width, height, radius) {
  const image = {id: id + '-image', type: 'image', src, width, height, preserveAspectRatio: 'xMidYMid slice'};
  return group(id, x, 0, [image], {clip: {x: 0, y: 0, width, height, radius}});
}

function builtInAsset(relativePath) {
  const url = new URL(relativePath, import.meta.url);
  return url.protocol === 'file:' ? decodeURIComponent(url.pathname) : url.href;
}

// Sparse checkouts do not carry projects/*/scenes payloads. Fall back to the
// catalog-local crops re-derived from decoded native frames (see
// handoffs/motion-catalog-previews/assets/README.md for their derivation and
// which edges are approximations).
function slotAsset(entry, slot) {
  const canonical = builtInAsset(slot.asset);
  if (fs.existsSync(canonical)) return canonical;
  const local = builtInAsset(`../../../../handoffs/motion-catalog-previews/assets/${entry.id}/${slot.actor}.png`);
  if (fs.existsSync(local)) return local;
  return canonical;
}

function photoStrip(entry, options, time) {
  const {variant, context, images, title, color, action} = options;
  const {slots, viewport, railDxPx} = entry.measurement;
  const {x, y, width, height} = viewport;
  if (images !== undefined && (!Array.isArray(images) || images.length !== slots.length ||
      images.some(src => typeof src !== 'string' || !src.trim()))) {
    throw Error('Supply five image paths, one per measured slot');
  }

  const tiles = slots.map((slot, index) => imageTile(
    slot.actor, images?.[index] ?? slotAsset(entry, slot), slot.x, slot.width, height, 17
  ));
  const offsets = variant === 'controls' ? railDxPx : railDxPx.slice(1, -1);
  const rail = group('rail', 0, 0, tiles, {
    keyframes: {x: offsets.map((value, index) => ({t: time(index), value, ease: 'linear'}))}
  });
  const stage = group('viewport', 0, 0, [rect('rail-matte', 0, 0, width, height, '#fafafa'), rail],
    {clip: {x: 0, y: 0, width, height}});
  if (context === 'isolated') return {width, height, layers: [stage]};

  if (context === 'restaurant') {
    stage.x = x;
    stage.y = y;
    return {width: 960, height: 720, background: '#fafafa', layers: [
      text('venue', title ?? 'Boqueria Soho', x, 21, 32, {fontWeight: 600}),
      text('details', 'Open now  ·  Spanish restaurant', x, 74, 20, {fill: '#4a5a62'}),
      ActionButton({id: 'directions', x, y: 125, width: 308, height: 47, copy: action ?? 'Directions', fill: color}),
      text('tabs', 'Overview        Menu        Reviews', x, 240, 21),
      rect('divider', x, 282, width, 1, '#d8dbe0'),
      stage,
      text('address', options.copy ?? '171 Spring Street, New York', x, 681, 22)
    ]};
  }

  // The film can use its own conversation UI; this wrapper demonstrates the mount.
  const reducedStrip = group('mini-app', 58, 178, [stage], {scaleX: .71, scaleY: .71});
  return {width: 960, height: 540, layers: [
    PhoneFrame({id: 'thread', x: 215, y: 15, width: 530, height: 510, title: 'Concierge',
      children: [
        MessageBubble({id: 'request', x: 158, y: 77, width: 336, height: 48,
          copy: options.copy ?? 'What does the restaurant look like?', tail: false, fill: color, fontSize: 15}),
        text('venue', title ?? 'Juniper Dining Room', 58, 138, 22, {fontWeight: 600}),
        reducedStrip,
        ActionButton({id: 'directions', x: 58, y: 427, width: 160, copy: action ?? 'Directions', fill: color})
      ]})
  ]};
}

function typingReply(options, time) {
  const {copy = 'Sure, I’ll bring in a few friends.', title = 'Muse', color} = options;
  const track = (...samples) => samples.map(([frame, value]) => ({t: time(frame), value, ease: 'linear'}));
  const width = Math.min(384, Math.max(132, Array.from(copy).length * 8.4 + 30));
  const widening = track([0, 42], [10, 72], [24, 72], [25, width*.55], [26, width*.79], [28, width], [30, width + 4], [32, width]);
  const bubble = rect('incoming-body', 0, 0, 72, 42, '#e7eaec', 19, {keyframes: {width: widening}});
  const tail = {id: 'incoming-tail', type: 'path', d: 'M 6 27 Q 7 36 0 43 Q 15 42 20 33 Z', fill: '#e7eaec'};
  const dots = [0, 1, 2].map(index => ({
    id: 'dot-' + index, type: 'circle', width: 7, height: 7, x: 15 + index * 16, y: 17, fill: '#67727b',
    keyframes: {opacity: track([7, .25], [11+3*index, .95], [17+index, .3], [19+index, .75], [25, .32], [26, 0])}
  }));
  const chars = Array.from(copy);
  const partial = fraction => chars.slice(0, Math.round(chars.length*fraction)).join('');
  const line = group('reply-reveal', 0, 0, [text('reply-copy', copy, 14, 10, 16, {
    keyframes: {
      text: track([25, partial(.37)], [26, partial(.72)], [28, copy]),
      opacity: track([25, .3], [26, .8], [28, 1]),
      blur: track([25, 4], [28, 0])
    }
  })], {start: time(25),clip:{x:0,y:0,width,height:42}});
  const incoming = group('incoming', 26, 176, [tail, bubble, ...dots, line], {
    keyframes: {opacity: track([0, .07], [5, .58], [10, 1]), blur: track([0, 7], [5, 2], [10, 0])}
  });
  return [PhoneFrame({id:'thread', x: 96, y: 16, width:448, height:328, title, children: [
    MessageBubble({id:'request', x: 129, y: 91, width: 285, height: 55, copy: options.request ?? 'Can you help with the team offsite?', fill: color, fontSize: 15}),
    incoming
  ]})];
}

function choiceToOutgoing(options, time) {
  const labels = options.labels ?? ['Mexican','Japanese','Italian','Indian','Chinese','Surprise me'];
  const selected = options.selected ?? 3;
  if (!Array.isArray(labels) || labels.length !== 6 || !labels.every(label => typeof label === 'string') ||
      !Number.isInteger(selected) || selected < 0 || selected >= labels.length) throw Error('Provide six labels and a selected row index from 0 to 5');
  const keys = (...samples) => samples.map(([frame, value]) => ({t: time(frame), value, ease:'linear'}));
  const list = group('options', 30, 139, [
    rect('list-body', 0, 0, 193, 202, '#e8eaec', 19),
    ...labels.map((label,index) => text('choice-' + index, label, 17, 14 + index * 29, 17,
      {fill: options.color, keyframes: index === selected ? {opacity: keys([8,1],[9,.88],[17,.31],[30,1])} : {}}))
  ], {end: time(31), keyframes:{scaleX: keys([21,1],[30,.82]), scaleY:keys([21,1],[30,.82])}});
  const result = MessageBubble({id:'result',x:166,y:153,width:250,height:58,copy:labels[selected]+'\nSelected option',
    fontSize:15,fill:'#e7eaee',side:'incoming',tail:false});
  result.start = time(31);
  result.keyframes = {x: keys([31,220],[35,184],[45,166]), y: keys([31,164],[35,152],[45,149])};
  const followUp = MessageBubble({id:'follow-up',x:27,y:290,width:255,height:47,copy:options.copy ?? 'Want me to find a spot?', side:'incoming',fontSize:15});
  followUp.start = time(45);
  followUp.opacity = .35;
  return [PhoneFrame({id:'thread', x:90, y:10, width:460, height:440,title:options.title ?? 'Dinner',children:[
    text('prompt', options.request ?? 'What are you in the mood for?', 29, 92, 19,{end:time(31)}), list,
    text('task-label', '✓  Dinner choice', 30, 97, 15,{start:time(31),fill:'#52616c'}),result,followUp,
    Composer({id:'composer',x:27,y:370,width:406,active:false})
  ]})];
}

function anchoredCard(options, time) {
  const keys = (...samples) => samples.map(([frame, value]) => ({t: time(frame), value, ease:'linear'}));
  const scale = keys([0,.15],[2,.55],[5,.98],[9,1.035],[20,1]);
  const card = AppCard({id:'card', x:35,y:170,width:318,height:203,title:options.title ?? 'Team lunch',
    detail:options.copy ?? 'Three places the team can try',action:options.action ?? 'View menu',color:'#cddfd6'});
  if (options.image) card.children[1] = group('art', 12, 12,
    [imageTile('card-photo', options.image, 0, 294, 73, 14)]);
  card.keyframes = {opacity: keys([0,.18],[4,1]), scaleX:scale,scaleY:scale};
  card.originX = 9;
  card.originY = 11;
  card.children.push(rect('card-press',0,0,318,203,'#07151e',22,
    {keyframes:{opacity:keys([58,0],[59,.13],[62,.22],[63,.17],[68,0])}}));
  const stream = group('message-stack',0,0,[
    MessageBubble({id:'request',x:147,y:87,width:276,height:55,copy:options.request ?? 'Find a place for us to eat.',fill:options.color,fontSize:16}),card
  ],{keyframes:{y:keys([0,20],[20,14],[57,0])}});
  return [PhoneFrame({id:'thread',x:92,y:10,width:456,height:440,title:'Team chat',children:[
    stream, Composer({id:'composer',x:27,y:380,width:402,active:false})
  ]})];
}

function conversationToApp(options, time) {
  const keys = (...samples) => samples.map(([frame,value]) => ({t:time(frame),value,ease:'linear'}));
  const thread = PhoneFrame({id:'thread',x:90,y:10,width:460,height:440,title:'Travel plans',children:[
    MessageBubble({id:'reply',x:25,y:92,width:316,height:56,copy:options.request ?? 'I found a few options.',side:'incoming'}),
    AppCard({id:'preview-card',x:25,y:172,width:306,height:206,title:options.previewTitle ?? 'Your recommendation',
      detail:'Open for details',action:'Explore',color:'#ded9c5'})
  ]});
  thread.keyframes = {blur:keys([3,0],[5,.5],[9,5],[14,6])};
  const app = group('app-document',0,0,[
    rect('panel',0,0,364,472,options.color,24),
    rect('handle',158,13,48,5,'#dbe9ef',3),
    text('app-title',options.title ?? 'Trip details',182,34,23,{textAnchor:'middle',fill:'#ffffff',fontWeight:600}),
    AppCard({id:'ticket',x:22,y:88,width:320,height:246,title:options.copy ?? 'City weekend',
      detail:'Two seats available',action:options.action ?? 'Compare fares',color:'#dce9e8'})
  ],{keyframes:{opacity:keys([3,0],[4,.19],[7,.63],[8,1]),y:keys([4,142],[7,95],[11,60],[15,54])}});
  return [thread,group('app-viewport',138,8,[app],{clip:{x:0,y:0,width:364,height:435}})];
}

// --- Generic blocks shared by several catalog entries -----------------------
// Their geometry is authored; the sourceFrames interval they are anchored to
// is observed. They are not measured-pixel recreations.

function scrollList(options, time) {
  // Rows translate up inside a clipped viewport while the prompt, request,
  // header and composer stay fixed. Modeled on the Linq shared-check scroll
  // and the Poke result/capability lists (momentum-in, settle).
  const keys = (...samples) => samples.map(([frame, value]) => ({t: time(frame), value, ease: 'linear'}));
  const rows = options.rows ?? [
    {title: 'Jamie (you)', detail: 'Chick’n Shack + Lemonade', badge: '$16'},
    {title: 'Dillion', detail: 'Veggie Shack', badge: '$12'},
    {title: 'Priya', detail: 'is choosing…', badge: ''},
    {title: 'Carlos', detail: 'is choosing…', badge: ''},
    {title: 'Siobhan', detail: 'is choosing…', badge: ''},
    {title: 'Rene', detail: 'is choosing…', badge: ''}
  ];
  if (!Array.isArray(rows) || rows.length < 3 || rows.length > 8) throw Error('Provide three to eight scroll rows');
  const travel = options.travel ?? 158;
  const rail = group('list-rail', 0, 0, rows.map((row, index) => group('row-' + index, 0, index * 66, [
    Avatar({id: 'row-avatar-' + index, x: 0, y: 0, size: 40, initials: row.title.slice(0, 1).toUpperCase()}),
    text('row-title-' + index, row.title, 52, 2, 17, {fontWeight: 600}),
    text('row-detail-' + index, row.detail ?? '', 52, 27, 15, {fill: '#5d6a72'}),
    text('row-badge-' + index, row.badge ?? '', 330, 10, 17, {textAnchor: 'end', fontWeight: 600})
  ])), {keyframes: {y: keys([4, 0], [9, -26], [18, -travel * .62], [27, -travel * .92], [32, -travel])}});
  return {width: 640, height: 460, layers: [PhoneFrame({id: 'thread', x: 90, y: 10, width: 460, height: 440, title: options.title ?? 'Shared check', children: [
    text('header', options.header ?? 'Check’s Shared', 30, 62, 20, {fontWeight: 600}),
    group('list-viewport', 30, 104, [rail], {clip: {x: 0, y: 0, width: 400, height: 250}}),
    rect('footer-divider', 30, 360, 400, 1, TOKENS.line),
    text('footer', options.footer ?? 'Subtotal (3 orders)        $33', 30, 376, 16),
    Composer({id: 'composer', x: 27, y: 392, width: 406, active: false})
  ]})]};
}

function chipRail(options, time) {
  // A fixed card with a horizontally paged rail of selectable chips; one chip
  // wins the selection fill while the card chrome stays fixed (Poke time picker).
  const keys = (...samples) => samples.map(([frame, value]) => ({t: time(frame), value, ease: 'linear'}));
  const columns = options.columns ?? [
    {label: 'Thursday, June 4', chips: ['6:00 PM', '6:45 PM', '7:30 PM']},
    {label: 'Friday, June 5', chips: ['7:30 PM', '10:30 PM']},
    {label: 'Saturday, June 6', chips: ['8:00 PM', '9:15 PM']}
  ];
  const selected = options.selected ?? {column: 1, chip: 0};
  if (!Array.isArray(columns) || !columns.length) throw Error('Provide day columns with chips');
  const rail = group('chip-rail', 0, 0, columns.map((column, c) => group('day-' + c, c * 205, 0, [
    text('day-label-' + c, column.label, 0, 0, 15, {fill: '#5d6a72'}),
    ...column.chips.map((chip, i) => group('chip-' + c + '-' + i, i * 96, 30, [
      rect('chip-body-' + c + '-' + i, 0, 0, 86, 34, c === selected.column && i === selected.chip ? (options.color ?? neutralBlue) : '#ffffff', 17,
        c === selected.column && i === selected.chip ? {keyframes: {fill: keys([22, '#ffffff'], [26, options.color ?? neutralBlue])}} : {stroke: '#8a949d', strokeWidth: 1}),
      text('chip-copy-' + c + '-' + i, chip, 43, 8, 14, {textAnchor: 'middle',
        fill: c === selected.column && i === selected.chip ? '#ffffff' : '#1d5f9e'})
    ]))
  ])), {keyframes: {x: keys([8, 0], [16, -96], [30, -205])}});
  return {width: 640, height: 300, layers: [
    group('picker-card', 130, 40, [
      rect('card', 0, 0, 380, 220, '#f4f6f8', 22),
      text('card-title', options.title ?? 'Pick a Time', 24, 22, 21, {fontWeight: 600}),
      group('chip-viewport', 24, 66, [rail], {clip: {x: 0, y: 0, width: 332, height: 80}}),
      text('note', options.copy ?? '4 events scheduled this week.', 24, 168, 14, {fill: '#5d6a72'})
    ])
  ]};
}

function statCounter(options, time) {
  // Rolling count-up numerals over a dimming stack of message screenshots.
  const keys = (...samples) => samples.map(([frame, value]) => ({t: time(frame), value, ease: 'linear'}));
  const stats = options.stats ?? [
    {value: '10,000+', label: 'SMS'},
    {value: '100,000+', label: 'emails'},
    {value: '8,000+', label: 'voice minutes'}
  ];
  const stack = group('screenshot-stack', 0, 0, [0, 1, 2].map(i => group('shot-' + i, i * 24, i * 18, [
    rect('shot-body-' + i, 0, 0, 150, 84, '#eef0f3', 10, {stroke: TOKENS.line, strokeWidth: 1}),
    rect('shot-line-' + i + '-a', 12, 14, 96, 8, '#d3d7dc', 4),
    rect('shot-line-' + i + '-b', 12, 30, 122, 8, '#d3d7dc', 4),
    rect('shot-line-' + i + '-c', 12, 46, 74, 8, '#d3d7dc', 4)
  ], {keyframes: {opacity: keys([8 + i * 20, 0], [12 + i * 20, 1])}})));
  const digits = (final, t0) => ({text: [0, .28, .55, .8, 1].map((f, i) =>
    ({t: time(t0 + i * 2), value: i === 4 ? final : '…', ease: 'hold'}))});
  const counters = stats.map((s, i) => group('counter-' + i, 0, 0, [
    text('value-' + i, s.value, 0, 0, 64, {fontWeight: 700, fill: options.color ?? '#17191d',
      keyframes: digits(s.value, 10 + i * 20)}),
    text('label-' + i, s.label, 4, 78, 26, {fill: '#5d6a72'})
  ], {keyframes: {opacity: keys([10 + i * 20, 0], [14 + i * 20, 1], [46 + i * 20, 1], [52 + i * 20, i < stats.length - 1 ? 0 : 1])},
      y: keys([10 + i * 20, 16], [14 + i * 20, 0])}));
  return {width: 640, height: 360, layers: [
    group('wall', 60, 210, [stack]),
    group('counters', 250, 120, counters)
  ]};
}

function appDrawerGrid(options, time) {
  // The Messages app drawer rises as one sheet revealing an icon grid (games).
  const keys = (...samples) => samples.map(([frame, value]) => ({t: time(frame), value, ease: 'linear'}));
  const apps = options.apps ?? ['8 Ball', 'Chess', 'Four in a Row', 'Word Games', 'Crazy 8', 'Cup Pong'];
  const colors = options.appColors ?? ['#0d7a5f', '#c7a06a', '#b02a30', '#2b3f8c', '#c0392b', '#28577a'];
  if (apps.length !== colors.length) throw Error('apps and appColors must have equal length');
  const icons = apps.map((label, i) => AppIcon({id: 'app-' + i, x: 24 + (i % 3) * 128, y: 26 + Math.floor(i / 3) * 104, size: 62,
    color: colors[i], label: label.slice(0, 10)}));
  const sheet = group('drawer', 0, 0, [
    rect('sheet-body', 0, 0, 420, 260, '#ffffff', 26, {stroke: TOKENS.line, strokeWidth: 1}),
    text('sheet-title', options.title ?? 'Games', 20, 14, 18, {fontWeight: 600}),
    ...icons
  ], {keyframes: {y: keys([2, 300], [12, 60], [18, 40], [24, 44])}});
  return {width: 640, height: 400, layers: [PhoneFrame({id: 'thread', x: 100, y: 8, width: 440, height: 384, title: options.thread ?? 'iMessage', children: [
    Composer({id: 'composer', x: 22, y: 60, width: 396, copy: options.copy ?? 'Yo i’m bored, chess battle?'}),
    sheet
  ]})]};
}

function gridAssemble(options, time) {
  // Many small surfaces fly in from offstage and settle into a loose grid.
  // item='phone' models the Linq device montage; item='icon' models app walls.
  const keys = (...samples) => samples.map(([frame, value]) => ({t: time(frame), value, ease: 'linear'}));
  const kind = options.item ?? 'phone';
  const count = Math.min(9, Math.max(4, options.count ?? 6));
  const nodes = Array.from({length: count}, (_, i) => {
    const col = i % 3, row = Math.floor(i / 3);
    const x = 70 + col * 175, y = 26 + row * 168;
    const sx = x + (col - 1) * 420, sy = y + 340 + row * 60;
    const start = 2 + i * 3;
    const body = kind === 'icon'
      ? AppIcon({id: 'node-' + i, x, y, size: 66, color: ['#252a31', options.color ?? neutralBlue, '#6e9c74'][i % 3], label: String.fromCharCode(65 + i)})
      : group('node-' + i, x, y, [
          rect('device-' + i, 0, 0, 120, 150, '#101417', 22, {stroke: '#3a4249', strokeWidth: 2}),
          rect('screen-' + i, 8, 12, 104, 126, '#f2f4f6', 14),
          rect('line-a-' + i, 16, 26, 66, 7, '#c4ccd4', 3),
          rect('line-b-' + i, 16, 40, 84, 7, '#d8dee4', 3),
          rect('line-c-' + i, 16, 54, 52, 7, '#d8dee4', 3)
        ]);
    body.keyframes = {x: keys([start, sx], [start + 16, x, 'easeOut']),
      y: keys([start, sy], [start + 16, y, 'easeOut']),
      opacity: keys([start, 0], [start + 4, 1]),
      rotation: keys([start, (i - count / 2) * 7], [start + 16, 0])};
    return body;
  });
  return {width: 640, height: 400, layers: [
    text('claim', options.copy ?? 'connect all your favorite tools', 320, 360, 22, {textAnchor: 'middle', fontWeight: 600,
      keyframes: {opacity: keys([30, 0], [38, 1])}}),
    ...nodes
  ]};
}

function avatarCluster(options, time) {
  // Circular portraits converge into a loose constellation under a claim.
  const keys = (...samples) => samples.map(([frame, value]) => ({t: time(frame), value, ease: 'linear'}));
  const count = Math.min(10, Math.max(4, options.count ?? 7));
  const nodes = Array.from({length: count}, (_, i) => {
    const angle = i * 2.399963; // golden-angle spread
    const rx = 40 + (i % 3) * 62, ry = 30 + (i % 2) * 56;
    const x = 320 + Math.cos(angle) * rx - 21, y = 170 + Math.sin(angle) * ry - 21;
    const sx = 320 + Math.cos(angle) * (rx + 320), sy = 170 + Math.sin(angle) * (ry + 260);
    const node = Avatar({id: 'face-' + i, x, y, size: 42, initials: String.fromCharCode(65 + i),
      fill: ['#d8e2f0', '#ecd9d1', '#e6e6d6', '#d8e6e9'][i % 4]});
    node.keyframes = {x: keys([2 + i * 2, sx], [16 + i * 2, x, 'easeOut']),
      y: keys([2 + i * 2, sy], [16 + i * 2, y, 'easeOut']),
      opacity: keys([2 + i * 2, 0], [6 + i * 2, 1]),
      scaleX: keys([2 + i * 2, .4], [16 + i * 2, 1]), scaleY: keys([2 + i * 2, .4], [16 + i * 2, 1])};
    node.originX = 21; node.originY = 21;
    return node;
  });
  return {width: 640, height: 360, layers: [
    text('claim', options.copy ?? 'Remembers your people', 320, 158, 30, {textAnchor: 'middle', fontWeight: 600,
      keyframes: {opacity: keys([0, 0], [6, 1])}}),
    ...nodes
  ]};
}

function productRail(options, time) {
  // An authored (unmeasured) continuous horizontal pan of product images under
  // fixed card chrome — same interaction family as the measured photo strip.
  const keys = (...samples) => samples.map(([frame, value]) => ({t: time(frame), value, ease: 'linear'}));
  const images = options.images ?? [];
  const colors = options.swatches ?? ['#e8ded5', '#d9c9bd', '#efe6da', '#cbb7a8', '#e2d5c9'];
  const rail = group('rail', 0, 0, colors.map((c, i) => images[i]
    ? imageTile('item-' + i, images[i], i * 288, 272, 300, 14)
    : group('item-' + i, i * 288, 0, [rect('item-body-' + i, 0, 0, 272, 300, c, 14), text('item-mark-' + i, '✦', 136, 130, 40, {textAnchor: 'middle'})])
  ), {keyframes: {x: keys([4, 0], [14, -180], [26, -430], [34, -576])}});
  return {width: 640, height: 460, layers: [
    group('product-card', 100, 20, [
      text('name', options.title ?? 'Necklaces', 0, 0, 28, {fontWeight: 600}),
      text('detail', options.copy ?? 'Sterling silver · New in', 0, 42, 17, {fill: '#5d6a72'}),
      group('rail-viewport', 0, 84, [rail], {clip: {x: 0, y: 0, width: 440, height: 300}}),
      ActionButton({id: 'action', x: 0, y: 400, width: 160, copy: options.action ?? 'Add to Bag', fill: options.color ?? '#101417'})
    ])
  ]};
}

const otherBlocks = {
  'daniel-typing-to-reply': typingReply,
  'poke-choice-to-outgoing': choiceToOutgoing,
  'mini-anchored-rich-card': anchoredCard,
  'linq-conversation-to-app': conversationToApp,
  scrollList,
  chipRail,
  statCounter,
  appDrawerGrid,
  gridAssemble,
  avatarCluster,
  productRail
};

function scopeIds(layer, prefix) {
  layer.id = prefix + '-' + layer.id;
  layer.children?.forEach(child => scopeIds(child, prefix));
}

export function mountMotion(id, input = {}) {
  const entry = getMotion(id);
  if (!entry) throw Error('Unknown catalog motion: ' + id);
  if (entry.status === 'evidence-gap') throw Error(entry.title + ': ' + entry.limits[0]);
  const {instanceId = entry.id, x = 0, y = 0, scale = 1, start = 0, variant = 'measured',
    context = 'isolated', color = neutralBlue} = input;
  if (!/^[-a-zA-Z0-9_]+$/.test(instanceId) || typeof instanceId !== 'string') throw Error('Use a unique simple instanceId');
  if (![x,y,scale,start].every(Number.isFinite) || scale <= 0 || start < 0) throw Error('Invalid mount position, scale or start time');
  if (!/^#[0-9a-f]{6}$/i.test(color)) throw Error('Use a six-digit hex color');
  if (!['isolated','restaurant','conversation'].includes(context) || (entry.id !== railId && context !== 'isolated')) throw Error('Unsupported motion context');
  if (!['measured','controls'].includes(variant) || (entry.id !== railId && variant !== 'measured')) throw Error('Unsupported motion variant');
  const [first,last] = variant === 'controls' ? entry.source.referencePreviewFrames : entry.source.sourceFrames;
  const nativeDuration = (last-first+1) / designRate;
  const duration = input.duration ?? nativeDuration;
  if (!Number.isFinite(duration) || duration < 1/designRate) throw Error('Duration must be at least one output frame');
  const time = frame => start + frame / designRate * (duration / nativeDuration);

  const options = {...input, variant, context, color};
  const builder = entry.id === railId ? null : otherBlocks[entry.implementation?.block ?? entry.id];
  if (entry.id !== railId && !builder) {
    throw Error(`${entry.id} has no editable block yet — it is a preview-only catalog entry. See its source preview.`);
  }
  const built = entry.id === railId ? photoStrip(entry,options,time) : builder(options,time);
  const [defaultWidth, defaultHeight] = sizes[entry.id] ?? [];
  const spec = Array.isArray(built) ? {width:defaultWidth, height:defaultHeight, layers:built} : built;
  spec.layers.forEach(layer => scopeIds(layer,instanceId));
  const layer = group(instanceId,x,y,spec.layers,{start,end:start+duration,scaleX:scale,scaleY:scale});
  const adapted = duration !== nativeDuration || context !== 'isolated' || Boolean(input.images);
  const provenance = entry.status === 'measured'
    ? adapted ? 'Measured rail samples with authored adaptation' : 'Measured rail samples in editable viewport'
    : 'Source-informed authored adaptation';
  const hooks = entry.cues.options.map(({sourceFrame,kind,provenance}) => ({time:time(sourceFrame-first),kind,
    target:instanceId,provenance}));
  return {layer, duration, hooks, width:spec.width, height:spec.height,
    background:spec.background ?? TOKENS.paper, provenance, sourceFrames:[first,last]};
}

export function motionScene(id, options = {}) {
  const entry = getMotion(id);
  const block = mountMotion(id, options);
  const {layer,width,height,background,duration,sourceFrames,provenance,hooks} = block;
  const scene = {width,height,background,fps:designRate,duration:layer.start+duration,title:entry.title,
    source:{sourceStart:sourceFrames[0]/designRate,sourceEnd:(sourceFrames[1]+1)/designRate,notes:provenance},
    layers:[layer]};
  if (entry.source.nativeRate !== '30/1' || duration !== (sourceFrames[1]-sourceFrames[0]+1)/designRate || layer.start) {
    // The scene contract treats sourceStart/End as an exact time offset.
    delete scene.source.sourceStart;
    delete scene.source.sourceEnd;
  }
  return {scene, description:entry.description, provenance, events:hooks.map(event => ({
    ...event, frame:Math.ceil(event.time * designRate - 1e-8)
  }))};
}
