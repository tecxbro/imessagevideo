import {readFileSync} from 'node:fs';
import {ActionButton, group, rect, text} from './components.mjs';

const catalog = JSON.parse(readFileSync(new URL('./catalogue.json', import.meta.url), 'utf8')).motion_catalog;
const evidenceRoot = 'release-evidence/film-trials/devin-bot/motion-catalog';
export function getMotion(id) {
  const entry = catalog.entries.find(item => item.id === id);
  if (!entry) throw Error(`Unknown motion: ${id}`);
  return entry;
}

export function describeMotion(entry) {
  const {signals, fit, source, ...description} = entry;
  if (!source) return {...description, source: null, preview: null, editable: false};
  return {
    ...description,
    source: {...catalog.sources[source], frames: entry.frames, frameConvention: 'zero-based, inclusive'},
    preview: `${evidenceRoot}/${entry.id}.mp4`,
    editable: true,
    commands: {
      scene: `scene ${entry.id} --out work/scene.json`,
      source: `source ${entry.id} --out work/reference.mp4`,
    },
  };
}

const normalize = value => value.toLowerCase().normalize('NFKD').replace(/[’']/g, '')
  .replace(/[^a-z0-9]+/g, ' ').trim().replace(/\b(photos|pictures|images|thumbnails|digits|attachments|fares|galleries)\b/g,
    token => token === 'galleries' ? 'gallery' : token.slice(0, -1));

export function searchMotions(brief) {
  // Do not promote an alternative that the brief explicitly rules out.
  const query = normalize(brief.replace(/\b(?:rather than|instead of|except for|not)\s+(?:a\s+|an\s+|the\s+)?(?:an?\s+)?(?:i?messages?\s+)?(?:photo\s+|image\s+|attachment\s+)?(?:stack|deck|carousel|rail)\b/gi, ' '));
  const phrase = term => ` ${query} `.includes(` ${normalize(term)} `);
  const results = catalog.entries.map(entry => {
    const cues = Object.entries(entry.signals).flatMap(([signal, terms]) => {
      const matches = terms.filter(phrase);
      return matches.length ? [{signal, matches}] : [];
    });
    const sourceMatch = entry.frames?.every(frame => phrase(String(frame)));
    const idMatch = query === normalize(entry.id);
    const score = cues.length * 3 + (sourceMatch || idMatch ? 20 : 0);
    return {entry, cues, score, sourceMatch, idMatch};
  }).filter(match => match.score).sort((a, b) => b.score - a.score || a.entry.id.localeCompare(b.entry.id));
  const top = results[0];
  const status = !top ? 'no-match'
    : top.score < 6 || top.score === results[1]?.score ? 'ambiguous' : 'matched';
  return {
    status,
    selection: status === 'matched' ? top.entry.id : null,
    results: results.map(({entry, cues, score, sourceMatch, idMatch}) =>
      ({...describeMotion(entry), score, cues, ...(sourceMatch ? {sourceMatch} : {}), ...(idMatch ? {idMatch} : {})})),
  };
}

const key = (frame, value) => ({t: frame/30, value, ease: 'linear'});
const track = ({samples}, map, lead) => samples.map((value, i) => key(i+lead, map(value)));
const circle = (id, x, y, size, fill) => ({id, type: 'circle', x, y, width: size, height: size, fill});
const str = (value, fallback, label, limit = 60) => {
  value ??= fallback;
  if (typeof value !== 'string' || !value.trim() || value.length > limit || /[\r\n]/.test(value)) {
    throw Error(`${label} must be 1–${limit} characters on one line`);
  }
  return value;
};
const color = (value, fallback) => {
  value ??= fallback;
  if (typeof value !== 'string' || !/^#[a-f0-9]{6}$/i.test(value)) throw Error('Use six-digit hex colors');
  return value;
};
const textMid = (id, value, x, y, size, options) => text(id, value, x, y, size, {textAnchor:'middle', ...options});

function rail(id, x, y, width, height, children, keys) {
  return group(id+'-viewport', x, y, [group(id, 0, 0, children, {keyframes:{x:keys}})],
    {clip:{width, height}});
}

const defaultCards = [
  {label:'FOYER', color:'#d5a780', accent:'#69362f', motif:'arch'},
  {label:'LAMP', color:'#c8955e', accent:'#46423a', motif:'disc'},
  {label:'STILL LIFE', color:'#e2c781', accent:'#8e4840', motif:'blocks'},
  {label:'TERRACE', color:'#a4af82', accent:'#3b504c', motif:'arch'},
  {label:'BLUE ROOM', color:'#82aeb1', accent:'#2e4f61', motif:'disc'},
];

function artwork(id, item, x, width, height) {
  const {label, src, color:fill, accent, motif} = item;
  let children;
  if (src) {
    children = [{id:id+'-image', type:'image', src, x:0, y:0, width, height}];
  } else {
    const size = Math.min(width, height)*.55;
    const center = (width-size)/2;
    children = [rect(id+'-base', 0, 0, width, height, fill)];
    if (motif === 'disc') {
      children.push(circle(id+'-shape', center, 52, size, accent),
        circle(id+'-inset', center+size*.35, 52+size*.35, size*.3, fill));
    } else if (motif === 'arch') {
      children.push(rect(id+'-shape', center, 48, size, .96*height, accent, size/2),
        rect(id+'-inset', center+size*.18, 77, size*.64, .86*height, fill, size*.32));
    } else {
      children.push(rect(id+'-shape', center, 64, size*.68, size, accent, 8),
        rect(id+'-inset', center+size*.4, 120, size*.6, size*.66, accent, 8, {rotation:-18}));
    }
    children.push(rect(id+'-plate', 15, height-51, width-30, 36, '#ffffff', 8));
    children.push(text(id+'-label', label, 26, height-43, 15, {fontWeight:700, letterSpacing:2}));
  }
  return group(id, x, 0, children, {clip:{width, height, radius:18}});
}

function buildPhotoRail(entry, options, lead) {
  const cards = options.cards ?? defaultCards;
  if (!Array.isArray(cards) || cards.length !== defaultCards.length) throw Error('Supply exactly five artwork cards');
  const boxes = [[-1060,417],[-619,268],[-327,504],[201,334],[559,444]];
  const actionColor = color(options.accent, '#202a24');
  const art = cards.map((card, i) => {
    if (!card || typeof card !== 'object' || Array.isArray(card)) throw Error('Each card must be an object');
    const fallback = defaultCards[i], motif = card.motif ?? fallback.motif;
    if (!['disc', 'arch', 'blocks'].includes(motif)) throw Error('Use disc, arch, or blocks as the artwork motif');
    if (card.src !== undefined && (typeof card.src !== 'string' || !card.src.trim() || /^(?:[a-z][a-z0-9+.-]*:|\/\/)/i.test(card.src))) {
      throw Error('Card src must be a local image path relative to the output scene');
    }
    const [left, width] = boxes[i];
    return artwork('art-'+i, {
      label: str(card.label, fallback.label, 'Card label', 22), src:card.src, motif,
      color: color(card.color, fallback.color), accent: color(card.accent, fallback.accent),
    }, left-195, width, 334);
  });
  return [
    rect('gallery-panel', 166, 19, 636, 682, '#ffffff', 36),
    text('gallery-title', str(options.title, 'Linden Design Museum', 'Title', 30), 195, 57, 34, {fontWeight:700}),
    text('gallery-meta', str(options.subtitle, 'New exhibition  /  Open today', 'Subtitle'), 195, 107, 21, {fill:'#505854'}),
    ActionButton({id:'gallery-action', x:195, y:151, width:348, copy:str(options.action, 'Plan a visit', 'Action', 24), fill:actionColor}),
    ActionButton({id:'gallery-info', x:563, y:151, width:92, copy:'Info', fill:actionColor}),
    ActionButton({id:'gallery-share', x:675, y:151, width:98, copy:'Share', fill:actionColor}),
    text('gallery-tabs', 'Overview           Collection           Visit', 195, 243, 20, {fontWeight:600}),
    rect('gallery-tab-indicator', 195, 278, 98, 3, actionColor, 1.5),
    rail('photo-rail', 195, 294, 578, 334, art, track(entry.fit, x => x, lead)),
    text('gallery-footer', str(options.footer, 'Gallery 02  /  Level One', 'Footer'), 195, 652, 19, {fill:'#505854'}),
  ];
}

function buildFareRail(entry, options, lead) {
  const fill = color(options.accent, '#245bc0');
  const cards = ['Standard','Flex'].map((fallback, i) => {
    const id = 'fare-'+i;
    return group(id, 24+i*359, 0, [
      rect(id+'-card', 0, 0, 338, 392, '#ffffff', 30),
      text(id+'-title', str(options.tiers?.[i], fallback, 'Tier name', 20), 20, 28, 34, {fontWeight:700}),
      text(id+'-details', i ? 'Priority boarding\n2 carry-ons\nFree changes' : '1 carry-on\nStandard boarding\nChange fee applies',
        20, 120, 26, {lineHeight:49, fill:'#2c3955'}),
      ActionButton({id:id+'-action', x:20, y:309, width:298, copy:'Select', fill}),
    ]);
  });
  return [
    rect('fare-sheet', 188, 38, 584, 644, '#c8dffa', 36),
    rect('flight-summary', 212, 62, 536, 112, '#ffffff', 25),
    text('flight-title', str(options.title, 'SEA to PDX', 'Title', 28), 235, 87, 31, {fontWeight:700}),
    text('flight-subtitle', str(options.subtitle, 'Choose your fare', 'Subtitle', 28), 235, 127, 21),
    rail('fare-rail', 188, 222, 584, 404, cards, track(entry.fit, x => x, lead)),
  ];
}

function buildAmountRoll(entry, options, lead) {
  const bg = color(options.accent, '#19252e');
  const start = options.startDigit ?? 2;
  if (!Number.isInteger(start) || start < 0 || start > 5) throw Error('startDigit must be an integer from 0 to 5 (no carry)');
  const digits = Array.from({length:5}, (_,i) => textMid('units-'+i, String(start+i), 27, 5+i*94, 68, {fill:'#ffffff'}));
  const plusKeys = [1.1,1.28,1.28,1.28,1.16,1.12,1.22,1.25,1.25,1.17,1.14,1.25,1.31,
    1.31,1.22,1.14,1.08,1.23,1.23,1.31,1.27,1.17,1.06,1.06,1];
  const scale = track({samples:plusKeys}, x => x, lead);
  return [
    rect('amount-panel', 187, 138, 586, 444, bg, 53),
    textMid('amount-title', str(options.title, 'Add to your balance', 'Title', 30), 480, 210, 29, {fill:'#ffffff'}),
    text('amount-prefix', str(options.prefix, '$1', 'Amount prefix', 5), 423, 316, 68, {fill:'#ffffff', textAnchor:'end'}),
    group('units-viewport', 423, 311, [group('units-rail', 0, 0, digits, {
      keyframes:{y:track(entry.fit, y => y, lead)},
    })], {clip:{width:54,height:94}}),
    text('amount-suffix', str(options.suffix, '.50', 'Amount suffix', 4), 477, 316, 68, {fill:'#ffffff'}),
    group('amount-plus', 617, 325, [
      circle('amount-plus-disc', 0, 0, 62, '#38515f'),
      textMid('amount-plus-mark', '+', 31, 7, 39, {fill:'#ffffff'}),
    ], {originX:31, originY:31, keyframes:{scaleX:scale, scaleY:scale}}),
    circle('amount-minus-disc', 281, 325, 62, '#38515f'),
    textMid('amount-minus-mark', '−', 312, 332, 39, {fill:'#ffffff'}),
    ActionButton({id:'amount-submit', x:330, y:477, width:300, copy:'Review', fill:'#35566d'}),
  ];
}

const builds = new Map([
  ['linq-fixed-chrome-photo-rail', buildPhotoRail],
  ['linq-flight-fare-rail', buildFareRail],
  ['linq-amount-units-roll', buildAmountRoll],
]);

export function buildCatalogScene(id, options = {}) {
  const entry = getMotion(id);
  const build = builds.get(id);
  if (!build) throw Error(`${entry.title}: ${entry.avoid}`);
  if (!options || typeof options !== 'object' || Array.isArray(options)) throw Error('Config must be a JSON object');
  const lead = 12, tail = 18;
  const source = catalog.sources[entry.source];
  return {
    width:960, height:720, fps:source.fps, duration:(lead+entry.fit.samples.length+tail)/source.fps,
    title:entry.title, background:color(options.background, '#f0ede6'),
    source:{
      notes:'New artwork and layout around fitted source motion; not a source-exact render.',
      evidence:{url:source.url, sha256:source.sha256, citedFrames:entry.frames,
        fittedFrames:[entry.fit.samples_start, entry.fit.samples_start+entry.fit.samples.length-1], outputLeadFrames:lead},
    },
    layers:build(entry, options, lead),
  };
}
