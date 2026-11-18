/** Editable starter components. Coordinates in a 960x540 design space.
 * These are new reusable designs, not traced/proprietary source UI assets.
 * All builders emit the same measured-scene contract consumed by the engines.
 */
export const TOKENS=Object.freeze({paper:'#f7f7f5',ink:'#17191d',muted:'#777b84',blue:'#1688fa',incoming:'#e9e9ed',line:'#d8dbe0',font:'Arial, sans-serif'});
const finite=(n,label,min=0,max=10000)=>{if(!Number.isFinite(n)||n<min||n>max)throw Error(`Invalid ${label}`);return n;};
const safeId=id=>{if(typeof id!=='string'||!/^[-a-zA-Z0-9_]+$/.test(id))throw Error('Use a unique simple component id');return id;};
const rect=(id,x,y,width,height,fill,radius=0,extra={})=>({id,type:'rect',x,y,width,height,fill,radius,...extra});
const text=(id,value,x,y,size=18,extra={})=>({id,type:'text',text:String(value),x,y,fontSize:size,fontFamily:TOKENS.font,fill:TOKENS.ink,...extra});
const group=(id,x,y,children,extra={})=>({id:safeId(id),type:'group',x,y,children,...extra});
export {rect,text,group};

export function MessageBubble({id,x=0,y=0,width=248,height=70,side='outgoing',copy='Can you book it?',tail=true,fill,fontSize=19}){
  safeId(id);finite(width,'bubble width',80);finite(height,'bubble height',38);
  if(!['incoming','outgoing'].includes(side))throw Error('Invalid message side');
  const color=fill??(side==='outgoing'?TOKENS.blue:TOKENS.incoming);
  const nodes=[rect(id+'-body',0,0,width,height,color,20)];
  if(tail){const d=side==='outgoing'?`M ${width-16} ${height-18} Q ${width-3} ${height+1} ${width+7} ${height-2} Q ${width-3} ${height-6} ${width-2} ${height-20} Z`:`M 16 ${height-18} Q 3 ${height+1} -7 ${height-2} Q 3 ${height-6} 2 ${height-20} Z`;nodes.push({id:id+'-tail',type:'path',d,fill:color});}
  nodes.push(text(id+'-copy',copy,17,14,fontSize,{fill:side==='outgoing'?'#ffffff':TOKENS.ink,lineHeight:24}));
  return group(id,x,y,nodes);
}
export function ActionButton({id,x=0,y=0,width=140,height=42,copy='Continue',fill=TOKENS.blue}){
  return group(id,x,y,[rect(id+'-shape',0,0,width,height,fill,height/2),text(id+'-label',copy,width/2,11,16,{fill:'#ffffff',textAnchor:'middle',fontWeight:600})]);
}
export function Composer({id,x=0,y=0,width=430,copy='',active=true}){
  return group(id,x,y,[rect(id+'-field',0,0,width,48,'#ffffff',24,{stroke:TOKENS.line,strokeWidth:1}),text(id+'-input',copy||'Message',18,14,17,{fill:copy?TOKENS.ink:TOKENS.muted}),
    {id:id+'-send',type:'circle',x:width-40,y:8,width:32,height:32,fill:active?TOKENS.blue:TOKENS.line},
    {id:id+'-arrow',type:'path',d:`M ${width-24} 33 L ${width-24} 16 M ${width-31} 23 L ${width-24} 16 L ${width-17} 23`,fill:'none',stroke:'#ffffff',strokeWidth:2}]);
}
export function AppIcon({id,x=0,y=0,size=64,roundness=.24,color='#22252a',label='A'}){
  finite(roundness,'icon roundness',0,.5);
  return group(id,x,y,[rect(id+'-shape',0,0,size,size,color,size*roundness),text(id+'-mark',label,size/2,size*.23,size*.42,{fill:'#ffffff',textAnchor:'middle',fontWeight:600})]);
}
export function AppCard({id,x=0,y=0,width=340,height=226,title='Your booking',detail='Friday · 7:00 PM',action='Confirm',color='#e9f1e7',image}){
  finite(width,'card width',180);finite(height,'card height',160);
  const art=image?imageTile(id+'-art',image,12,12,width-24,height*.36,14):rect(id+'-art',12,12,width-24,height*.36,color,14);
  return group(id,x,y,[rect(id+'-surface',0,0,width,height,'#ffffff',22,{stroke:TOKENS.line,strokeWidth:1}),art,
    text(id+'-title',title,20,height*.46,23,{fontWeight:600}),text(id+'-detail',detail,20,height*.46+33,16,{fill:TOKENS.muted}),
    ActionButton({id:id+'-action',x:20,y:height-58,width:width-40,copy:action})]);
}
export function Avatar({id,x=0,y=0,size=42,initials='JD',fill='#d8e2f0',image}){
  if (image) return imageTile(id,image,x,y,size,size,size/2);
  return group(id,x,y,[{id:id+'-disc',type:'circle',width:size,height:size,fill},text(id+'-initials',initials,size/2,size*.27,size*.32,{textAnchor:'middle',fontWeight:600})]);
}
export function BottomSheet({id,x=0,y=0,width=430,height=310,title='Apps',children=[]}){
  return group(id,x,y,[rect(id+'-surface',0,0,width,height,'#f5f5f7',25),rect(id+'-handle',width/2-19,10,38,4,'#c4c7cc',2),text(id+'-heading',title,22,33,24,{fontWeight:600}),...children],{clip:{x:0,y:0,width,height,radius:25}});
}
export function PhoneFrame({id,x=0,y=0,width=440,height=500,title='A conversation',children=[]}){
  return group(id,x,y,[rect(id+'-matte',0,0,width,height,'#ffffff',28,{stroke:TOKENS.line,strokeWidth:1}),
    group(id+'-screen',0,0,[...children],{clip:{x:0,y:0,width,height,radius:28}}),
    rect(id+'-bar',1,1,width-2,66,'#f8f8fa',27),rect(id+'-bar-square',1,33,width-2,33,'#f8f8fa'),
    text(id+'-back','‹',18,17,30,{fill:TOKENS.blue}),text(id+'-title',title,width/2,25,17,{textAnchor:'middle',fontWeight:600}),rect(id+'-divider',1,66,width-2,1,TOKENS.line)]);
}
export function CameraRig({id='camera',children=[],keyframes={},x=0,y=0,originX=480,originY=270}){
  return group(id,x,y,children,{originX,originY,keyframes});
}

const segmenter = new Intl.Segmenter(undefined, {granularity: 'grapheme'});
const graphemes = value => Array.from(segmenter.segment(value), item => item.segment);
const emojiFont = 'Arial, Apple Color Emoji, Segoe UI Emoji, Noto Color Emoji, sans-serif';
const key = (t, value, ease = 'hold') => ({t, value, ease});

// Stable across replay hosts. Supply measured metrics when using a different face or script.
function estimatedWidth(copy, size) {
  return graphemes(copy).reduce((sum, letter) => {
    if (/^[\p{Extended_Pictographic}\p{Regional_Indicator}\p{Script=Han}\p{Script=Hangul}\p{Script=Hiragana}\p{Script=Katakana}]|\u20e3/u.test(letter)) return sum + 1.2 * size;
    if (/^[ilI1.,:;!'`|\s]/u.test(letter)) return sum + .31 * size;
    if (/^[MWmw@%&]/u.test(letter)) return sum + .87 * size;
    return sum + (/^[A-Z]/u.test(letter) ? .74 : .62) * size;
  }, 0);
}

function wrappedLines(copy, width, measure) {
  return copy.split(/\r\n?|\n/u).flatMap(paragraph => {
    const lines = [];
    let current = '';
    for (const word of paragraph.trim().split(/\s+/u)) {
      const next = current ? `${current} ${word}` : word;
      if (measure(next) <= width) {
        current = next;
        continue;
      }
      if (current) lines.push(current);
      current = '';
      for (const letter of graphemes(word)) {
        if (current && measure(current + letter) > width) {
          lines.push(current);
          current = '';
        }
        current += letter;
      }
    }
    return [...lines, current];
  });
}

function fittedLabel(copy, width, measure) {
  const singleLine = String(copy).replace(/\s+/gu, ' ').trim();
  if (measure(singleLine) <= width) return singleLine;
  let label = '';
  for (const letter of graphemes(singleLine)) {
    if (measure(label + letter + '…') > width) break;
    label += letter;
  }
  return label + '…';
}

function imageTile(id, image, x, y, width, height, radius, fit = 'cover') {
  if (typeof image?.src !== 'string' || !image.src.trim()) throw Error(`Missing image src for ${id}`);
  if (fit !== 'cover' && fit !== 'contain') throw Error(`Unknown image fit: ${fit}`);
  const preserveAspectRatio = fit === 'cover' ? 'xMidYMid slice' : 'xMidYMid meet';
  const photo = {id: `${id}-image`, type: 'image', src: image.src, width, height, preserveAspectRatio};
  if (image.alt !== undefined) photo.alt = String(image.alt);
  return group(id, x, y, [photo], {clip: {width, height, radius}});
}

export function PhotoAttachment({id, x = 0, y = 0, width = 242, height = 140, image, fit = 'cover'}) {
  finite(width, 'photo width', 100);
  finite(height, 'photo height', 56);
  const tile = imageTile(id, image, x, y, width, height, 15, fit);
  tile.children.unshift(rect(`${id}-surface`, 0, 0, width, height, '#eeedf0'));
  return tile;
}

export function AttachmentCollage({id, x = 0, y = 0, width = 244, height = 162, images}) {
  finite(width, 'collage width', 100);
  finite(height, 'collage height', 82);
  if (![2, 3].includes(images?.length)) throw Error('AttachmentCollage needs two or three images');
  // Authored overlapping arrangement. Individual frame sizes can differ in actual Photos bundles.
  const columns = images.length === 3 ? [.03, .32, .08] : [0, .32];
  const rows = images.length === 3 ? [0, .24, .5] : [0, .32];
  const tileHeight = height * (images.length === 3 ? .5 : .68);
  const tiles = images.map((image, i) => imageTile(`${id}-photo-${i}`, image, width * columns[i], height * rows[i], width * .68, tileHeight, 12));
  return group(id, x, y, tiles, {clip: {width, height, radius: 12}});
}

export function PhotoStrip({id, x = 0, y = 0, width = 242, height = 115, images, position = []}) {
  finite(width, 'strip width', 100);
  finite(height, 'strip height', 56);
  if (!images?.length) throw Error('PhotoStrip needs at least one image');
  const gap = 5;
  const itemWidth = images.length === 1 ? width : Math.round(width * .78);
  const maxOffset = images.length * itemWidth + (images.length - 1) * gap - width;
  const visuals = images.map((image, i) => imageTile(`${id}-photo-${i}`, image, i * (itemWidth + gap), 0, itemWidth, height, 9));
  const motion = new Map([[0, key(0, 0)]]);
  for (const {t, value, ease = 'easeInOut'} of position) {
    finite(t, 'strip key time');
    motion.set(t, key(t, -Math.min(maxOffset, finite(value, 'strip offset')), ease));
  }
  const rail = group(`${id}-rail`, 0, 0, visuals, {keyframes: {x: [...motion.values()].sort((a, b) => a.t - b.t)}});
  return group(id, x, y, [rect(`${id}-surface`, 0, 0, width, height, '#f0eeea', 16), rail], {clip: {width, height, radius: 16}});
}

function setTrack(track, point) {
  const last = track.at(-1);
  if (last?.t !== point.t) track.push(point);
  else if (last.value !== point.value) track[track.length - 1] = point;
}

export function AttachmentStack({id, x = 0, y = 0, width = 222, height = 150, images, swipes = []}) {
  finite(width, 'stack width', 100);
  finite(height, 'stack height', 82);
  if (!images?.length) throw Error('AttachmentStack needs at least one image');
  const depth = Math.min(2, images.length - 1);
  const faceWidth = width - 6 * depth;
  const faceHeight = height - 4 * depth;
  const cards = images.map((image, i) => {
    const card = imageTile(`${id}-photo-${i}`, image, 0, 0, faceWidth, faceHeight, 14);
    return {...card, originX: faceWidth / 2, originY: faceHeight / 2, keyframes: {
      x: [key(0, 0)], rotation: [key(0, 0)], opacity: [key(0, i === 0 ? 1 : 0)],
    }};
  });
  let current = 0;
  let settledAt = 0;
  const offscreenX = -width - Math.ceil(height * .12) - 6;
  for (const {at, index, duration = .32} of swipes) {
    finite(at, 'stack swipe time', settledAt);
    finite(duration, 'stack swipe duration', .05, 2);
    if (!Number.isInteger(index) || !cards[index] || index === current) throw Error('Stack swipe needs a different image index');
    const departing = cards[current].keyframes;
    const arriving = cards[index].keyframes;
    const forward = index > current;
    settledAt = at + duration;
    for (const [prop, from, to] of [['x', 0, forward ? offscreenX : 0], ['rotation', 0, forward ? -12 : 0]]) {
      setTrack(departing[prop], key(at, from));
      setTrack(departing[prop], key(settledAt, to, 'easeInOut'));
    }
    for (const [prop, from] of [['x', forward ? 6 : offscreenX], ['rotation', forward ? 0 : -12]]) {
      setTrack(arriving[prop], key(at, from));
      setTrack(arriving[prop], key(settledAt, 0, 'easeInOut'));
    }
    // Keep both cards opaque during contact. Paint order reveals the next card
    // as the higher card slides, and the losing card disappears once covered or offscreen.
    setTrack(departing.opacity, key(settledAt, 0));
    setTrack(arriving.opacity, key(at, 1));
    current = index;
  }
  const backing = Array.from({length: depth}, (_, i) => {
    const step = depth - i;
    return rect(`${id}-edge-${step}`, step * 6, step * 4, faceWidth, faceHeight, step === 2 ? '#bbbcc4' : '#d6d7dd', 14);
  });
  return group(id, x, y, [...backing, ...cards.reverse()], {clip: {width, height, radius: 14}});
}

function reactionBadge(id, x, {at, emoji = '❤️'}) {
  const bubble = rect(`${id}-disc`, 0, 0, 30, 25, '#e9e9ed', 13, {stroke: '#ffffff', strokeWidth: 1});
  const dot = {id: `${id}-dot`, type: 'circle', x: 4, y: 20, width: 8, height: 8, fill: '#e9e9ed', stroke: '#ffffff', strokeWidth: .8};
  const mark = /^([❤♥]\uFE0F?)$/u.test(emoji) ? {
    id: `${id}-mark`, type: 'path', x: 7, y: 6,
    d: 'M 8 13 C 5 11 0 8 0 4.5 C 0 .2 5.4 -1 8 2.7 C 10.6 -1 16 .2 16 4.5 C 16 8 11 11 8 13 Z', fill: '#e04768',
  } : text(`${id}-mark`, emoji, 15, 3, 15, {fontFamily: emojiFont, textAnchor: 'middle'});
  const bounce = [key(at, .55), key(at + .12, 1.08, 'easeOut'), key(at + .22, 1, 'easeOut')];
  return group(id, x, -14, [dot, bubble, mark], {start: at, originX: 15, originY: 20, keyframes: {scaleX: bounce, scaleY: bounce}});
}

function attachmentSurface(id, spec, maxWidth, measure) {
  const {type, width, height, ...fields} = spec;
  const size = (fallbackWidth, fallbackHeight) => ({id, width: Math.min(width ?? fallbackWidth, maxWidth), height: height ?? fallbackHeight});
  if (type === 'photo-attachment') {
    const options = size(242, 140);
    return {height: options.height, width: options.width, node: PhotoAttachment({...fields, ...options})};
  }
  if (type === 'attachment-collage') {
    const options = size(244, 162);
    return {height: options.height, width: options.width, node: AttachmentCollage({...fields, ...options})};
  }
  if (type === 'photo-strip') {
    const options = size(252, 112);
    return {height: options.height, width: options.width, node: PhotoStrip({...fields, ...options})};
  }
  if (type === 'attachment-stack') {
    const options = size(222, 150);
    return {height: options.height, width: options.width, node: AttachmentStack({...fields, ...options})};
  }
  if (type === 'app-card') {
    const options = size(272, 205);
    const {title = 'Your booking', detail = 'Friday · 7:00 PM', action = 'Confirm', color, image} = fields;
    const node = AppCard({
      ...options, color, image,
      title: fittedLabel(title, options.width - 40, copy => measure(copy, 23)),
      detail: fittedLabel(detail, options.width - 40, copy => measure(copy, 16)),
      action: fittedLabel(action, options.width - 60, copy => measure(copy, 16)),
    });
    return {height: options.height, width: options.width, node};
  }
  throw Error(`Unknown attachment surface: ${type}`);
}

function conversationComposer(id, y, width, draftKeys, measure) {
  const composer = Composer({id, x: 16, y, width});
  const [field, input, send, arrow] = composer.children;
  const room = width - 48 - input.x;
  const nonempty = draftKeys.map(({t, value}) => key(t, Number(Boolean(value.trim()))));
  const placeholder = text(`${id}-placeholder`, 'Message', input.x, input.y, input.fontSize, {fill: TOKENS.muted, keyframes: {
    opacity: nonempty.map(({t, value}) => key(t, 1 - value)),
  }});
  const display = draftKeys.map(({t, value}) => key(t, value.split(/\r\n?|\n/u).at(-1)));
  input.text = '';
  input.fill = TOKENS.ink;
  input.fontFamily = emojiFont;
  input.keyframes = {text: display, x: display.map(({t, value}) => key(t, input.x - Math.max(0, measure(value, 17) - room)))};
  send.keyframes = {opacity: nonempty};
  arrow.keyframes = {opacity: nonempty};
  const editable = group(`${id}-draft-window`, 0, 0, [input], {clip: {x: input.x, y: 0, width: room, height: 48}});
  composer.children = [field, placeholder, editable, send, arrow];
  return composer;
}

/** Builds editable film actors in the regular JSON scene contract. All cue times are output seconds. */
export function Conversation({id = 'conversation', x = 0, y = 0, width = 390, height = 500, title, people = [], self = 'you', messages = [], draft = [], scroll = [], measureText = estimatedWidth} = {}) {
  safeId(id);
  finite(width, 'conversation width', 270);
  finite(height, 'conversation height', 250);
  const peopleById = new Map();
  for (const person of people) {
    safeId(person.id);
    if (peopleById.has(person.id)) throw Error(`Duplicate participant: ${person.id}`);
    peopleById.set(person.id, person);
  }
  const messageIds = new Set();
  const timeline = messages.map(message => {
    const at = finite(message.at ?? 0, 'message time');
    safeId(message.id);
    if (messageIds.has(message.id)) throw Error(`Duplicate message: ${message.id}`);
    messageIds.add(message.id);
    if (message.person !== self && !peopleById.has(message.person)) throw Error(`Unknown participant: ${message.person}`);
    if (message.send && message.person !== self) throw Error('Only the local participant can send the composer draft');
    return {...message, at};
  }).sort((a, b) => a.at - b.at);
  const draftChanges = new Map([[0, '']]);
  for (const edit of draft) draftChanges.set(finite(edit.at, 'draft time'), String(edit.copy ?? ''));
  const sends = new Map();
  for (const message of timeline.filter(message => message.send)) {
    if (sends.has(message.at)) throw Error('Only one composer send can occur at a time');
    sends.set(message.at, message);
  }
  let draftCopy = '';
  const draftKeys = [];
  const draftTimes = new Set([...draftChanges.keys(), ...sends.keys()]);
  for (const t of [...draftTimes].sort((a, b) => a - b)) {
    draftCopy = draftChanges.get(t) ?? draftCopy;
    if (sends.has(t)) {
      sends.get(t).copy ??= draftCopy;
      draftCopy = '';
    }
    draftKeys.push(key(t, draftCopy));
  }

  const composerY = height - 62;
  const barHeight = 67;
  const transcriptHeight = composerY - barHeight - 5;
  const transcriptWidth = width - 2;
  const visibleContacts = new Set(timeline.map(message => message.person).filter(person => person !== self));
  const arrivalLayouts = new Map();
  let nextTop = 12;
  const rows = timeline.map(message => {
    const prefix = `${id}-message-${message.id}`;
    const outgoing = message.person === self;
    const participant = peopleById.get(message.person);
    const left = outgoing ? 16 : 48;
    const right = 17;
    const maxWidth = Math.min(Math.floor(transcriptWidth * .78), transcriptWidth - left - right);
    const copy = String(message.copy ?? '');
    const hasCopy = Boolean(copy.trim());
    if (!hasCopy && !message.attachment) throw Error(`Message ${message.id} needs copy or an attachment`);
    const surface = message.attachment ? attachmentSurface(`${prefix}-attachment`, message.attachment, maxWidth, measureText) : null;
    const lines = hasCopy ? wrappedLines(copy, maxWidth - 36, line => measureText(line, 17)) : [];
    const bubbleWidth = hasCopy ? Math.min(maxWidth, Math.max(80, ...lines.map(line => Math.ceil(measureText(line, 17)) + 36))) : 0;
    const bubbleHeight = hasCopy ? Math.max(43, 22 * lines.length + 19) : 0;
    const contentWidth = Math.max(bubbleWidth, surface?.width ?? 0);
    const contentHeight = bubbleHeight + (surface?.height ?? 0) + (surface && hasCopy ? 7 : 0);
    const bubbleX = outgoing ? contentWidth - bubbleWidth : 0;
    const showName = !outgoing && visibleContacts.size > 1;
    const reactionInset = message.reaction ? 16 : 0;
    const rowY = nextTop + reactionInset + (showName ? 17 : 0);
    const rowX = outgoing ? transcriptWidth - right - contentWidth : left;
    const nodes = [];
    if (hasCopy) {
      const bubble = MessageBubble({id: prefix, side: outgoing ? 'outgoing' : 'incoming', copy: lines.join('\n'), width: bubbleWidth, height: bubbleHeight, fontSize: 17, tail: !surface});
      for (const child of bubble.children) child.x = (child.x ?? 0) + bubbleX;
      const label = bubble.children.at(-1);
      Object.assign(label, {y: 10, lineHeight: 22, fontFamily: emojiFont});
      nodes.push(...bubble.children);
    }
    if (surface) {
      surface.node.x = outgoing ? contentWidth - surface.width : 0;
      surface.node.y = bubbleHeight + (hasCopy ? 7 : 0);
      nodes.push(surface.node);
    }
    if (!outgoing) {
      const name = String(participant.name ?? participant.id);
      const initials = participant.initials ?? name.split(/\s+/u).slice(0, 2).map(word => graphemes(word)[0] ?? '').join('').toUpperCase();
      nodes.push(Avatar({id: `${prefix}-avatar`, x: -34, y: contentHeight - 26, size: 26, initials: graphemes(String(initials)).slice(0, 2).join(''), fill: participant.fill, image: participant.image}));
      if (showName) {
        const fitted = fittedLabel(name, maxWidth, value => measureText(value, 12));
        nodes.push(text(`${prefix}-name`, fitted, 2, -17 - reactionInset, 12, {fill: '#5f6170'}));
      }
    }
    if (message.reaction) {
      const at = finite(message.reaction.at, 'reaction time', message.at);
      const rightEdge = hasCopy ? bubbleX + bubbleWidth : surface.width;
      nodes.push(reactionBadge(`${prefix}-reaction`, rightEdge - 25, {...message.reaction, at}));
    }
    nextTop = rowY + contentHeight + 11;
    arrivalLayouts.set(message.at, transcriptHeight - nextTop);
    const extra = message.at === 0 ? {} : {start: message.at, keyframes: {
      y: [key(message.at, rowY + 10), key(message.at + .26, rowY, 'easeOut')],
      opacity: [key(message.at, .24), key(message.at + .18, 1, 'easeOut')],
    }};
    return group(prefix, rowX, rowY, nodes, extra);
  });

  const follow = [key(0, arrivalLayouts.get(0) ?? transcriptHeight - 12)];
  const arrivalTimes = [...arrivalLayouts.keys()].filter(t => t > 0);
  for (const [index, t] of arrivalTimes.entries()) {
    setTrack(follow, key(t, follow.at(-1).value));
    follow.push(key(Math.min(t + .28, arrivalTimes[index + 1] ?? Infinity), arrivalLayouts.get(t), 'easeOut'));
  }
  const offsets = new Map([[0, key(0, 0)]]);
  for (const {at, offset, ease = 'easeInOut'} of scroll) {
    finite(at, 'scroll time');
    offsets.set(at, key(at, finite(offset, 'scroll offset'), ease));
  }
  const browse = group(`${id}-history-offset`, 0, 0, rows, {keyframes: {y: [...offsets.values()].sort((a, b) => a.t - b.t)}});
  const moving = group(`${id}-scroll`, 0, 0, [browse], {keyframes: {y: follow}});
  const transcript = group(`${id}-transcript`, 1, barHeight, [moving], {clip: {x: 0, y: 0, width: transcriptWidth, height: transcriptHeight}});
  const composer = conversationComposer(`${id}-composer`, composerY, width - 32, draftKeys, measureText);
  const names = people.filter(person => person.id !== self).map(person => person.name ?? person.id);
  const label = fittedLabel(title ?? (names.join(', ') || 'Conversation'), width - 96, copy => measureText(copy, 17));
  const phone = PhoneFrame({id, x, y, width, height, title: label, children: [transcript, composer]});
  const layerIds = new Set();
  function verifyIds(layer) {
    if (layerIds.has(layer.id)) throw Error(`Message IDs generate an overlapping layer ID: ${layer.id}`);
    layerIds.add(layer.id);
    for (const child of layer.children ?? []) verifyIds(child);
  }
  verifyIds(phone);
  return phone;
}

export const COMPONENTS=Object.freeze([
  {name:'MessageBubble',purpose:'Incoming/outgoing message, editable copy and tail',parameters:['copy','side','width','height','fill','tail']},
  {name:'Composer',purpose:'Typed input and send control as separate layers',parameters:['copy','width','active']},
  {name:'AppIcon',purpose:'An icon whose surface can change corner radius',parameters:['size','roundness','color','label']},
  {name:'AppCard',purpose:'Artwork, heading, detail and action in one reusable card',parameters:['width','height','title','detail','action','color']},
  {name:'BottomSheet',purpose:'Clipped panel with handle and nested app controls',parameters:['width','height','title','children']},
  {name:'PhoneFrame',purpose:'Conversation viewport; screen children are clipped independently',parameters:['width','height','title','children']},
  {name:'ActionButton',purpose:'Action surface and label with stable identity',parameters:['width','height','copy','fill']},
  {name:'Avatar',purpose:'Generic initials, not a copied source portrait',parameters:['size','initials','fill']},
  {name:'CameraRig',purpose:'Parent transform, separate from local UI layout',parameters:['children','keyframes','originX','originY']}
]);
