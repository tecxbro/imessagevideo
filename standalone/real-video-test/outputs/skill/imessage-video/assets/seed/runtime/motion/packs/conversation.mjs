// Conversation staging uses editable components. Timings are authored unless the
// entry cites a measured window. Native captures are references, not scene assets.
const SOURCE = 'https://github.com/theswerd/imessage-ui/blob/1f132909792ff540501385f91d37ef20629c55b7';

function entry(id, metadata, build) {
  return {
    id,
    source: {kind:'authored', ref:`packs/conversation.mjs#${id}`, range:[0,2.4]},
    ...metadata,
    build,
  };
}

const graphemes = new Intl.Segmenter(undefined,{granularity:'grapheme'});

function textWidth(value) {
  return Array.from(graphemes.segment(value),({segment}) => {
    if (/^[ .,:;!iIl1'’]$/.test(segment)) return 4.8;
    if (/^[MW@&%mw]$/.test(segment)) return 14.4;
    if (/^[A-Z]$/.test(segment)) return 11.7;
    return /^[\u0020-\u024f]$/.test(segment) ? 8.7 : 16;
  }).reduce((sum,width) => sum+width,0);
}

function wrap(value, width, limit = 2) {
  const pending = Array.from(graphemes.segment(value),({segment}) => segment);
  const lines = [];
  while (pending.length && lines.length < limit) {
    let line = '';
    while (pending.length && !pending[0].includes('\n') && textWidth(line+pending[0]) <= width) line += pending.shift();
    if (pending[0]?.includes('\n')) pending.shift();
    else if (pending.length && lines.length < limit-1 && !/^\s$/.test(pending[0])) {
      const space = line.lastIndexOf(' ');
      if (space >= line.length/2) {
        pending.unshift(...Array.from(graphemes.segment(line.slice(space+1)),({segment}) => segment));
        line = line.slice(0,space);
      }
    }
    if (lines.length === limit-1 && pending.some(segment => segment.trim())) {
      const chars = Array.from(graphemes.segment(line.trimEnd()),({segment}) => segment);
      while (textWidth(chars.join('')+'…') > width) chars.pop();
      line = chars.join('')+'…';
    }
    while (pending[0] === ' ') pending.shift();
    lines.push(line.trim());
  }
  return lines;
}

function message(ctx, id, x, y, copy, side = 'incoming', width = 262, height = 54, lineLimit = 2) {
  const lines = wrap(copy,width-32,lineLimit);
  const bubble = ctx.ui.MessageBubble({id,x,y,width,height,side,copy:lines.join('\n'),fontSize:16});
  Object.assign(part(bubble,'copy'),{y:lines.length > 1 ? (height-39)/2 : 14,lineHeight:18});
  return bubble;
}

function composer(ctx, id, y, copy = '', width = 454) {
  return ctx.ui.Composer({id,x:23,y,width,copy:wrap(copy,width-62,1)[0] ?? '',active:Boolean(copy)});
}

const part = (layer, suffix) => layer.children.find(child => child.id === `${layer.id}-${suffix}`);

function clipText(ctx, id, value, x, y, width, size, extra = {}) {
  return ctx.group(id,x,y,[ctx.text(`${id}-copy`,value,0,0,size,extra)],
    {clip:{x:0,y:0,width,height:size*1.6}});
}

function show(ctx, layer, begin, finish = begin) {
  const keys = begin === finish
    ? [[0,0],[begin,1,'hold']]
    : [[0,0],[begin,0],[finish,1,'easeOut']];
  ctx.track(layer,'opacity',keys);
}

function marker(ctx, id, x, y, label) {
  return ctx.group(id,x,y,[
    ctx.rect(`${id}-body`,0,0,126,29,ctx.colors.light,14),
    ctx.text(`${id}-text`,label,63,6,13,{textAnchor:'middle',fill:ctx.colors.muted}),
  ]);
}

function path(id, x, y, d, stroke, strokeWidth = 2) {
  return {id,x,y,d,type:'path',fill:'none',stroke,strokeWidth,lineCap:'round',lineJoin:'round'};
}

function atMilliseconds(ctx, start, milliseconds) {
  return start + milliseconds / 1000 / (ctx.duration ?? 2.4);
}

// The reference gives sampled geometry, so this adaptation interpolates those
// values and leaves the recording and the reference implementation out of the scene.
const SEND_REFERENCE = {
  kind:'measured-adaptation',
  ref:`${SOURCE}/references/ios/motion/send-60fps.mp4`,
  range:[73/60,115/60],
  frames:[73,114],
  note:'Source frames are zero-based. Geometry is fitted to the editable preview layout using the measured collapse ratios, rise and overshoot. Color, text timing outside the flight and resting geometry are adapted.',
};
const LONG_PRESS_REFERENCE = {
  kind:'measured-adaptation',
  ref:`${SOURCE}/references/ios/motion/longpress-60fps.mp4`,
  range:[85/60,115/60],
  frames:[85,114],
  note:'Recorded window covers the selected row, dimming, menu and bar entrance. The source calibration gives a 380 ms menu entrance. Preview artwork, blur treatment and control labels are adapted.',
};

export const entries = [
  entry('composer-type', {
    title:'Type a draft in place',
    moves:'The composer gains characters at uneven intervals as the caret advances.',
    fixed:'The draft field, transcript, heading, and phone viewport are stationary.',
    notice:'A person is building a draft before any message is sent.',
    fits:'Show human input or let the viewer read the prompt as it is typed.',
    avoid:'Typing implies human authorship and input. It misreads a reply that arrives whole.',
    intents:['Let the viewer see a person type the question','Spell out the request in the message field','Type the prompt without sending it'],
    editable:['heading','copy','reply'],
  }, ctx => {
    const draft = composer(ctx,'type-draft',0,'');
    const input = part(draft,'input');
    const visible = Array.from(graphemes.segment(wrap(ctx.content.copy,380,1)[0] ?? ''), token => token.segment);
    const weights = visible.map(character => /[ .,!?]/.test(character) ? 1.8 : 1);
    const total = weights.reduce((sum,weight) => sum+weight,0);
    let elapsed = 0;
    const letters = visible.map((_,index) => {
      elapsed += weights[index];
      return [.13 + .69 * elapsed / total, visible.slice(0,index+1).join(''),'hold'];
    });
    ctx.track(input,'text',[[0,'Message'],...letters]);
    if (letters.length) {
      ctx.track(input,'fill',[[0,ctx.colors.muted],[letters[0][0],ctx.colors.ink,'hold']]);
      ctx.track(part(draft,'send'),'fill',[[0,ctx.colors.light],[letters[0][0],ctx.colors.blue,'hold']]);
      ctx.event('first-character',letters[0][0],input.id,'typing');
      ctx.event('draft-complete',letters.at(-1)[0],input.id,'typing_end');
    }
    const caret = ctx.rect('typing-caret',18,12,2,24,ctx.colors.blue);
    ctx.track(caret,'x',[[0,18],...letters.map(([time,value]) => [time,18+textWidth(value),'hold'])]);
    ctx.track(caret,'opacity',[[0,0],[.12,1,'hold'],[.88,0,'hold'],[.96,1,'hold']]);
    draft.children.push(caret);
    ctx.stage.children.push(message(ctx,'type-prior-message',30,164,ctx.content.reply));
    ctx.footer.children.push(draft);
  }),

  entry('draft-send-flight', {
    title:'Send from the composer into history',
    moves:'The draft box collapses toward its right edge while the outgoing balloon rises, slightly overshoots, then settles into its transcript slot.',
    fixed:'The conversation heading, prior reply, and composer field stay fixed. The send control disappears at the trigger.',
    notice:'The text the viewer just read in the field becomes a real outgoing message.',
    fits:'Establish the exact send moment without cutting away from the conversation.',
    avoid:'A send flight implies committing the draft. Avoid it while composing, reviewing, or receiving a message.',
    intents:['Show the typed draft becoming a sent bubble','Watch the message fly out of the composer','Tap send and turn the input into an outgoing message','Turn the line we typed into a blue message in the conversation'],
    editable:['heading','copy','reply'],
    source:SEND_REFERENCE,
  }, ctx => {
    const start = .19;
    const moment = ms => atMilliseconds(ctx,start,ms);
    const draft = composer(ctx,'send-draft',248,ctx.content.copy);
    const input = part(draft,'input');
    ctx.track(input,'text',[[0,input.text],[start,'Message','hold']]);
    ctx.track(input,'fill',[[0,ctx.colors.ink],[start,ctx.colors.muted,'hold']]);
    for (const suffix of ['send','arrow']) ctx.track(part(draft,suffix),'opacity',[[0,1],[start,0,'hold']]);
    const ghost = ctx.rect('send-field-collapse',24,248,452,47,'#91c5fe',23,{opacity:0});
    const widths = [[0,292.2],[17,294.2],[33,271.6],[50,251.7],[67,225.8],[83,194.7],[100,154],[117,123],[133,98],[150,81.7],[183,67.9]];
    ctx.track(ghost,'width',widths.map(([ms,w]) => [moment(ms),w*452/292.2]));
    ctx.track(ghost,'x',widths.map(([ms,w]) => [moment(ms),476-w*452/292.2]));
    ctx.track(ghost,'opacity',[[0,0],[start,.64,'hold'],[moment(70),.5],[moment(183),0]]);
    const incoming = message(ctx,'send-prior-reply',28,42,ctx.content.reply);
    const outgoing = message(ctx,'send-outgoing',242,248,ctx.content.copy,'outgoing',228,48);
    Object.assign(outgoing,{originX:228,originY:48});
    const y = [[0,248],[33,248],[150,207],[183,186],[233,162],[317,133],[350,128],[417,124],[450,124],[633,128],[690,128]];
    ctx.track(outgoing,'y',y.map(([ms,value]) => [moment(ms),value]));
    const scale = [[33,.5],[70,.7],[150,.87],[183,.772],[260,.91],[360,.98],[500,1],[690,1]];
    for (const axis of ['scaleX','scaleY']) ctx.track(outgoing,axis,scale.map(([ms,value]) => [moment(ms),value]));
    show(ctx,outgoing,moment(33),moment(70));
    ctx.stage.children.push(incoming,draft,ghost,outgoing);
    ctx.event('send',start,outgoing.id,'message_send');
    ctx.event('settle',moment(690),outgoing.id,'message_settle');
  }),

  entry('typing-indicator-cycle', {
    title:'Cycle an incoming typing indicator',
    moves:'Three dots lift and dim in staggered phases inside a stationary bubble.',
    fixed:'The dots’ container, prior outgoing message, composer and heading.',
    notice:'The recipient is working on a reply, with no text to read yet.',
    fits:'A short conversational pause before the other person answers.',
    avoid:'Typing dots imply a participant is composing. A loading job, completed result or explicit delivery state needs its own signal.',
    intents:['Show that the other person is typing','Wait for a reply with three cycling dots','Keep the waiting bubble still while its dots pulse'],
    editable:['heading','copy'],
  }, ctx => {
    const outgoing = message(ctx,'waiting-request',217,65,ctx.content.copy,'outgoing',248);
    const dots = [0,1,2].map(i => {
      const dot = ctx.rect(`waiting-dot-${i}`,22+i*19,19,9,9,ctx.colors.muted,5);
      const turns = [.18,.43,.68].flatMap(start => {
        const phase = start+i*.036;
        return [[phase,19],[phase+.043,12,'easeOut'],[phase+.103,19,'easeIn']];
      });
      ctx.track(dot,'y',[[0,19],...turns]);
      ctx.track(dot,'opacity',[[0,.54],...turns.map(([time,y,ease]) => [time,y === 12 ? 1 : .54,ease])]);
      return dot;
    });
    const indicator = ctx.group('waiting-indicator',30,167,[ctx.rect('waiting-indicator-body',0,0,101,44,ctx.colors.light,21),...dots]);
    show(ctx,indicator,.11,.16);
    ctx.stage.children.push(outgoing,indicator);
    ctx.footer.children.push(composer(ctx,'waiting-composer',0));
    ctx.event('thinking-visible',.11,indicator.id,'typing_indicator');
  }),

  entry('reply-makes-room', {
    title:'Make room for a whole incoming reply',
    moves:'The previous rows lift together. The complete incoming reply rises a shorter distance into the bottom slot.',
    fixed:'The header, composer, and bottom resting line of the transcript.',
    notice:'The other participant has answered and the conversation advances to the latest message.',
    fits:'A reply arrives in an already populated conversation.',
    avoid:'A composer send, timestamp peek, or an answer generated a word at a time reads as a different action.',
    intents:['A reply comes in and nudges previous messages up','Show the whole answer arriving at the bottom','Keep the composer still while a new reply makes room'],
    editable:['heading','copy','reply'],
  }, ctx => {
    const history = ctx.group('arrival-history',0,0,[
      message(ctx,'arrival-prior',30,160,'Can you check for me?'),
      message(ctx,'arrival-outgoing',223,224,ctx.content.copy,'outgoing',244),
    ]);
    const incoming = message(ctx,'arrival-new-reply',30,276,ctx.content.reply);
    ctx.track(history,'y',[[0,0],[.45,0],[.64,-68,'easeOut']]);
    ctx.track(incoming,'y',[[0,276],[.48,276],[.611,222,'easeOut'],[.662,224,'easeInOut']]);
    show(ctx,incoming,.48,.56);
    ctx.stage.children.push(history,incoming);
    ctx.footer.children.push(composer(ctx,'arrival-composer',0));
    ctx.event('reply-arrival',.48,incoming.id,'message_arrival');
  }),

  entry('delivery-receipt-handoff', {
    title:'Move the delivery receipt to the latest send',
    moves:'The old receipt fades under the first bubble. The latest bubble rises toward its final slot as its receipt resolves.',
    fixed:'The first bubble, the composer and the conversation heading.',
    notice:'The delivery status belongs to the latest sent item.',
    fits:'Track where a confirmation label lives after a new outgoing item is acknowledged.',
    avoid:'A delivery confirmation does not establish that the recipient has read the message.',
    intents:['Shift Delivered to the newest message','Show which sent item has the latest delivery receipt','Move the acknowledgment below the second blue bubble'],
    editable:['heading','copy','reply','detail'],
    defaults:{detail:'Delivered'},
    source:{
      kind:'measured-adaptation',ref:`${SOURCE}/references/ios/motion/send-60fps.mp4`,range:[134/60,148/60],frames:[134,147],
      note:'Source f134–147 establishes the 15 pt rise of the newest bubble while the prior bubble stays fixed. Receipt opacity curves and copy are authored.',
    },
  }, ctx => {
    const top = message(ctx,'receipt-first-message',232,113,ctx.content.copy,'outgoing',234,46);
    const lower = message(ctx,'receipt-latest-message',232,204,ctx.content.reply,'outgoing',234,46);
    const oldReceipt = ctx.text('receipt-old-status',ctx.content.detail,466,161,13,{textAnchor:'end',fill:ctx.colors.muted});
    const newReceipt = ctx.text('receipt-new-status',ctx.content.detail,466,249,13,{textAnchor:'end',fill:ctx.colors.muted});
    const trigger = .46;
    const settled = atMilliseconds(ctx,trigger,217);
    ctx.track(oldReceipt,'opacity',[[0,1],[trigger,1],[settled,0,'easeOut']]);
    ctx.track(lower,'y',[[0,204],[trigger,204],[settled,189,'easeOut']]);
    ctx.track(newReceipt,'y',[[0,255],[trigger,255],[settled,238,'easeOut']]);
    show(ctx,newReceipt,trigger,settled);
    ctx.stage.children.push(top,oldReceipt,lower,newReceipt);
    ctx.footer.children.push(composer(ctx,'receipt-composer',0));
    ctx.event('receipt-reassigned',trigger,newReceipt.id,'delivery_status');
  }),

  entry('long-press-actions', {
    title:'Reveal actions around a pressed message',
    moves:'Context dims while the option tray opens below the held row and the reaction rail grows above it.',
    fixed:'The selected message stays centered on its original slot throughout the reveal.',
    notice:'The press selects one message and exposes possible actions.',
    fits:'Introduce options tied to a single message without implying a choice has happened.',
    avoid:'A held menu should not imply a reaction was picked, content was deleted, or the full conversation changed.',
    intents:['Long press one message and show the reaction choices','Open the menu around a bubble without moving it','Dim the chat around one selected message'],
    editable:['heading','copy','reply'],
    source:LONG_PRESS_REFERENCE,
  }, ctx => {
    const trigger = .27;
    const time = ms => atMilliseconds(ctx,trigger,ms);
    const background = message(ctx,'actions-context',28,38,ctx.content.reply);
    const backgroundTwo = message(ctx,'actions-context-two',28,220,'We have time after lunch.');
    const foreground = message(ctx,'actions-selected',217,123,ctx.content.copy,'outgoing',252);
    const scrim = ctx.rect('actions-scrim',0,0,500,298,'#111826',0);
    ctx.track(scrim,'opacity',[[0,0],[trigger,0],[time(150),.29,'easeOut']]);
    const rail = ctx.group('actions-reaction-rail',177,76,[
      ctx.rect('actions-rail-surface',0,0,292,38,'#ffffff',19),
      ...['Love','Like','Laugh','Emphasize'].map((label,i) => ctx.text(`actions-reaction-${i}`,label,16+i*68,11,13,{fill:ctx.colors.ink,fontWeight:600})),
    ],{originX:275,originY:38});
    const menu = ctx.group('actions-context-menu',278,176,[
      ctx.rect('actions-menu-surface',0,0,191,109,'#ffffff',16),
      ...['Copy','Reply','More'].map((label,i) => ctx.text(`actions-option-${i}`,label,15,10+i*34,16)),
    ],{originX:180,originY:0});
    for (const axis of ['scaleX','scaleY']) {
      ctx.track(rail,axis,[[0,.57],[time(100),.57],[time(380),1,'easeOut']]);
      ctx.track(menu,axis,[[0,.8],[trigger,.8],[time(130),1,'easeOut']]);
    }
    show(ctx,rail,time(100),time(170));
    show(ctx,menu,trigger,time(130));
    ctx.stage.children.push(background,backgroundTwo,scrim,foreground,rail,menu);
    ctx.footer.children.push(composer(ctx,'actions-composer',0));
    ctx.event('hold-threshold',trigger,foreground.id,'long_press');
    ctx.event('actions-ready',time(380),rail.id,'menu_open');
  }),

  entry('reaction-attach', {
    title:'Attach a chosen reaction to its message',
    moves:'The selected reaction follows a curved approach, shrinks into a corner badge and settles as the nearby text row makes room.',
    fixed:'Message copy, heading and composer. Earlier messages stay put.',
    notice:'The chosen response belongs to this one message and remains attached after the picker goes away.',
    fits:'Show the result of choosing a reaction once the available choices are understood.',
    avoid:'A reaction overlay on the whole screen reads as celebration or product decoration.',
    intents:['Tap a reaction and pin it to the message corner','Show the chosen emoji landing on one bubble','Apply a reaction and close its options'],
    editable:['heading','copy','reply','action'],
    defaults:{action:'Love'},
  }, ctx => {
    const target = message(ctx,'reaction-target',32,151,ctx.content.copy);
    const older = message(ctx,'reaction-prior',216,41,ctx.content.reply,'outgoing',250);
    const source = ctx.group('reaction-picker',237,83,[
      ctx.rect('reaction-picker-body',0,0,230,42,ctx.colors.light,20),
      ctx.text('reaction-picker-label',ctx.content.action,115,11,16,{textAnchor:'middle'}),
    ]);
    const badge = ctx.group('reaction-badge',350,104,[
      ctx.rect('reaction-badge-body',0,0,92,35,ctx.colors.blue,17),
      ctx.text('reaction-badge-label',ctx.content.action,46,8,15,{textAnchor:'middle',fill:'#ffffff',fontWeight:600}),
      ctx.rect('reaction-badge-mark-one',73,29,9,9,ctx.colors.blue,5),
      ctx.rect('reaction-badge-mark-two',85,37,5,5,ctx.colors.blue,3),
    ],{originX:46,originY:17});
    const decision = .35;
    ctx.track(source,'opacity',[[0,1],[decision,1],[.49,0,'easeOut']]);
    ctx.track(badge,'x',[[0,350],[decision,350],[.51,309,'easeOut'],[.67,227,'easeInOut']]);
    ctx.track(badge,'y',[[0,86],[decision,86],[.5,68,'easeOut'],[.63,134,'easeIn'],[.67,131,'easeOut']]);
    for (const axis of ['scaleX','scaleY']) ctx.track(badge,axis,[[0,1.09],[decision,1.09],[.62,.79,'easeInOut'],[.68,.83,'easeOut']]);
    show(ctx,badge,decision);
    ctx.track(target,'y',[[0,151],[.56,151],[.68,168,'easeOut']]);
    ctx.stage.children.push(older,target,source,badge);
    ctx.footer.children.push(composer(ctx,'reaction-composer',0));
    ctx.event('reaction-choice',decision,badge.id,'reaction_select');
    ctx.event('reaction-attached',.67,target.id,'reaction_attached');
  }),

  entry('transcript-timestamp-peek', {
    title:'Peek at timestamps by dragging the transcript',
    moves:'Every bubble shifts left once and springs back on release, exposing small times in a stationary gutter.',
    fixed:'Times remain on the trailing edge. The heading, composer, and individual vertical positions stay fixed.',
    notice:'These are times for existing messages, revealed by a temporary drag.',
    fits:'Show when multiple parts of an existing conversation occurred.',
    avoid:'This is a transcript-wide left drag. A single selected message moving right signals a reply gesture.',
    intents:['Swipe all the bubbles left to reveal their timestamps','Temporarily slide the transcript off the right time labels','Peek at the sent times without moving the header'],
    editable:['heading','copy','reply','detail'],
    defaults:{detail:'1:26 PM'},
    source:{
      kind:'observed-pose-adaptation',ref:`${SOURCE}/references/ios/captures/swipe-timestamps-light.png`,range:[0,0],
      note:'A still at t=0 establishes the 58 pt displacement and timestamp alignment. Drag and return timing are authored.',
    },
  }, ctx => {
    const positions = [[70,49,ctx.content.copy,'incoming'],[241,125,ctx.content.reply,'outgoing'],[70,201,'That works for me.','incoming']];
    const bubbles = ctx.group('peek-bubble-column',0,0,positions.map(([x,y,copy,side],i) => message(ctx,`peek-message-${i}`,x,y,copy,side,226)));
    ctx.track(bubbles,'x',[[0,0],[.22,0],[.45,-58,'linear'],[.64,-58],[.72,-3,'easeOut'],[.77,0,'easeOut']]);
    const times = ctx.group('peek-time-gutter',0,0,
      positions.map(([,y],i) => ctx.text(`peek-time-${i}`,i === 1 ? ctx.content.detail : [`1:25 PM`,``,`1:28 PM`][i],486,y+19,12,{fill:ctx.colors.muted,textAnchor:'end'})));
    ctx.track(times,'opacity',[[0,0],[.26,0],[.45,1,'easeOut'],[.64,1],[.75,0,'easeIn']]);
    ctx.stage.children.push(times,bubbles);
    ctx.footer.children.push(composer(ctx,'peek-composer',0));
    ctx.event('peek-begin',.22,bubbles.id,'gesture_begin');
    ctx.event('peek-release',.64,bubbles.id,'gesture_end');
  }),

  entry('swipe-to-quote', {
    title:'Swipe one message to quote it',
    moves:'Only the chosen bubble follows the drag. An arrow appears behind it, then the row returns and its quote opens above the composer.',
    fixed:'Other transcript rows, header and reply input position.',
    notice:'The next draft will reply to one specific earlier message.',
    fits:'An answer needs an explicit target in a busy conversation.',
    avoid:'A transcript-wide swipe to reveal timestamps never opens a quoted draft.',
    intents:['Swipe right on one bubble to create a quoted reply','Pull a single message sideways then open its reply draft','Show which earlier message the next answer refers to','Show which message I’m replying to'],
    editable:['heading','copy','reply','title'],
    defaults:{title:'Replying to this message'},
  }, ctx => {
    const earlier = message(ctx,'quote-earlier',210,58,ctx.content.reply,'outgoing',254);
    const target = message(ctx,'quote-message',34,138,ctx.content.copy);
    const arrow = path('quote-gesture-arrow',30,154,'M 20 0 L 7 11 L 20 22 M 8 11 H 31',ctx.colors.blue,3);
    ctx.track(target,'x',[[0,34],[.22,34],[.47,115,'linear'],[.52,123,'easeOut'],[.65,30,'easeOut'],[.72,34,'easeOut']]);
    ctx.track(arrow,'opacity',[[0,0],[.29,0],[.44,1,'easeOut'],[.59,1],[.67,0,'easeIn']]);
    const quote = ctx.group('quote-draft-preview',23,285,[
      ctx.rect('quote-draft-shape',0,0,454,53,ctx.colors.light,14),
      ctx.rect('quote-draft-rule',11,11,3,30,ctx.colors.blue,1),
      ctx.text('quote-draft-label',ctx.content.title,24,7,13,{fontWeight:600,fill:ctx.colors.blue}),
      clipText(ctx,'quote-draft-snippet',ctx.content.copy,24,24,412,15),
    ]);
    ctx.track(quote,'y',[[0,285],[.57,285],[.72,242,'easeOut']]);
    show(ctx,quote,.57,.68);
    ctx.stage.children.push(earlier,arrow,target,quote);
    ctx.footer.children.push(composer(ctx,'quote-composer',0));
    ctx.event('reply-gesture-commit',.48,target.id,'swipe_commit');
    ctx.event('reply-draft-open',.64,quote.id,'reply_compose_open');
  }),

  entry('inline-thread-open', {
    title:'Expand an inline reply thread',
    moves:'A connector grows from the parent while two indented replies emerge in sequence. The next unrelated row moves down.',
    fixed:'The parent message, heading and composer.',
    notice:'Several messages belong under one earlier message, as a readable subthread.',
    fits:'Expose a group of existing inline replies while preserving their parent context.',
    avoid:'A quoted draft is an action the user will take next. It should not unfold a cluster of replies that already exist.',
    intents:['Open an inline chain under a specific message','Unfold the replies under a message and keep the parent still','Show the reply branch without leaving the conversation'],
    editable:['heading','copy','reply','detail'],
    defaults:{detail:'I will leave at noon.'},
  }, ctx => {
    const parent = message(ctx,'thread-parent',30,38,ctx.content.copy);
    const first = message(ctx,'thread-reply-first',80,117,ctx.content.reply,'incoming',275,46);
    const second = message(ctx,'thread-reply-second',137,174,ctx.content.detail,'outgoing',249,46);
    const next = message(ctx,'thread-unrelated',30,111,'One more thing.','incoming',223,46);
    const connector = ctx.rect('thread-connector',49,96,3,2,ctx.colors.muted,1);
    ctx.track(connector,'height',[[0,2],[.31,2],[.66,106,'easeOut']]);
    ctx.track(next,'y',[[0,111],[.31,111],[.687,234,'easeOut']]);
    ctx.track(first,'y',[[0,102],[.38,102],[.58,117,'easeOut']]);
    ctx.track(second,'y',[[0,141],[.52,141],[.7,174,'easeOut']]);
    show(ctx,first,.39,.56);
    show(ctx,second,.56,.69);
    ctx.stage.children.push(connector,parent,next,first,second);
    ctx.footer.children.push(composer(ctx,'thread-composer',0));
    ctx.event('thread-expand',.31,parent.id,'thread_open');
    ctx.event('thread-readable',.7,second.id,'thread_ready');
  }),

  entry('edit-message-reflow', {
    title:'Edit a message at its existing position',
    moves:'The original bubble deepens to fit an editable second line. Nearby content reflows and the edit marker appears on commit.',
    fixed:'The same message retains its identity and leading row. The header and main composer do not move.',
    notice:'A previously sent message changes in place and keeps its row in the conversation.',
    fits:'Correct existing text while preserving the surrounding conversation.',
    avoid:'Do not show an edit by sending a second message or deleting the original row.',
    intents:['Correct the existing message instead of sending another','Edit one bubble in place and keep its position in the chat','Expand the bubble to fit the corrected line'],
    editable:['heading','copy','reply','detail'],
    defaults:{copy:'Meet at the station.',detail:'By the north entrance.'},
  }, ctx => {
    const original = message(ctx,'edit-original',221,64,ctx.content.copy,'outgoing',240,51,1);
    const corrected = part(original,'copy');
    const body = part(original,'body');
    const tail = part(original,'tail');
    const next = message(ctx,'edit-later-message',29,142,ctx.content.reply);
    const status = ctx.text('edit-status','Edited',461,122,12,{fill:ctx.colors.muted,textAnchor:'end'});
    const field = clipText(ctx,'edit-line-insert',ctx.content.detail,17,36,202,16,{fill:'#ffffff'});
    original.children.push(field);
    ctx.track(body,'height',[[0,51],[.27,51],[.49,78,'easeOut']]);
    ctx.track(tail,'y',[[0,0],[.27,0],[.49,27,'easeOut']]);
    ctx.track(next,'y',[[0,142],[.27,142],[.49,169,'easeOut']]);
    ctx.track(status,'y',[[0,122],[.27,122],[.49,145,'easeOut']]);
    ctx.track(corrected,'opacity',[[0,1],[.27,1],[.42,.71,'easeOut'],[.61,1,'easeOut']]);
    show(ctx,field,.34,.47);
    show(ctx,status,.64,.75);
    ctx.stage.children.push(original,status,next);
    ctx.footer.children.push(composer(ctx,'edit-composer',0));
    ctx.event('edit-begin',.27,original.id,'edit_open');
    ctx.event('edit-commit',.64,original.id,'edit_commit');
  }),

  entry('undo-send-remove', {
    title:'Undo a send and retract its row',
    moves:'The outgoing bubble contracts toward its own tail and fades. Nearby rows close the gap, then a quiet history status appears.',
    fixed:'The header, composer and surviving messages’ copy.',
    notice:'One previously sent message was retracted from the conversation.',
    fits:'Show that a mistaken send was undone and what remains afterward.',
    avoid:'This removal changes history. It is different from canceling an unsent draft or merely hiding one row for yourself.',
    intents:['Take back a message that was already sent','Undo send and close the resulting gap','Retract the outgoing bubble from the transcript'],
    editable:['heading','copy','reply'],
  }, ctx => {
    const prior = message(ctx,'undo-prior',29,113,ctx.content.reply);
    const outgoing = message(ctx,'undo-outgoing',223,193,ctx.content.copy,'outgoing',244);
    Object.assign(outgoing,{originX:241,originY:47});
    ctx.track(outgoing,'scaleX',[[0,1],[.36,1],[.43,1.035,'easeOut'],[.57,.065,'easeIn']]);
    ctx.track(outgoing,'scaleY',[[0,1],[.42,1],[.57,.48,'easeIn']]);
    ctx.track(outgoing,'opacity',[[0,1],[.44,1],[.57,0,'easeIn']]);
    ctx.track(prior,'y',[[0,113],[.48,113],[.68,164,'easeOut']]);
    const notice = ctx.text('undo-history-note','You unsent a message',250,237,13,{textAnchor:'middle',fill:ctx.colors.muted});
    show(ctx,notice,.62,.74);
    ctx.stage.children.push(prior,outgoing,notice);
    ctx.footer.children.push(composer(ctx,'undo-composer',0));
    ctx.event('undo-send',.36,outgoing.id,'unsend');
    ctx.event('row-removed',.57,outgoing.id,'message_removed');
  }),

  entry('history-prepend-anchor', {
    title:'Load older messages without losing the reading position',
    moves:'History appears above the visible rows. The rows stay put through insertion and then follow the next drag together.',
    fixed:'The currently read bubble stays at the same position during insertion. The heading and composer remain fixed throughout.',
    notice:'Earlier history became available while the current reading position was preserved.',
    fits:'Demonstrate pagination or a chat-history fetch while keeping the viewer oriented.',
    avoid:'Jumping to unread content deliberately changes the reading position and requires a destination marker.',
    intents:['Load older messages above the current one without jumping','Insert earlier chat history while anchoring where I am reading','Prepend older items and preserve the scroll position'],
    editable:['heading','copy','reply','detail'],
    defaults:{detail:'Yesterday'},
  }, ctx => {
    const old = ctx.group('prepend-older-page',0,0,[
      marker(ctx,'prepend-previous-day',187,-114,ctx.content.detail),
      message(ctx,'prepend-old-bubble',216,-69,ctx.content.reply,'outgoing',250),
    ]);
    show(ctx,old,.39);
    const current = message(ctx,'prepend-anchor-message',30,60,ctx.content.copy);
    const younger = message(ctx,'prepend-younger-message',225,145,'That was helpful.','outgoing',237);
    const viewport = ctx.group('prepend-transcript',0,0,[old,current,younger]);
    ctx.track(viewport,'y',[[0,0],[.53,0],[.82,127,'easeOut']]);
    const wait = marker(ctx,'prepend-loading-indicator',187,12,'Loading earlier…');
    ctx.track(wait,'opacity',[[0,0],[.12,0],[.21,1,'easeOut'],[.36,1],[.43,0,'easeIn']]);
    ctx.stage.children.push(viewport,wait);
    ctx.footer.children.push(composer(ctx,'prepend-composer',0));
    ctx.event('history-inserted',.39,old.id,'history_prepend');
    ctx.event('history-reveal-drag',.53,viewport.id,'gesture_begin');
  }),

  entry('jump-to-unread', {
    title:'Jump to the first unread message',
    moves:'A single controlled scroll advances past intervening rows. The unread divider comes to rest at a predictable spot and the jump control clears.',
    fixed:'The reading frame, composer and header stay anchored while the transcript travels.',
    notice:'The destination is the beginning of unread content.',
    fits:'Skip past older chat history and land on a marked new starting point.',
    avoid:'Quietly fetching an earlier page should preserve the reading position and use a different move.',
    intents:['Press jump and land on the first unread message','Scroll straight to the unread divider','Move through the chat to the new replies and stop on the marker'],
    editable:['heading','copy','reply','detail'],
    defaults:{detail:'Unread messages'},
  }, ctx => {
    const markerRow = ctx.group('unread-destination',0,406,[
      ctx.rect('unread-left-rule',30,13,145,2,ctx.colors.blue,1),
      ctx.text('unread-divider-label',ctx.content.detail,250,2,15,{textAnchor:'middle',fill:ctx.colors.blue,fontWeight:600}),
      ctx.rect('unread-right-rule',325,13,145,2,ctx.colors.blue,1),
    ]);
    const transcript = ctx.group('unread-transcript',0,0,[
      message(ctx,'unread-known-message',218,52,ctx.content.copy,'outgoing',246),
      message(ctx,'unread-prior-answer',30,140,'Okay, one minute.'),
      message(ctx,'unread-crossing-message',220,273,'I will check again.','outgoing',242),
      markerRow,
      message(ctx,'unread-first-new',30,461,ctx.content.reply),
      message(ctx,'unread-second-new',30,535,'The details are here.'),
    ]);
    const control = marker(ctx,'unread-jump-control',342,253,'Jump to unread');
    ctx.track(transcript,'y',[[0,0],[.29,0],[.58,-353,'easeInOut'],[.72,-355,'easeOut']]);
    ctx.track(control,'opacity',[[0,1],[.29,1],[.41,0,'easeIn']]);
    ctx.stage.children.push(transcript,control);
    ctx.footer.children.push(composer(ctx,'unread-composer',0));
    ctx.event('unread-jump',.29,control.id,'tap');
    ctx.event('unread-destination',.72,markerRow.id,'scroll_settle');
  }),

  entry('keyboard-focus-reflow', {
    title:'Focus the composer and open keyboard space',
    moves:'The keyboard pushes up from below, lifting the composer and the last message to keep both reachable.',
    fixed:'The conversation header and textarea contents. No characters are entered.',
    notice:'The conversation moved into text-entry mode while preserving the latest message.',
    fits:'Show how a reply starts and where the user will type next.',
    avoid:'A keyboard rise should not be used as a visual synonym for typing or for sending a message.',
    intents:['Tap the composer to bring up the keyboard','Lift the input field with the keyboard while the header stays fixed','Focus the message box without entering characters'],
    editable:['heading','copy','reply'],
    defaults:{copy:''},
  }, ctx => {
    const last = message(ctx,'focus-last-message',30,198,ctx.content.reply);
    const draft = composer(ctx,'focus-composer',0,ctx.content.copy);
    const keyRows = ['QWERTYUIOP','ASDFGHJKL','ZXCVBNM'];
    const keys = keyRows.flatMap((row,y) => Array.from(row,(letter,x) => {
      const gutter = (500 - row.length * 46) / 2;
      const id = `focus-key-${letter.toLowerCase()}`;
      return ctx.group(id,gutter+x*46,15+y*38,[
        ctx.rect(`${id}-body`,0,0,38,33,'#ffffff',5),
        ctx.text(`${id}-text`,letter,19,8,14,{textAnchor:'middle'}),
      ]);
    }));
    const keyboard = ctx.group('focus-keyboard',0,298,[ctx.rect('focus-keyboard-body',0,0,500,152,'#dfe4eb',0),...keys,
      ctx.rect('focus-keyboard-space',120,130,260,19,'#ffffff',7)]);
    ctx.track(last,'y',[[0,198],[.34,198],[.6,37,'easeOut']]);
    ctx.track(keyboard,'y',[[0,298],[.34,298],[.6,147,'easeOut']]);
    ctx.track(ctx.footer,'y',[[0,396],[.34,396],[.6,197,'easeOut']]);
    ctx.stage.children.push(last,keyboard);
    ctx.footer.children.push(draft);
    ctx.event('composer-focus',.34,draft.id,'tap');
    ctx.event('keyboard-ready',.6,keyboard.id,'keyboard_show');
  }),

  entry('link-preview-upgrade', {
    title:'Upgrade a plain link into an inline preview',
    moves:'The link card extends horizontally and the source metadata slides in behind a clipping boundary.',
    fixed:'The URL, message row height, adjacent reply, heading and composer.',
    notice:'The shared link gained a richer preview alongside its original address.',
    fits:'Play an inline metadata fetch or introduce information contained in an already shared link.',
    avoid:'Opening this box is not navigation to the destination or a second message send.',
    intents:['Turn a pasted URL into a rich link card inside the bubble','Load a preview next to the shared link','Show the metadata expanding without leaving chat'],
    editable:['heading','copy','reply','title','detail'],
    defaults:{copy:'https://example.com/map',title:'Trail map',detail:'Maps and access notes'},
  }, ctx => {
    const card = ctx.rect('link-preview-surface',28,80,207,66,ctx.colors.light,15);
    const below = message(ctx,'link-below',30,172,ctx.content.reply,'incoming',288,46);
    const link = clipText(ctx,'link-address',ctx.content.copy,45,103,181,15,{fill:ctx.colors.blue});
    const preview = ctx.group('link-metadata',-225,0,[
      ctx.rect('link-metadata-thumbnail',0,1,43,43,ctx.colors.blue,8),
      path('link-chain-glyph',10,10,'M 0 17 L 15 2 Q 20 -2 24 2 Q 28 6 24 10 L 10 25 M 4 11 L 0 15 Q -4 19 0 23 Q 4 27 8 23 L 12 19','#ffffff',2.5),
      clipText(ctx,'link-title',ctx.content.title,54,1,158,17,{fontWeight:600}),
      clipText(ctx,'link-detail',ctx.content.detail,54,23,158,13,{fill:ctx.colors.muted}),
    ]);
    const window = ctx.group('link-metadata-window',241,91,[preview],
      {clip:{x:0,y:0,width:223,height:46}});
    const rule = ctx.rect('link-preview-rule',231,96,1,34,ctx.colors.line,0);
    ctx.track(card,'width',[[0,207],[.35,207],[.69,444,'easeOut']]);
    ctx.track(preview,'x',[[0,-225],[.42,-225],[.69,0,'easeOut']]);
    show(ctx,rule,.41,.59);
    ctx.stage.children.push(card,link,window,rule,below);
    ctx.footer.children.push(composer(ctx,'link-composer',0));
    ctx.event('preview-metadata-ready',.45,preview.id,'link_preview');
  }),

  entry('send-failure-retry', {
    title:'Signal a failed send and reveal retry',
    moves:'One outgoing bubble gives a short damped shake. The retry control and failure status then appear beside and below it.',
    fixed:'Existing conversation rows, recipient, heading and composer.',
    notice:'The message exists locally and delivery failed. The viewer can retry it.',
    fits:'Demonstrate the recoverable failed-send state.',
    avoid:'A failure signal should not shake the whole screen or confirm that the message arrived.',
    intents:['Show a failed message and give it a retry button','Shake one undelivered bubble and show what went wrong','The send fails, but the chat stays put'],
    editable:['heading','copy','reply','action'],
    defaults:{action:'Not Delivered'},
  }, ctx => {
    const previous = message(ctx,'failed-send-context',30,74,ctx.content.reply);
    const failure = message(ctx,'failed-outgoing',193,153,ctx.content.copy,'outgoing',240);
    const retry = ctx.group('failed-retry-control',440,161,[
      ctx.rect('failed-retry-ring',0,0,33,33,ctx.colors.paper,16,{stroke:ctx.colors.red,strokeWidth:2}),
      ctx.text('failed-retry-symbol','!',17,4,19,{textAnchor:'middle',fontWeight:600,fill:ctx.colors.red}),
    ]);
    const status = ctx.text('failed-status',ctx.content.action,435,210,14,{textAnchor:'end',fill:ctx.colors.red});
    ctx.track(failure,'x',[[0,193],[.41,193],[.438,181,'easeOut'],[.466,204,'easeInOut'],[.495,186,'easeInOut'],[.522,197,'easeInOut'],[.57,193,'easeOut']]);
    show(ctx,retry,.48,.57);
    show(ctx,status,.53,.67);
    ctx.stage.children.push(previous,failure,retry,status);
    ctx.footer.children.push(composer(ctx,'failed-composer',0));
    ctx.event('delivery-failed',.41,failure.id,'delivery_error');
    ctx.event('retry-ready',.57,retry.id,'retry_ready');
  }),

  entry('schedule-send-wheel', {
    title:'Set a future send time without sending yet',
    moves:'A time wheel rolls behind a fixed selection band. The selected time persists in a small schedule chip as the wheel closes.',
    fixed:'Selection band, draft copy and conversation history.',
    notice:'The message will be sent later, at the time displayed on the chip.',
    fits:'Make the distinction between choosing a send time and executing a send visible.',
    avoid:'Do not use a send flight if this message stays in the draft area after scheduling.',
    intents:['Roll the time picker and schedule this draft for later','Choose a future send time, preserve the draft, and show the schedule','Set send later without sending now'],
    editable:['heading','copy','reply','detail'],
    defaults:{detail:'7:45 PM'},
  }, ctx => {
    const prior = message(ctx,'schedule-prior',29,55,ctx.content.reply);
    const band = ctx.rect('schedule-band',13,66,328,31,'#e3efff',9);
    const wheelValues = ['7:00 PM','7:15 PM','7:30 PM',ctx.content.detail,'8:00 PM'];
    const wheel = ctx.group('schedule-wheel',0,0,wheelValues.map((label,i) =>
      ctx.text(`schedule-wheel-value-${i}`,label,178,39+i*31,17,{textAnchor:'middle',fill:i === 3 ? ctx.colors.ink : ctx.colors.muted})));
    const wheelWindow = ctx.group('schedule-wheel-window',0,0,[wheel],{clip:{x:0,y:34,width:354,height:88}});
    const sheet = ctx.group('schedule-time-picker',73,150,[
      ctx.rect('schedule-sheet-surface',0,0,354,133,'#f0f3f8',18),
      ctx.text('schedule-sheet-title','Send later',177,8,15,{textAnchor:'middle',fontWeight:600}),
      band,wheelWindow,
    ]);
    ctx.track(wheel,'y',[[0,0],[.25,0],[.49,-65,'easeOut'],[.54,-62,'easeOut']]);
    ctx.track(sheet,'opacity',[[0,1],[.68,1],[.82,0,'easeIn']]);
    const chip = marker(ctx,'schedule-confirmed-chip',187,224,ctx.content.detail);
    ctx.track(chip,'y',[[0,224],[.69,224],[.82,257,'easeOut']]);
    show(ctx,chip,.68,.79);
    ctx.stage.children.push(prior,sheet,chip);
    ctx.footer.children.push(composer(ctx,'schedule-draft',0,ctx.content.copy));
    ctx.event('time-wheel-start',.25,wheel.id,'picker_scroll');
    ctx.event('schedule-committed',.68,chip.id,'send_scheduled');
  }),

  entry('batch-select-messages', {
    title:'Select messages for one batch action',
    moves:'The transcript shifts to make room for a check rail. Two rows gain checks separately, then an action bar replaces the composer.',
    fixed:'Header, transcript order, and each message’s text.',
    notice:'Two particular rows are selected for a later shared action.',
    fits:'Show deliberate selection across several messages before forwarding or deleting them.',
    avoid:'Showing the batch controls does not imply the action was executed or affected every row.',
    intents:['Select two messages and expose the batch toolbar','Reveal checkboxes and mark a pair of bubbles','Show how to select multiple messages before forwarding'],
    editable:['heading','copy','reply','action'],
    defaults:{action:'Forward'},
  }, ctx => {
    const rowY = [47,124,201];
    const rows = ctx.group('batch-transcript',0,0,[
      message(ctx,'batch-row-one',28,rowY[0],ctx.content.copy,'incoming',256),
      message(ctx,'batch-row-two',181,rowY[1],ctx.content.reply,'outgoing',251),
      message(ctx,'batch-row-three',28,rowY[2],'We are set for tomorrow.','incoming',256),
    ]);
    ctx.track(rows,'x',[[0,0],[.19,0],[.39,38,'easeOut']]);
    const blanks = rowY.map((y,i) =>
      ctx.rect(`batch-row-check-${i}`,20,y+16,21,21,ctx.colors.paper,11,{stroke:ctx.colors.muted,strokeWidth:1.5}));
    const rail = ctx.group('batch-selection-rail',0,0,blanks);
    show(ctx,rail,.19,.36);
    const marks = rowY.slice(0,2).map((y,i) => {
      const selected = ctx.group(`batch-selected-${i}`,20,y+16,[
        ctx.rect(`batch-selected-fill-${i}`,0,0,21,21,ctx.colors.blue,11),
        path(`batch-selected-check-${i}`,0,0,'M 5 10 L 9 14 L 16 7','#ffffff',2),
      ]);
      show(ctx,selected,.43+i*.19,.48+i*.19);
      return selected;
    });
    const draft = composer(ctx,'batch-composer',0);
    ctx.track(draft,'opacity',[[0,1],[.43,1],[.58,0,'easeOut']]);
    const count = ctx.text('batch-selection-count','1 selected',0,0,15,{fill:ctx.colors.muted});
    const toolbar = ctx.group('batch-toolbar',23,12,[
      count,
      ctx.text('batch-toolbar-action',ctx.content.action,454,0,16,{textAnchor:'end',fill:ctx.colors.blue,fontWeight:600}),
    ]);
    ctx.track(count,'text',[[0,'1 selected'],[.62,'2 selected','hold']]);
    show(ctx,toolbar,.47,.61);
    ctx.stage.children.push(rows,rail,...marks);
    ctx.footer.children.push(draft,toolbar);
    ctx.event('selection-mode',.19,rail.id,'selection_open');
    ctx.event('selection-first',.43,marks[0].id,'select');
    ctx.event('selection-second',.62,marks[1].id,'select');
  }),

  entry('pin-conversation-avatar', {
    title:'Promote a conversation into the pinned tray',
    moves:'The avatar follows a short arc from its row into the pinned tray. Its old row collapses and lower rows slide up.',
    fixed:'The inbox header, the pin lane, and other conversations’ names and preview copy.',
    notice:'The same conversation is now reachable from the pinned area.',
    fits:'Show a conversation being promoted within the inbox.',
    avoid:'Pinning retains the conversation. It should not look like archiving, deleting or opening it.',
    intents:['Move this conversation from the inbox into pinned chats','Pin a conversation so its avatar travels to the top tray','Promote one chat and fill the list gap it leaves'],
    editable:['heading','copy','reply','title'],
    defaults:{heading:'Messages',title:'Trail crew'},
  }, ctx => {
    const tray = ctx.rect('pin-tray',25,16,450,84,ctx.colors.light,15);
    const label = ctx.text('pin-tray-label','Pinned',41,46,15,{fill:ctx.colors.muted});
    const selected = ctx.group('pin-original-row',0,114,[
      ctx.rect('pin-selected-row-surface',26,0,448,54,'#deeeff',11),
      ctx.text('pin-selected-row-title',ctx.content.title,94,6,16,{fontWeight:600}),
      clipText(ctx,'pin-selected-row-summary',ctx.content.copy,94,27,345,13,{fill:ctx.colors.muted}),
    ]);
    const rest = ctx.group('pin-unmoved-conversations',0,176,[
      ctx.rect('pin-row-two-avatar',37,8,36,36,'#dae9df',18),
      ctx.text('pin-row-two-title','Weekend plans',94,7,16,{fontWeight:600}),
      clipText(ctx,'pin-row-two-summary',ctx.content.reply,94,28,345,13,{fill:ctx.colors.muted}),
      ctx.rect('pin-row-three-avatar',37,66,36,36,'#e5e0f2',18),
      ctx.text('pin-row-three-title','Project notes',94,65,16,{fontWeight:600}),
      ctx.text('pin-row-three-summary','The updated notes are ready.',94,86,13,{fill:ctx.colors.muted}),
    ]);
    const avatar = ctx.group('pin-traveling-avatar',37,122,[
      ctx.rect('pin-traveling-avatar-background',0,0,38,38,ctx.colors.blue,19),
      ctx.text('pin-traveling-avatar-initial',Array.from(ctx.content.title.toUpperCase())[0] ?? 'A',19,8,17,{textAnchor:'middle',fill:'#ffffff',fontWeight:600}),
    ],{originX:19,originY:19});
    const pinnedTitle = ctx.text('pin-final-title',ctx.content.title,268,74,12,{textAnchor:'middle'});
    ctx.track(selected,'opacity',[[0,1],[.35,1],[.56,0,'easeOut']]);
    ctx.track(rest,'y',[[0,176],[.42,176],[.68,115,'easeInOut']]);
    ctx.track(avatar,'x',[[0,37],[.35,37],[.51,160,'easeOut'],[.69,249,'easeOut']]);
    ctx.track(avatar,'y',[[0,122],[.35,122],[.56,26,'easeOut'],[.69,29,'easeOut']]);
    show(ctx,pinnedTitle,.62,.74);
    ctx.stage.children.push(tray,label,selected,rest,avatar,pinnedTitle);
    ctx.event('pin-chat',.35,selected.id,'conversation_pin');
    ctx.event('pin-arrival',.69,avatar.id,'pin_settle');
  }),
];
