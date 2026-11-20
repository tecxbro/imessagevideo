// Direction's Moon Cue suggested passing attention from a reply to a nearby prop.
// The editable geometry and full-exit option are adaptations of that passage.

const id = 'screen-to-physical-prop';
const source = {
  kind: 'direction-authored-adaptation',
  ref: 'https://github.com/tecxbro/imessagevideo/blob/db9218888e89660771b9946c5bd0e32568b57a1e/skill/imessage-motion-recreation/direction/film/movement.py',
  picture: 'https://github.com/tecxbro/imessagevideo/blob/db9218888e89660771b9946c5bd0e32568b57a1e/review/imv-v3/direction/locked.mp4',
  pictureSha256: '838fbb35fa9741cb373875d2c6f88536c2dd46ab6abc39978e47a1d7f978cec7',
  range: [140 / 24, 169 / 24],
  frames: [140, 169],
  fps: 24,
  cueFrame: 153,
  note: 'The locked shot holds the readable reply, starts the 12-frame phone/focus lead at 141, cuts at 153, and completes the tin camera push at 168. The phone remains partly visible at 152. The preview ports Direction’s independent source curves. Its full left exit, tighter scale at the cut, and closed-tin hold adapt the requested brief. The source begins lifting the lid at 165.',
};

// Direction's move_to_clue from the locked cut. Sample its independent curves
// at the source cadence, then map those samples to the editable preview clock.
function cluePhase(sourceFrame) {
  const phase = Math.min(1, Math.max(0, (sourceFrame - 141) / 12));
  const pushTime = Math.min(1, Math.max(0, (sourceFrame - 150) / 18));
  return {
    departure: phase ** 1.7,
    focus: phase * phase * (3 - 2 * phase),
    push: 1 - (1 - pushTime) ** 2,
  };
}

function oval(id, x, y, width, height, fill, extra = {}) {
  return {id, type: 'circle', x, y, width, height, fill, ...extra};
}

function propTable(ctx) {
  const {content, group, rect, text} = ctx;
  const tin = group('prop-tin', 242, 125, [
    oval('tin-contact-shadow', -4, 60, 197, 61, '#161016', {blur: 8, opacity: .72}),
    oval('tin-bottom', 1, 29, 182, 71, '#6d272c', {stroke: '#402029', strokeWidth: 3}),
    rect('tin-wall', 2, 39, 179, 24, '#74262b', 1),
    oval('tin-lid-rim', 0, 0, 185, 79, '#b74d3c', {stroke: '#ed9c74', strokeWidth: 1.5}),
    oval('tin-lid-field', 6, 5, 173, 68, '#ad3b40', {stroke: '#822931', strokeWidth: 2}),
    {id: 'tin-lid-catchlight', type: 'path', d: 'M 19 30 Q 40 12 88 12 Q 129 11 153 21',
      fill: 'none', stroke: '#f6ac83', strokeWidth: 2, opacity: .68},
    text('tin-mark', content.title, 92, 29, 15, {
      textAnchor: 'middle', fill: '#fff0d4', fontWeight: 700, letterSpacing: 1.4,
    }),
    {id: 'tin-mark-underline', type: 'path', d: 'M 75 51 L 109 51',
      fill: 'none', stroke: '#f7ba82', strokeWidth: 1.5},
  ]);
  const ambient = oval('tin-light', 219, 79, 260, 198, '#a66951', {blur: 31, opacity: .55});
  const stars = [[303, 103], [338, 79], [374, 85]].map(([x, y], i) => ({
    id: 'table-star-' + i, type: 'path', x, y, fill: '#e3a86e',
    d: 'M 0 -6 L 1.5 -1.8 L 6 0 L 1.5 1.8 L 0 6 L -1.5 1.8 L -6 0 L -1.5 -1.8 Z',
  }));
  const scene = group('prop-table-camera', 0, 0, [
    rect('table-surface', -280, -120, 1080, 520, '#493039'),
    ambient,
    rect('table-edge', -260, 249, 1020, 54, '#32242a', 0, {originX: 515, rotation: 2.3}),
    rect('table-edge-light', -260, 248, 1020, 2, '#694639', 0, {originX: 515, rotation: 2.3}),
    oval('spool-shadow', 207, 206, 65, 21, '#23191e', {blur: 3, opacity: .62}),
    oval('spool-top', 207, 199, 56, 22, '#674940', {stroke: '#8b5d48', strokeWidth: 2}),
    oval('spool-hole', 229, 206, 9, 7, '#2a2027'),
    ...stars,
    tin,
  ], {originX: 334.5, originY: 164.5});
  return {scene, tin};
}

function wrapMessage(copy, columns) {
  const lines = [];
  let line = '';
  for (const word of copy.trim().split(/\s+/)) {
    if (!line) {
      line = word;
    } else if (line.length + word.length < columns) {
      line += ' ' + word;
    } else {
      lines.push(line);
      line = word;
    }
  }
  return [...lines, line];
}

function handset(ctx) {
  const {content, group, rect, ui} = ctx;
  const question = wrapMessage(content.copy, 26);
  const answer = wrapMessage(content.reply, 26);
  const questionHeight = 25 + 24 * question.length;
  const replyY = 111 + questionHeight + 15;
  const phone = ui.PhoneFrame({
    id: 'prop-conversation', width: 360, height: 480, title: content.action,
    children: [
      ui.MessageBubble({
        id: 'prop-question', x: 81, y: 111, width: 253, height: questionHeight,
        copy: question.join('\n'), fontSize: 20,
      }),
      ui.MessageBubble({
        id: 'prop-reply', x: 24, y: replyY, width: 273, height: 25 + 24 * answer.length,
        copy: answer.join('\n'), fontSize: 20, side: 'incoming',
      }),
      ui.Composer({id: 'prop-composer', x: 20, y: 408, width: 320, active: false}),
    ],
  });
  return group('prop-handset', 35, 9, [
    rect('handset-body', 0, 0, 219, 280, '#20191f', 19, {stroke: '#986a54', strokeWidth: 2}),
    group('editable-handset-screen', 8, 7, [phone], {scaleX: .562, scaleY: .552}),
  ], {originX: 109.5, originY: 140});
}

export const entries = [{
  id,
  title: 'Pass attention from a phone reply to a physical prop',
  moves: 'The phone falls away to the left and loses focus as the physical prop on the right sharpens. The camera cuts to a tighter continuation, pushes in a little farther, then holds.',
  fixed: 'The prop stays put on the table. The reply and its conversation layout move together with the phone.',
  notice: 'The reply names something that exists outside the phone, and the tighter shot confirms it is the same physical object.',
  fits: 'Use when a readable message identifies a physical object and the next beat needs the audience to recognize that object in the real scene.',
  avoid: 'Moving attention off the phone ends that reading beat. A long reply or text that still drives the next action needs a longer read or a later cut.',
  intents: [
    'The viewer reads a reply naming a prop. The phone falls off the left as attention crosses to a red tin on the right. Cut to a closer continuation on the physical tin. Hold the tin and release attention from the phone.',
    'Read a reply, let the handset leave frame and cut closer to the object it points to.',
    'Transfer attention from a message screen to a real object with a leftward phone exit and a tighter prop shot.',
  ],
  editable: ['heading', 'copy', 'reply', 'title', 'detail', 'action', 'values'],
  defaults: {
    heading: 'From the screen to the prop table', copy: 'Where’s the moon?',
    reply: 'Red tin. Under the stars.', title: 'MOON', action: 'Stage Crew',
    detail: 'Find the object named in the reply.', values: [100],
  },
  editNotes: 'Use copy and reply for the short exchange, action for the contact name, and title for the label on the prop. Replace the vector children inside prop-tin to swap the prop for both shots. The first values item sets departure from 0 (source-like drift and cut with the phone visible) to 100 (full exit before the cut).',
  source,
  build(ctx) {
    const {track, event, stage, content, frameCount, rect} = ctx;
    const {scene, tin} = propTable(ctx);
    const phone = handset(ctx);
    const veil = rect('prop-table-veil', 0, 0, 500, 298, '#170e1a');
    const departure = Math.max(0, Math.min(100, content.values[0])) / 100;
    const onFrame = fraction => Math.ceil(fraction * frameCount - 1e-8) / frameCount;
    const turn = onFrame(.43);
    const release = onFrame(.62);
    const cut = onFrame(.66);
    const hold = onFrame(.82);
    const origin = Array.from({length: 12}, (_, i) => ({
      t: turn + (release - turn) * i / 11,
      ...cluePhase(141 + i),
    }));
    const sourcePixels = 500 / 960;
    const lastDeparture = origin.at(-1).departure;
    const travel = (1 - departure) * 112 * sourcePixels + departure * 275 / lastDeparture;
    const close = Array.from({length: 16}, (_, i) => [
      cut + (hold - cut) * i / 15, 1.52 * (1 + .12 * cluePhase(153 + i).push), i === 0 ? 'hold' : 'linear',
    ]);
    for (const property of ['scaleX', 'scaleY']) {
      track(scene, property, [[0, 1], ...close]);
    }
    track(scene, 'blur', [...origin.map(({t, focus}) => [t, (10 - 7 * focus) * sourcePixels]), [cut, 0, 'hold']]);
    track(veil, 'opacity', [...origin.map(({t, focus}) => [t, .55 - .32 * focus]), [cut, 0, 'hold']]);
    track(phone, 'x', origin.map(({t, departure: p}) => [t, 35 - travel * p]));
    track(phone, 'y', origin.map(({t, departure: p}) => [t, 9 + 16 * sourcePixels * p]));
    track(phone, 'rotation', origin.map(({t, departure: p}) => [t, -6 * p]));
    track(phone, 'blur', origin.map(({t, departure: p}) => [t, 1.9 * sourcePixels * p]));
    track(phone, 'opacity', [[0, 1], [cut, 0, 'hold']]);
    stage.children.push(scene, veil, phone);
    ctx.label(content.detail);
    ctx.setInitialUI({
      conversationId: 'thread.prop-table',
      messages: [
        {id: 'message.question', senderId: 'operator', text: content.copy},
        {id: 'message.reply', senderId: 'stage-crew', text: content.reply},
      ],
      composer: {text: '', focused: false},
      viewport: {surface: 'conversation', anchorMessageId: 'message.reply'},
    });
    event('reply-readable', 0, 'prop-reply', 'edit.read');
    event('phone-releases-attention', turn, phone.id, 'camera.release');
    event('attention-on-prop', release, tin.id, 'edit.focus');
    event('cut-to-prop', cut, tin.id, 'edit.cut', null);
    event('prop-hold-start', hold, tin.id, 'edit.hold');
  },
}];
