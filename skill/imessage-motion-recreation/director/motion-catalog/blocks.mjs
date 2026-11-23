import {ActionButton, AppCard, Composer, MessageBubble, PhoneFrame, TOKENS, group, rect, text} from '../components.mjs';
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

function photoStrip(entry, options, time) {
  const {variant, context, images, title, color, action} = options;
  const {slots, viewport, railDxPx} = entry.measurement;
  const {x, y, width, height} = viewport;
  if (images !== undefined && (!Array.isArray(images) || images.length !== slots.length ||
      images.some(src => typeof src !== 'string' || !src.trim()))) {
    throw Error('Supply five image paths, one per measured slot');
  }

  const tiles = slots.map((slot, index) => imageTile(
    slot.actor, images?.[index] ?? builtInAsset(slot.asset), slot.x, slot.width, height, 17
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

const otherBlocks = {
  'daniel-typing-to-reply': typingReply,
  'poke-choice-to-outgoing': choiceToOutgoing,
  'mini-anchored-rich-card': anchoredCard,
  'linq-conversation-to-app': conversationToApp
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
  const [defaultWidth, defaultHeight] = sizes[entry.id] ?? [];
  const spec = entry.id === railId ? photoStrip(entry,options,time) : {
    width:defaultWidth, height:defaultHeight, layers:otherBlocks[entry.id](options,time)
  };
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
