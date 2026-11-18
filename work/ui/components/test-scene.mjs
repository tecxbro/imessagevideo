/** Builds component-test scenes for the html engine.
 * Usage: node test-scene.mjs <name> → writes scenes/<name>.json */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {MessageBubble, TapbackBadge, TypingIndicator, Composer, AppCard, PhotoStrip,
        DeviceFrame, NavBar, VoiceMessage, DeliveryStatus, AppDrawer, Avatar, CameraRig,
        TOKENS, group, text} from './components-v2.mjs';

const dir = path.dirname(fileURLToPath(import.meta.url));
const name = process.argv[2] ?? 'thread';
const W = 960, H = 540, FS = 30;

function scene(layers, extra = {}) {
  return {width: W, height: H, fps: FS, duration: extra.duration ?? 6, background: '#f2f2f7', ...extra, layers};
}

const scenes = {
  /* Q4 layout proof: 1-line vs 4-line copy, tails, tapback anchored through a real
   * thread scroll, group chrome, typing, composer lifecycle, Delivered status. */
  thread() {
    const margin = 270, f = 22;                       // compact font scale so thread fits
    const b = (id, side, copy, opts = {}) =>
      MessageBubble({id, side, copy, fontSize: f, x: side === 'outgoing' ? 0 : margin, ...opts});
    const in1 = b('in1', 'incoming', 'Sure, it’ll be $166.89', {tail: false});
    in1.y = 26;
    const out1 = b('out1', 'outgoing', 'can you order my weekly groceries? 🛒 and maybe a cake too', {maxWidth: 300});
    out1.x = W - margin - out1.meta.w;
    out1.y = in1.y + in1.meta.h + 8;
    const in2 = b('in2', 'incoming', 'Apple Cash request below', {tail: false});
    in2.y = out1.y + out1.meta.h + 8;
    const card = AppCard({id: 'cash', x: margin, y: in2.y + in2.meta.h + 8, width: 240,
      title: 'Cash', caption: '$166.89 Request', cta: 'Pay', skin: 'cash', fontSize: f,
      badge: {label: '', color: '#ffffff', ink: '#000'}});
    const in3 = b('in3', 'incoming', 'Got it, ordering now 🛒', {tapback: {emoji: '👍', from: 'me'}});
    in3.y = card.y + card.meta.h + 10;
    const grp = b('grp', 'incoming', 'how about this one?', {tail: false, senderName: 'Renata',
      senderAvatar: {initials: 'R', fill: '#e8d0e9'}});
    grp.x = margin + f * 2.3;
    grp.y = in3.y + in3.meta.h + 30;
    const typing = TypingIndicator({id: 'typing', x: margin, y: grp.y + grp.meta.h + 12, fontSize: f,
      t0: 1.2, cycles: 6});
    typing.keyframes = {opacity: [{t: 0, value: 0}, {t: 1.1, value: 0, ease: 'hold'}, {t: 1.2, value: 1}]};
    const sent = b('sent', 'outgoing', "Yo i'm bored, chess battle?");
    sent.x = W - margin - sent.meta.w;
    sent.y = typing.y + typing.meta.h + 10;
    sent.keyframes = {opacity: [{t: 4.4, value: 0}, {t: 4.55, value: 1}],
      y: [{t: 4.4, value: sent.y + 40}, {t: 4.75, value: sent.y, ease: 'easeOut'}]};
    const status = DeliveryStatus({id: 'status', y: sent.y + sent.meta.h + 4, anchorX: W - margin,
      copy: 'Delivered', fontSize: f, start: 4.8});
    // the scroll: whole thread (incl. tapback'd card + bubble) slides up at t=3.0
    const threadG = group('thread', 0, 0, [in1, out1, in2, card, in3, grp, typing, sent, status]);
    threadG.keyframes = {y: [{t: 0, value: 0}, {t: 3.0, value: 0, ease: 'hold'}, {t: 3.6, value: -190, ease: 'easeInOut'}]};
    const comp = Composer({id: 'comp', x: margin, y: H - 50, width: W - margin * 2, height: 34,
      placeholder: 'iMessage', typed: "Yo i'm bored, chess battle?", typeStart: 1.4, sendT: 4.4, typedSteps: 8});
    const nav = NavBar({id: 'nav', x: margin, y: 2, width: W - margin * 2, name: 'Linq', fontSize: 14});
    return scene([threadG, comp, nav], {duration: 6});
  },

  /* Camera proof: device frame + world-space props through a camera move. */
  device() {
    const nav = NavBar({id: 'nav', x: 0, y: 0, width: 251, name: 'Muse', avatar: {initials: 'M', fill: '#f0d9c8'}, fontSize: 13});
    const b1 = MessageBubble({id: 'db1', x: 0, y: 64, side: 'outgoing', copy: 'muse, my boss wants a team offsite tmr. can u help?', fontSize: 13, maxWidth: 170});
    b1.x = 251 - 12 - b1.meta.w;
    const ty = TypingIndicator({id: 'dty', x: 12, y: 190, fontSize: 13, t0: 0.4, cycles: 6});
    const b2 = MessageBubble({id: 'db2', x: 12, y: 215, side: 'incoming', copy: 'sure lemme bring in some friends.', fontSize: 13});
    b2.start = 3.4;
    const comp = Composer({id: 'dcomp', x: 8, y: 486, width: 235, height: 28, placeholder: 'iMessage'});
    const phone = DeviceFrame({id: 'phone', x: 0, y: 0, width: 260, height: 530,
      children: [nav, b1, ty, b2, comp]});
    const phoneWrap = group('phone-slot', 350, 5, [phone]);
    phoneWrap.keyframes = {
      scaleX: [{t: 0, value: 1.25}, {t: 1.2, value: 1, ease: 'easeInOut'}, {t: 4, value: 1}, {t: 5.4, value: 1.12, ease: 'easeInOut'}],
      scaleY: [{t: 0, value: 1.25}, {t: 1.2, value: 1, ease: 'easeInOut'}, {t: 4, value: 1}, {t: 5.4, value: 1.12, ease: 'easeInOut'}],
      x: [{t: 0, value: 220}, {t: 1.2, value: 350, ease: 'easeInOut'}, {t: 4, value: 350}, {t: 5.4, value: 320, ease: 'easeInOut'}],
      rotation: [{t: 0, value: 0}, {t: 4, value: 0}, {t: 5.4, value: -4, ease: 'easeInOut'}],
    };
    phoneWrap.originX = 130; phoneWrap.originY = 265;
    // world-space props: title text + floating emoji — must NOT follow phone
    const title = text('title', 'Your iMessage agent', 480, 40, 30, {fontWeight: 700, textAnchor: 'middle'});
    const deco = text('deco', '⚽ 🍕 ✨', 80, 480, 44);
    const cam = CameraRig({id: 'camera', children: [title, deco],
      keyframes: {x: [{t: 3, value: 0}, {t: 5.4, value: -60, ease: 'easeInOut'}]}});
    return scene([cam, phoneWrap], {duration: 6});
  },

  /* Attachment proof: card arrival → tap → expand morph; photo strip under chrome. */
  card() {
    const strip = PhotoStrip({id: 'strip', x: 0, y: 0, width: 300, height: 130, speed: 60, t0: 0.5, duration: 5,
      images: [
        {src: 'data:image/svg+xml,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="200" height="130"><rect width="200" height="130" fill="#c96f4a"/><circle cx="100" cy="65" r="30" fill="#f4d6a0"/></svg>'), width: 200},
        {src: 'data:image/svg+xml,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="200" height="130"><rect width="200" height="130" fill="#4a6f8c"/><rect x="60" y="40" width="80" height="50" fill="#e8e0d0"/></svg>'), width: 200},
        {src: 'data:image/svg+xml,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="200" height="130"><rect width="200" height="130" fill="#6f8c5a"/><ellipse cx="100" cy="65" rx="45" ry="28" fill="#f0e6c8"/></svg>'), width: 200},
      ]});
    const card = AppCard({id: 'rest', x: 280, y: 120, width: 300, mediaHeight: 130,
      title: 'Boqueria Soho', caption: 'Tap for details', cta: null,
      badge: {label: 'B', color: '#fff'}, mediaChildren: strip.children});
    // fix: use the strip itself inside media clip
    card.children.find(c => c.id === 'rest-card').children[1] =
      group('rest-media', 0, 0, [strip], {clip: {x: 0, y: 0, width: 300, height: 130, radius: 26}});
    const arrival = MessageBubble({id: 'intro', x: 280, y: 40, side: 'incoming', copy: "Here's what's hot right now 🔥", fontSize: FS});
    card.start = 1.0;
    card.keyframes = {opacity: [{t: 1.0, value: 0}, {t: 1.15, value: 1}],
      scaleX: [{t: 1.0, value: 0.6}, {t: 1.3, value: 1, ease: 'easeOut'}],
      scaleY: [{t: 1.0, value: 0.6}, {t: 1.3, value: 1, ease: 'easeOut'}]};
    card.originX = 30; card.originY = 60;
    // expanded panel appearing on tap (verified morph, not push): same surface grows
    const panel = group('rest-panel', 200, 60, [
      {id: 'rest-panel-surface', type: 'rect', x: 0, y: 0, width: 560, height: 420, fill: '#ffffff', radius: 30, shadow: {x: 0, y: 8, blur: 30, color: '#00000033'}},
      text('rest-panel-title', 'Boqueria Soho', 30, 26, 30, {fontWeight: 700}),
      text('rest-panel-back', '‹', 14, 18, 34, {fill: TOKENS.blueAlt}),
      {id: 'rest-panel-cta', type: 'rect', x: 30, y: 340, width: 500, height: 56, fill: '#1b1b1b', radius: 28},
      text('rest-panel-cta-label', 'Directions', 280, 355, 22, {fill: '#ffffff', textAnchor: 'middle', fontWeight: 600}),
    ], {start: 3.6});
    panel.keyframes = {opacity: [{t: 3.6, value: 0}, {t: 3.75, value: 1}],
      scaleX: [{t: 3.6, value: 0.55}, {t: 3.95, value: 1, ease: 'easeOut'}],
      scaleY: [{t: 3.6, value: 0.55}, {t: 3.95, value: 1, ease: 'easeOut'}]};
    panel.originX = 280; panel.originY = 270;
    card.keyframes.opacity.push({t: 3.6, value: 1}, {t: 3.7, value: 0});
    return scene([arrival, card, panel], {duration: 6});
  },

  /* Unfamiliar-content stress: long names, emoji-heavy copy, 3-photo attachment,
   * tapback, reply bubble — copy/assets NOT designed for the components. */
  unfamiliar() {
    const margin = 250, f = 24, gut = margin + f * 2.3;
    const svg = (sky, sun, hill) => 'data:image/svg+xml,' + encodeURIComponent(
      `<svg xmlns="http://www.w3.org/2000/svg" width="330" height="200"><rect width="330" height="200" fill="${sky}"/><circle cx="240" cy="55" r="34" fill="${sun}"/><rect y="130" width="330" height="70" fill="${hill}"/></svg>`);
    const nav = NavBar({id: 'nav', x: margin, y: 2, width: W - margin * 2,
      name: 'Isabella-Catherine Montgomery-Whitfield', fontSize: 15});
    const in1 = MessageBubble({id: 'u1', x: gut, y: 62, side: 'incoming', fontSize: f,
      copy: 'guess who finally passed her sommelier exam 🍷🥂🎉',
      senderName: 'Isabella-Catherine Montgomery-Whitfield'});
    const av = Avatar({id: 'av', x: margin, y: in1.y + in1.meta.h - f * 1.8, size: f * 1.5, initials: 'I', fill: '#d9c8e8'});
    const att = PhotoStrip({id: 'att', x: gut, y: in1.y + in1.meta.h + 8, width: 340, height: 200,
      speed: 0, t0: 0, duration: 0.001, gap: 8,
      images: [{src: svg('#7db3d8', '#ffd34d', '#4a7a4a'), width: 240},
               {src: svg('#e88f6a', '#fff2cc', '#7a4a3a'), width: 240},
               {src: svg('#8e6bbf', '#f5a7c0', '#3a5a7a'), width: 240}]});
    const in2 = MessageBubble({id: 'u2', x: gut, y: att.y + att.meta.h + 14, side: 'incoming', fontSize: f,
      copy: 'celebration dinner thursday — you in?', tapback: {emoji: '🎉', from: 'me'}});
    const out1 = MessageBubble({id: 'u3', y: in2.y + in2.meta.h + 16, side: 'outgoing', fontSize: f,
      copy: 'obviously yes 🙌 but why is the reservation under "Dr. Bartholomew Featherstonehaugh III"?', maxWidth: 340});
    out1.x = W - margin - out1.meta.w;
    const in3 = MessageBubble({id: 'u4', x: gut, y: out1.y + out1.meta.h + 12, side: 'incoming', fontSize: f,
      copy: 'long story 😅', tail: true});
    const threadG = group('thread', 0, 0, [in1, av, att, in2, out1, in3]);
    threadG.keyframes = {y: [{t: 0, value: 0}, {t: 3.2, value: 0, ease: 'hold'}, {t: 3.8, value: -180, ease: 'easeInOut'}]};
    const comp = Composer({id: 'comp', x: margin, y: H - 50, width: W - margin * 2, height: 34,
      placeholder: 'iMessage', typed: 'lmao ok 😂', typeStart: 4.0, sendT: 5.4, typedSteps: 3});
    return scene([threadG, comp, nav], {duration: 6});
  },

  /* Drawer + voice note. */
  extras() {
    const voice = VoiceMessage({id: 'vm', x: 260, y: 60, fontSize: 30, seconds: 4, transcript: 'Please remind me about this dinner…'});
    const drawer = AppDrawer({id: 'drawer', x: 300, y: 220, width: 360, fontSize: 26});
    drawer.keyframes = {y: [{t: 0, value: 540}, {t: 0.8, value: 220, ease: 'easeOut'}]};
    const comp = Composer({id: 'c2', x: 260, y: 490, width: 440, height: 44, placeholder: 'Message Poke'});
    return scene([voice, drawer, comp], {duration: 4});
  },
};

const s = scenes[name]();
fs.mkdirSync(path.join(dir, 'scenes'), {recursive: true});
const out = path.join(dir, 'scenes', name + '.json');
fs.writeFileSync(out, JSON.stringify(s, null, 1));
console.log('wrote', out, 'layers', s.layers.length);
