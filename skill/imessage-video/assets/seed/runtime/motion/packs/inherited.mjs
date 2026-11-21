import {buildMotion as baseMotion} from '../../director/motions.mjs';

const base = 'skill/imessage-motion-recreation/director/motions.mjs';
const baseProvenance = id => ({
  kind: 'authored-adaptation',
  ref: `${base}#${id}`,
  range: [0, 4],
  note: 'Original editable motion starter at c49482a, fit into the library stage with the same keyframe choreography.',
});

function baseEntry(id, title, moves, fixed, notice, fits, avoid, intents, editable, landmarks) {
  return {
    id, title, moves, fixed, notice, fits, avoid, intents, editable,
    source: baseProvenance(id),
    build(ctx) {
      const {scene} = baseMotion(id, {
        title: ctx.content.title, copy: ctx.content.copy, duration: 4, fps: ctx.fps,
      });
      const retime = layer => {
        for (const track of Object.values(layer.keyframes ?? {}))
          for (const key of track) key.t *= ctx.duration / 4;
        for (const child of layer.children ?? []) retime(child);
      };
      scene.layers.forEach(retime);
      ctx.stage.children.push(ctx.group('base-motion', 0, 8, scene.layers, {scaleX: .52, scaleY: .52}));
      ctx.label(ctx.content.detail);
      for (const [name, fraction, target] of landmarks)
        ctx.event(name, fraction, target);
    },
  };
}

const clip = (width, height, radius = 0) => ({x: 0, y: 0, width, height, radius});
const ease = 'easeOut';
const leave = 'easeIn';
const sheetCurve = [879, 640, 482, 374, 294, 232, 183, 144, 113, 89, 69, 54, 43, 36, 31, 29, 30, 31, 33, 34, 35, 36, 36, 37, 38, 38, 39];
const centeredCopy = [[1, 1], [7, .94], [13, .73], [17, .65], [21, .61], [27, .58], [37, .56], [49, .56]];

function film(projectId, range, framesInclusive, note) {
  const project = projectId === '03-photon-mini' ? '03-photon-mini-complete-v1' : '06-gallery-complete-v1';
  return {
    kind: 'measured-adaptation',
    ref: `projects/${project}/imessage-recreations/references/${projectId}/source.mp4`,
    range, framesInclusive, note,
  };
}

const authored = id => ({kind:'authored', ref:`packs/inherited.mjs#${id}`, range:[0,2.4]});

function attachmentStack(ctx) {
  const {group, rect, text, image, content, colors, track, stage, event} = ctx;
  const width = 272, height = 174;
  const swipes = content.swipes ?? 1;
  if (swipes >= content.photos.length) throw Error('Supply at least one more photo than swipes');
  const resting = rank => ({x:104 + rank * 16, y:60 - rank * 8, rotation:rank * -4, scale:1-rank*.042});
  const exit = {x:-288,y:88,rotation:-15,scale:1};
  const window = i => {
    const start = .27 + i * .53 / swipes;
    return [start, start + .13 / swipes, start + .50 / swipes];
  };
  const cards = Array.from({length:content.photos.length}, (_, index) => {
    const id = `attachment-${index + 1}`, first = resting(index);
    const poses = [[0,first,'linear']];
    for (let swipe=0;swipe<swipes && swipe<=index;swipe++) {
      const [start,pickup,finish] = window(swipe);
      const rank = index - swipe;
      const rest = resting(rank);
      poses.push([rank ? pickup : start,rest,'hold'],[finish,rank ? resting(rank-1) : exit,rank ? ease : leave]);
    }
    const card = group(id,first.x,first.y,[
      rect(`${id}-rim`,0,0,width,height,colors.paper,13,{shadow:{x:0,y:3,blur:8,color:'#8290a1'}}),
      group(`${id}-clip`,5,5,[image(`${id}-image`,0,0,width-10,height-10,{photo:index})],
        {clip:clip(width-10,height-10,9)}),
    ],{originX:width/2,originY:height/2,rotation:first.rotation,scaleX:first.scale,scaleY:first.scale});
    for (const property of ['x','y','rotation','scaleX','scaleY']) {
      const key = property.startsWith('scale') ? 'scale' : property;
      track(card,property,poses.map(([time,pose,easing])=>[time,pose[key],easing]));
    }
    return card;
  });
  stage.children.push(text('stack-copy',content.copy,22,11,15),...cards.toReversed(),
    text('stack-count',`${cards.length} attachments`,105,255,15,{fill:colors.muted}));
  const composer = ctx.ui.Composer({id:'stack-composer',x:24,y:1,width:450,active:false});
  composer.scaleY = .76;
  ctx.footer.children.push(composer);
  for(let i=0;i<swipes;i++) {
    const [start,,finish] = window(i);
    const suffix = i ? '-2' : '';
    event('swipe'+suffix, start+1/ctx.frameCount, cards[i].id,'media.swipe');
    event('promoted'+suffix,finish,cards[i+1].id,'media.promote');
  }
}

function riseSheet(ctx) {
  const {stage, group, rect, text, colors, image, content, track, event} = ctx;
  const preview = ctx.ui.MessageBubble({id:'existing-message',x:25,y:16,width:300,height:42,copy:content.copy,side:'incoming',fontSize:15});
  const card = group('inline-preview', 38, 80, [
    rect('preview-material', 0, 0, 266, 170, colors.light, 18),
    image('preview-art', 12, 12, 242, 110),
    text('preview-title', content.title, 12, 130, 21, {fontWeight: 700}),
  ]);
  const scrim = rect('sheet-scrim', 0, 0, 500, 298, '#132333', 0, {opacity: 0});
  track(scrim, 'opacity', [[0,0],[.28,0],[.44,.42,ease]]);
  const sheet = group('detail-sheet', 0, 298, [
    rect('sheet-surface', 0, 0, 500, 305, colors.paper, 24),
    rect('sheet-grabber', 224, 10, 52, 5, '#9aa9ba', 2.5),
    text('sheet-title', content.title, 26, 33, 25, {fontWeight: 700}),
    text('sheet-detail', content.detail, 27, 66, 16, {fill: colors.muted}),
    image('sheet-art', 26, 95, 448, 92),
    ctx.ui.ActionButton({id:'sheet-action', x:26, y:195, width:448, copy:content.action}),
  ]);
  track(sheet, 'y', [[0, 298], [.30, 298], ...sheetCurve.map((y, i) => [
    .32 + .44 * i / (sheetCurve.length - 1), 48 + (y - 39) * 250 / (1080 - 39),
  ])]);
  stage.children.push(preview, card, scrim, sheet);
  event('sheet-enter', .32, sheet.id, 'panel.open');
  event('sheet-settle', .76, sheet.id, 'panel.settle');
}

function gatherPortraits(ctx) {
  const {stage, group, rect, text, colors, image, content, track, event} = ctx;
  stage.children.push(rect('portrait-dark-field', 0, 0, 500, 298, '#253843'));
  const heading = group('anchored-copy', 250, 149, [
    text('centered-title', content.title, 0, -42, 42, {fill: '#f4f6f7', textAnchor: 'middle', fontWeight: 700}),
    text('centered-detail', content.detail, 0, 10, 22, {fill: '#bddae5', textAnchor: 'middle'}),
  ]);
  for (const prop of ['scaleX','scaleY'])
    track(heading, prop, centeredCopy.map(([offset, value]) => [.21 + .53 * offset / 49, value]));
  const routes = [
    [-76,-72,112,48,42,25], [251,-145,268,39,214,17], [507,-31,402,83,398,42],
    [522,335,387,194,365,204], [-112,340,140,190,56,225],
  ];
  const portraits = routes.map(([x,y,mx,my,ex,ey], i) => {
    const id = `portrait-${i + 1}`, arrival = .13 + i % 3 * .035;
    const node = group(id, x, y, [
      rect(`${id}-matte`, 0, 0, 88, 88, colors.paper, 44),
      group(`${id}-aperture`, 4, 4, [image(`${id}-photo`, 0, 0, 80, 80, {photo:i})], {clip:clip(80,80,40)}),
    ], {originX: 44, originY: 44});
    track(node,'x',[[arrival,x],[.53,mx,ease],[.79,ex,ease]]);
    track(node,'y',[[arrival,y],[.53,my,ease],[.79,ey,ease]]);
    track(node,'opacity',[[0,0],[arrival,0],[arrival+.14,1]]);
    track(node,'blur',[[arrival,12],[.49,3],[.79,0,ease]]);
    for (const prop of ['scaleX','scaleY']) track(node,prop,[[arrival,1.88],[.53,1.09,ease],[.79,1,ease]]);
    return node;
  });
  stage.children.push(heading, ...portraits);
  event('converge', .23, heading.id, 'layout.assembly');
  event('settled', .79, portraits[4].id, 'layout.settle');
}

export const entries = [
  baseEntry('message-wall','Bring a wall of messages into view',
    'Conversation tiles enter in a stagger while a common camera glides through the wall.',
    'The cells retain their columns; the layout order and each message identity stay readable.',
    'Independent examples accumulate into breadth.',
    'Show that a product works across distinct conversations or cases.',
    'A single thread with new messages needs sender and timing continuity.',
    ['Sweep through a wall of messages to show breadth','Stagger several conversations into a message grid'],
    ['copy','detail'], [['wall-settles',.71,'wall-message-8']]),
  {...baseEntry('app-drawer','Raise the app drawer as one clipped sheet',
    'The drawer carries a handle and icons upward together from offscreen.',
    'The phone header and underlying message remain in place.',
    'The app choices live in a single drawer within the conversation.',
    'Reveal where to find a set of tools or integrations.',
    'Opening an individual card into its own content is not a picker.',
    ['Pull up the app drawer to show available tools','Reveal the iMessage apps in a sheet from the bottom'],
    ['detail'], [['drawer-open',.42,'drawer']]), variantOf:'inline-card-expand'},
  baseEntry('identity-morph','Morph an identity into an app tile',
    'The surface changes radius, size, and color while two distinct marks exchange at its center.',
    'The central identity anchor and background plane hold.',
    'The viewer reads the new mark as the same product in a new form.',
    'Introduce an app icon as another expression of an existing identity.',
    'When the icon is unrelated to the prior mark, a hard identity change reads more clearly.',
    ['Turn the circular logo into a rounded square app icon','Morph the brand identity into an app tile'],
    ['detail'], [['identity-resolved',.60,'identity-new-mark']]),
  baseEntry('circle-to-panel','Grow a small control into a working surface',
    'One circle widens into a panel while the corner radius changes; contents appear after the surface has room.',
    'The transformation remains centered on the same stage anchor.',
    'The same surface becomes a place to act.',
    'Connect a compact affordance with the larger panel it opens.',
    'A newly introduced unrelated surface should have its own arrival.',
    ['Widen a circular control into its panel','Grow the round action into a working surface'],
    ['title','detail'], [['panel-ready',.70,'morph-contents']]),
  baseEntry('mini-app-expand','Expand a mini-app in the thread',
    'An embedded card scales from its bottom anchor into reading size inside its conversation.',
    'The request, composer, phone silhouette, and conversation header hold.',
    'The short request and a usable response coexist in the same surface.',
    'Show an inline app that remains in the thread while it grows.',
    'A sheet that covers the conversation needs depth and scrim behavior.',
    ['Expand the mini-app in the conversation without opening a modal','Grow the inline app card while keeping the chat visible'],
    ['title','detail'], [['inline-card-readable',.45,'mini-app']]),
  baseEntry('selection-confirm','Resolve a button press in place',
    'One control transitions from action color to pressed styling to confirmation wording and color.',
    'The button position, geometry and parent card stay fixed.',
    'The same action visibly succeeds without a route change.',
    'Confirm a selected option or a completed action in the existing control.',
    'A queued or uncertain outcome should not be signaled as complete.',
    ['Change the same button into a confirmation after the press','Keep the card still while the confirm button turns into confirmed'],
    ['title','detail'], [['press',.49,'selection-card-action'],['confirmed',.57,'selection-card-action']]),
  baseEntry('card-orbit','Bring a product family into a readable lineup',
    'Independent cards arrive from separate angles with distinct rotations and settle into an ordered row.',
    'The destination row establishes a common baseline against a stationary field.',
    'Distinct offerings become a set while retaining their labels.',
    'Introduce a small product family with breadth and comparable visual weight.',
    'An avatar ring or a deck swipe implies a different spatial relationship.',
    ['Bring separate product cards together into a lineup','Pull the offerings from different directions into one row'],
    ['detail'], [['lineup-settled',.55,'orbit-card-2']]),
  {
    id:'messages-attachment-stack', title:'Swipe the front attachment off a stack',
    moves:'The top card translates and rotates off the deck; the next card advances in depth and turns back toward zero.',
    fixed:'The attachment count, conversation label, composer, and backdrop remain fixed.',
    notice:'The photos are separate cards in one attachment, and the next card moves into the lead slot.',
    fits:'Show one-at-a-time browsing with an authored inline stack of overlapping attachments.',
    avoid:'A horizontal media rail needs a shared strip translation with no individual promotion.',
    intents:['Peel the front photo away and bring the next attachment forward','Flick the top picture aside so the photo underneath takes its place'],
    editable:['heading','copy','photos','swipes'], photoCount:{min:2,max:5},
    example:'motion/examples/photo-swipe.content.json',
    comparison:'motion/PHOTO-SWIPE.md',
    source:{kind:'authored-adaptation',ref:'a23bfb294fbc65739811a84f264ad306ca192fe1:skill/imessage-motion-recreation/director/motion-library/blocks.mjs#attachmentStack',range:[0,4],
      note:'The earlier recipe supplies rank-by-rank translation, rotation and scale. Inline promotion and gesture timing are authored.'},
    build:attachmentStack,
  },
  {
    id:'inline-card-expand', title:'Raise a detail sheet above a dimmed conversation',
    moves:'A distinct grabber and sheet rise together and settle while the chat dims below.',
    fixed:'The header and underlying message/card stay put in the conversation.',
    notice:'The selected card opens another surface while the thread remains visible underneath.',
    fits:'Expose more detail or actions in a temporary sheet while preserving conversation context.',
    avoid:'An inline card expanding in place or an app-drawer picker has different content and layer ownership.',
    intents:['Open a full sheet over a dimmed conversation','Lift the bottom sheet over the chat and dim the conversation below','Tapping the preview pulls up details in a modal with the chat still behind'],
    editable:['heading','copy','title','detail','action','photos'],
    source:film('03-photon-mini',[7.033333,8.033333],[211,240],'Historical grabber y samples from a23bfb2 mapped into a new detail sheet. The scrim and content are authored.'),
    build:riseSheet,
  },
  {
    id:'avatar-ring-assemble', title:'Gather portraits around centered copy',
    moves:'Portraits approach on separate trajectories, sharpen and settle around shrinking headline copy.',
    fixed:'The center of the copy remains anchored and the backdrop holds.',
    notice:'Independent people converge around a shared idea without shifting the idea’s anchor.',
    fits:'Present a group or set of participants around one promise.',
    avoid:'Present products in a lineup if readers need to compare each with equal prominence.',
    intents:['Gather headshots around a centered headline','Bring the portraits in from different directions around the text'],
    editable:['heading','title','detail','photos'],
    source:film('06-gallery',[20.1,21.8],[603,653],'The centered text scale follows historical a23bfb2 samples. Portrait routes, focus and artwork are authored.'),
    build:gatherPortraits,
  },
  {
    id:'tear-perforated-ticket', title:'Separate a ticket along its perforation',
    moves:'A perforated seam parts left to right as the stub tilts around the still-joined edge, then drops once detached.',
    fixed:'The main ticket, its copy and the backdrop stay pinned.',
    notice:'The smaller section belonged to the original ticket and is now independently usable.',
    fits:'Show a detachable stub or one part becoming independent after separation.',
    avoid:'An ordinary close action has no physical seam, and a stack reveal keeps its surfaces intact.',
    intents:['Tear the receipt stub off along the perforated line','Detach the bottom of a ticket while the top stays pinned'],
    editable:['heading','title','detail','action'], source:authored('tear-perforated-ticket'),
    build(ctx) {
      const {stage, group, rect, text, content, track, event} = ctx;
      const stub = group('ticket-stub',56,164,[
        rect('stub-surface',0,0,388,63,'#e6c784',12),
        text('stub-copy',content.action,30,23,16,{fontWeight:700,fill:'#3d2d16'}),
      ],{originX:386,originY:0});
      const sheet = group('main-ticket',56,36,[
        rect('ticket-matte',0,0,388,129,'#f8e5ae',15),
        text('ticket-title',content.title,28,25,26,{fontWeight:700,fill:'#3d2d16'}),
        text('ticket-detail',content.detail,30,70,16,{fill:'#574522'}),
      ]);
      const tabs = Array.from({length: 19}, (_, i) => {
        const tab = rect(`perforation-${i}`,67+i*20,160,10,6,'#ad9154',3);
        track(tab,'opacity',[[0,1],[.25+i*.02,0,'hold']]);
        return tab;
      });
      track(stub,'rotation',[[0,0],[.24,0],[.60,-12,'easeIn'],[.85,-7,ease]]);
      track(stub,'y',[[0,164],[.61,164],[.85,206,ease]]);
      track(stub,'x',[[0,56],[.61,56],[.85,30,ease]]);
      stage.children.push(stub,sheet,...tabs);
      ctx.label(content.detail);
      event('tear-start',.25,tabs[0].id,'ticket.tear');
      event('stub-detaches',.61,stub.id,'ticket.detach');
    },
  },
  {
    id:'message-pin-landing', title:'Carry a location cue from chat to a map pin',
    moves:'A dot leaves the inline location cue, travels into the map, and compresses before it becomes an anchored pin.',
    fixed:'The question, stage map, route, and heading remain stationary throughout the travel.',
    notice:'The viewer connects the original question to an exact place on the map.',
    fits:'Turn an address or a location answer into a physical destination while preserving the related question.',
    avoid:'For unrelated destinations, use separate labels and a camera move rather than a single traveling token.',
    intents:['Take the answer out of the chat and land it on a map pin','Carry a location from a text bubble to its spot on the map','Move the location token into an actual mapped destination'],
    editable:['heading','copy','title','detail'], source:authored('message-pin-landing'),
    build(ctx) {
      const {stage, group, rect, text, colors, content, track, event} = ctx;
      const thread = ctx.ui.MessageBubble({id:'location-query',x:28,y:20,width:380,height:49,copy:content.copy,side:'incoming',fontSize:16});
      const map = group('map-area',28,80,[rect('map-field',0,0,444,185,'#edf1e8',12),
        {id:'map-road',type:'path',d:'M -12 111 C 109 113 180 49 227 86 S 333 117 450 28 M 94 -5 C 62 81 194 148 137 189 M 320 -6 C 284 59 447 138 353 192',fill:'none',stroke:'#ffffff',strokeWidth:13},
        {id:'route',type:'path',d:'M 28 111 C 109 113 180 49 227 86 S 258 113 281 101',fill:'none',stroke:'#7caec4',strokeWidth:4},
        text('map-place',content.title,287,108,15,{fill:colors.muted,fontWeight:700}),
      ],{clip:clip(444,185,12)});
      const pin = group('mapped-cue',56,45,[
        {id:'pin-tail',type:'path',d:'M -6 4 L 0 15 L 6 4 Z',fill:colors.blue,opacity:0},
        {id:'pin-dot',type:'circle',x:-9,y:-9,width:18,height:18,fill:colors.blue},
      ]);
      track(pin,'x',[[0,56],[.26,56],[.47,191,'easeIn'],[.69,309,ease]]);
      track(pin,'y',[[0,45],[.26,45],[.47,98,'easeIn'],[.69,171,ease]]);
      track(pin,'scaleY',[[0,1],[.65,1],[.70,.76],[.77,1.1,ease],[.81,1,ease]]);
      track(pin.children[0],'opacity',[[0,0],[.68,0],[.77,1]]);
      stage.children.push(map,thread,pin);
      ctx.label(content.detail);
      event('location-leaves',.29,pin.id,'location.transfer');
      event('location-lands',.69,pin.id,'location.mark');
    },
  },
];
