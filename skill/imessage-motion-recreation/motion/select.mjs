/** Offline brief selection. Hard constraints come before catalog similarity. */

const ALIASES = [
  [/\b(?:top (?:line|label|caption|title)|name at the top|masthead|headline|header|title)\b/g, 'heading'],
  [/\b(?:headshots?|profile (?:photos|pictures))\b/g, 'avatar'],
  [/\b(?:images?|pictures?|thumbnails?|photographs?|imagery|stills)\b/g, 'photos'],
  [/\b(?:photo|pics?)\b/g, 'photos'],
  [/\b(?:side to side horizontally|side to side|laterally|sideways|horizontally)\b/g, 'horizontal'],
  [/\b(?:beneath|below|underneath)\b/g, 'under'],
  [/\b(?:above|atop)\b/g, 'over'],
  [/\b(?:stay(?:s|ing)? put|hold(?:s|ing)? still|remain(?:s|ing)? (?:fixed|still|in place)|stay(?:s|ing)? (?:fixed|still|in place)|lock(?:ed)? in place)\b/g, 'fixed'],
  [/\b(?:stationary|unmoving|motionless|anchored|pinned|unchanged|static)\b/g, 'fixed'],
  [/\b(?:don['’]t|doesn['’]t|shouldn['’]t|mustn['’]t|won['’]t|can['’]t)\b/g, 'not'],
  [/\b(?:scroll(?:s|ing|ed)?|glid(?:e[sd]?|ing)|drift(?:s|ing|ed)?|travel(?:s|l?ing|l?ed)?|slid(?:e[sd]?|ing)|pan(?:s|ning|ned)?)\b/g, 'slide'],
  [/\bmotion blur\b/g, 'blur'],
  [/\b(?:animat(?:e[sd]?|ing)|mov(?:e[sd]?|ing)|motion)\b/g, 'move'],
  [/\b(?:twirl(?:s|ing)?|spin(?:s|ning)?|rotat(?:e[sd]?|ing))\b/g, 'rotate'],
  [/\b(?:come together|gather(?:s|ing)?|converg(?:e[sd]?|ing))\b/g, 'assemble'],
  [/\b(?:scale down|get(?:s|ting)? smaller|contract(?:s|ing)?)\b/g, 'shrink'],
  [/\b(?:scale up|get(?:s|ting)? bigger|grow(?:s|ing)?|enlarge(?:s|d)?)\b/g, 'expand'],
  [/\b(?:full size|full screen)\b/g, 'fullscreen'],
  [/\b(?:darken(?:s|ing|ed)?|dim(?:s|ming|med)?)\b/g, 'dim'],
  [/\b(?:rise[sd]?|rising|ascend(?:s|ing|ed)?|come(?:s)? up|bring(?:s)? up)\b/g, 'rise'],
  [/\bupwards?\b/g, 'up'],
  [/\bdownwards?\b/g, 'down'],
  [/\bvertically\b/g, 'vertical'],
  [/\b(?:compose(?:r)? bar|input (?:box|field)|message field)\b/g, 'composer'],
  [/\b(?:conversation|conversations|group thread|message thread|chat thread)\b/g, 'chat'],
];

const STOP = new Set(('a an and are at be can could do enough for from get had has have he her him how i if in into is it its just let lets like make me my of on one only our out please put so some that the their them there these they this those to us use want was we were what when where which who will with would you your should can t s show see viewer notice stays place keep whole under over around then').split(' '));
const GENERAL = new Set(['move', 'slide', 'fixed', 'photo', 'heading', 'chat', 'control', 'button', 'card', 'message', 'screen', 'carousel', 'swipe', 'text', 'camera']);
const ACTOR = /\b(heading|photos|composer|camera|background|controls|buttons?|chat|viewport)\b/g;
const MOTION = 'slide|move|rise|drop|shift|sweep|rotate|expand|shrink|fade|swipe|bounce|zoom|scroll|animate';
const QUALIFIER = '(?:the |a |an |all |each |both |our |your |these |those |new )*';
const PAIR = {
  photos: {id:'photos-under-fixed-heading', fixed:'heading', directions:['left', 'horizontal']},
  heading: {id:'heading-over-fixed-photos', fixed:'photos', directions:['right', 'horizontal']},
};
const DIRECTION = 'up|down|left|right|vertical|horizontal';
const FIXED_BEFORE = new RegExp('\\b(?:fixed|keep|hold|pin|lock|freeze|leave alone|(?:not|never|without) (?:a |any )?(?:' + MOTION + ')) (?:up |down )?' + QUALIFIER + '$');
const FIXED_AFTER = new RegExp('^ (?:that |which |should |must |can |will |does |are |is |all |both |remains? |stays? |stay )*(?:fixed\\b|(?:not|never) (?:' + MOTION + ')\\b|alone\\b|still\\b)');
const MOVE_BEFORE = new RegExp('\\b(' + MOTION + ') (' + DIRECTION + ' )?' + QUALIFIER + '$');
const MOVE_AFTER = new RegExp('^ (?:that |which |should |must |will |would )*(' + MOTION + ')(?:s|es)?\\b(?: (' + DIRECTION + ')\\b)?');
const DIRECTION_AFTER = new RegExp('^ (' + DIRECTION + ')\\b');
const COORDINATED = new RegExp('\\b(photos|heading) and ' + QUALIFIER + '(photos|heading) (?:both )?(' + MOTION + ')(?:s|es)?\\b');
const JOINT_TARGET = new RegExp('\\b(' + MOTION + ') ' + QUALIFIER + '(photos|heading) and ' + QUALIFIER + '(photos|heading)\\b');

function normalized(input) {
  return ALIASES.reduce((value, [pattern, replacement]) => value.replace(pattern, replacement), String(input ?? '')
    .normalize('NFKD').replace(/\p{M}/gu, '').toLowerCase().replace(/[-‐–—]+/g, ' ')).replace(/[^a-z0-9]+/g, ' ').trim();
}

function terms(input) {
  return normalized(input).split(' ').filter(word => word && !STOP.has(word));
}

function stem(word) {
  if (word === 'heading') return word;
  if (word.length > 6 && word.endsWith('ing')) return word.slice(0, -3).replace(/([a-z])\1$/, '$1');
  if (word.endsWith('ies')) return word.slice(0, -3) + 'y';
  if (word.length > 4 && word.endsWith('s') && !word.endsWith('ss')) return word.slice(0, -1);
  return word;
}

function words(input) {
  return terms(input).map(stem);
}

function clauses(input) {
  return input.split(/[,;.!?]+|\b(?:while|whereas|but|although|where)\b/i).map(normalized).filter(Boolean);
}

function briefRoles(input) {
  const fixed = new Set();
  const moving = new Map();
  const mentioned = new Set();
  for (const clause of clauses(input)) {
    for (const match of clause.matchAll(ACTOR)) {
      const name = nameOf(match[1]);
      const before = clause.slice(0, match.index);
      const after = clause.slice(match.index + match[0].length).replace(/^ (?:strip|rail|row|grid|band|text)\b/, '');
      mentioned.add(name);
      if (FIXED_BEFORE.test(before) || FIXED_AFTER.test(after)) {
        fixed.add(name);
        continue;
      }
      const preceding = before.match(MOVE_BEFORE);
      const following = after.match(MOVE_AFTER);
      const verb = preceding?.[1] ?? following?.[1];
      const direction = preceding?.[2]?.trim() ?? following?.[2] ??
        (preceding ? after.match(DIRECTION_AFTER)?.[1] : undefined);
      if (verb) {
        moving.set(name, {verb, direction});
      }
    }
    const coordinated = clause.match(COORDINATED);
    if (coordinated) {
      moving.set(coordinated[1], {verb: coordinated[3]});
      moving.set(coordinated[2], {verb: coordinated[3]});
    }
    const jointTarget = clause.match(JOINT_TARGET);
    if (jointTarget && !fixed.has(jointTarget[2]) && !fixed.has(jointTarget[3])) {
      moving.set(jointTarget[2], {verb: jointTarget[1]});
      moving.set(jointTarget[3], {verb: jointTarget[1]});
    }
  }
  return {fixed, moving, mentioned};
}

function nameOf(word) {
  return /^buttons?$/.test(word) ? 'controls' : word;
}

function decision(action, reason, matches = [], extra = {}) {
  return {action, matches, reason, candidates: [], ...extra};
}

const EDITS = [
  [/\b(?:slow(?:er|ly| down)|speed up|faster|quicker|over \d+(?:\.\d+)? seconds|a longer pause|hold longer)\b/i, 'timing'],
  [/\b(?:with (?:new|different|my|our|your|three|four|five) (?:photos|images|pictures|labels|copy|messages|cards)|swap (?:in |out )?|replace (?:the |its |their |those )?|change (?:the |its ))\b/i, 'content'],
  [/\b(?:again|twice|repeat|loop|three times)\b/i, 'repetition'],
];
const SPECIAL = /\b(?:3d|three dimensional|page curl|cloth physics|fabric simulation|fluid simulation|ray tracing|particle simulation|elastic grid|glass reflection|liquid morph|lens flare|live tracking|procedural fire|blow up into confetti)\b/g;
const FORBID = /\b(?:without|avoid|no|never|not) (?:a |an |any |the )?(?:any )?([a-z]+)\b/g;
const TECHNIQUES = new Set('bounce camera cut dim fade flip zoom rotate spin slide shake explode tilt blur pulse strobe wobble'.split(' '));

function avoidedTechniques(input) {
  return [...normalized(input).matchAll(FORBID)].map(match => match[1]).filter(word => TECHNIQUES.has(word));
}

function adaptation(input) {
  return EDITS.filter(([pattern]) => pattern.test(input)).map(([, kind]) => kind);
}

function matched(entry, request, candidates = []) {
  const changes = adaptation(request);
  const action = changes.length ? 'adapt' : 'retrieve';
  return decision(action, entry.fits ?? entry.notice ?? entry.moves, [entry.id], {
    candidates,
    ...(changes.length && {changes, conditions: 'Keep the motion’s moving and fixed layers. Check the entry’s editable fields for the requested changes.'}),
  });
}

function roleMatch(entries, roles, input) {
  const {fixed, moving, mentioned} = roles;
  const conflict = [...fixed].find(actor => moving.has(actor));
  if (conflict) return decision('missing', `The request asks for the ${conflict} to move and stay fixed in the same beat.`);
  if (!mentioned.has('photos') || !mentioned.has('heading')) return null;
  const relational = /\b(?:under|over|through|behind)\b/.test(input);
  for (const [actor, motion] of Object.entries(PAIR)) {
    const movement = moving.get(actor);
    if (!movement || !(fixed.has(motion.fixed) || relational) || moving.size > 1) continue;
    const compatible = /^(?:move|slide|sweep|shift)$/.test(movement.verb)
      && (!movement.direction || motion.directions.includes(movement.direction));
    const entry = entries.find(candidate => candidate.id === motion.id);
    if (entry && compatible && !avoidedTechniques(input).includes('slide')) return matched(entry, input);
  }
  return null;
}

function indexEntry(entry) {
  const main = [entry.id, entry.title, entry.moves, ...(entry.intents ?? [])].join(' ');
  const examples = [entry.title, ...(entry.intents ?? [])].map(words);
  return {
    entry,
    primary: new Set(words(main)),
    context: new Set(words([entry.fits, entry.notice, entry.fixed].join(' '))),
    moving: new Set(words(entry.moves)),
    fixed: new Set(words(entry.fixed)),
    examples,
    all: normalized([main, entry.fits, entry.notice].join(' ')),
  };
}

function rank(entries, input, roles) {
  const allWords = words(input);
  const query = new Set(allWords);
  const special = [...normalized(input).matchAll(SPECIAL)].map(match => match[0]);
  const forbidden = avoidedTechniques(input);
  const queryWithoutNegation = new Set([...query].filter(word => !forbidden.includes(word) && word !== 'not' && word !== 'no'));
  const indexed = entries.map(indexEntry);
  const counts = new Map([...queryWithoutNegation].map(word => [word, indexed.filter(record => record.primary.has(word)).length]));
  return indexed.map(({entry, primary, context, moving, fixed, examples, all}) => {
    const issues = [...special.filter(phrase => !all.includes(phrase)).map(phrase => `requires ${phrase}`),
      ...forbidden.filter(word => moving.has(stem(word))).map(word => `uses ${word}`)];
    for (const actor of roles.fixed) {
      if (moving.has(stem(actor)) && !fixed.has(stem(actor))) issues.push(`moves the requested fixed ${actor}`);
    }
    for (const [actor, movement] of roles.moving) {
      if (!moving.has(stem(actor))) issues.push(fixed.has(stem(actor))
        ? `fixes the requested moving ${actor}`
        : `does not describe a moving ${actor}`);
      if (TECHNIQUES.has(movement.verb) && !moving.has(stem(movement.verb))) issues.push(`requires ${movement.verb} on the ${actor}`);
      const photoPair = PAIR[actor];
      if (photoPair?.id === entry.id && movement.direction && !photoPair.directions.includes(movement.direction)) {
        issues.push(`travels ${photoPair.directions[0]}, requested ${movement.direction}`);
      }
    }
    const signals = [...queryWithoutNegation].filter(word => primary.has(word));
    const distinctive = signals.filter(word => !GENERAL.has(word));
    const relevance = signals.reduce((score, word) => {
      const rarity = 1 + Math.log((indexed.length + 2) / ((counts.get(word) ?? 0) + 2));
      return score + (GENERAL.has(word) ? 0.7 : rarity);
    }, 0);
    const contextScore = [...queryWithoutNegation].filter(word => context.has(word) && !primary.has(word)).length * 0.28;
    const pairs = new Set(allWords.slice(1).map((word, index) => allWords[index] + ' ' + word));
    const phraseScore = examples.reduce((best, example) => Math.max(best, example.slice(1)
      .filter((word, index) => pairs.has(example[index] + ' ' + word)).length * 1.75), 0);
    const assigned = [...roles.moving.keys()].filter(actor => moving.has(stem(actor))).length * 1.5
      + [...roles.fixed].filter(actor => fixed.has(stem(actor))).length * 1.2;
    const score = Math.round((relevance + contextScore + phraseScore + assigned) * 100) / 100;
    return {id: entry.id, score, signals, distinctive, issues};
  }).filter(candidate => candidate.score > 0)
    .sort((a, b) => Number(Boolean(a.issues.length)) - Number(Boolean(b.issues.length)) || b.score - a.score || a.id.localeCompare(b.id));
}

function isHold(input, roles) {
  if (roles.moving.size) return false;
  return /\b(?:still|steady|fixed)\b/.test(input)
    && /\b(?:everything|whole|entire|both|all|frame|shot|screen|hold|keep|stay|remain|leave|completely)\b/.test(input)
    || /\b(?:reading hold|time to read|long enough to read)\b/.test(input);
}

function selectBeat(entries, request) {
  const input = normalized(request);
  const roles = briefRoles(request);
  const prohibited = /\b(?:without|no|not|avoid) (?:extra |any |a |the )?(?:animation|motion|movement|animate|move|transitions?)\b/;
  const movement = /\b(?:slide|move|zoom|cut|reveal|tap|focus|fade|bounce|push|pull|scroll|change|shift|swipe|rotate|assemble|rise|dim|expand|shrink|drag|collapse|spill|shake)\b/;
  const explicitHold = isHold(input, roles) || prohibited.test(input);
  const positiveClauses = clauses(request).map(clause => clause.replace(/\b(?:not|without|no|avoid|never) (?:extra |any |a |the )?(?:animation|movement|animate|move|slide|zoom|cut|fade|bounce|rotate|scroll)\b/g, ''));
  if (explicitHold && !positiveClauses.some(clause => movement.test(clause))) {
    return decision('hold', 'A static reading hold preserves attention on the content and the requested fixed layers.');
  }
  if (![...input.matchAll(SPECIAL)].length) {
    const route = roleMatch(entries, roles, input);
    if (route) return route;
  }
  const candidates = rank(entries, request, roles).slice(0, 5);
  const [first, second] = candidates.filter(candidate => !candidate.issues.length);
  const decisive = first && first.score >= 3.4 && first.distinctive.length >= 1 && first.signals.length >= 2
    && (!second || first.score - second.score >= Math.max(0.85, first.score * 0.12));
  if (decisive) return matched(entries.find(entry => entry.id === first.id), request, candidates);
  const reason = candidates.length && !first
    ? 'The nearest catalog entries violate a required motion technique or fixed-layer constraint.'
    : candidates.length
      ? 'The wording has close alternatives. Specify which layer moves, which layer stays fixed, and what the viewer should notice.'
      : 'The catalog has no motion with enough evidence to fit this request.';
  return decision('missing', reason, [], {candidates});
}

export function select(entries, request) {
  if (!Array.isArray(entries)) throw new TypeError('Pass the catalog entries as an array.');
  const brief = String(request ?? '').trim();
  const explicit = entries.find(entry => entry.id.toLowerCase() === brief.toLowerCase());
  if (explicit) return matched(explicit, brief);
  if (!brief) return decision('missing', 'Describe what moves, what stays fixed, and what the viewer should notice.');
  const exactComposite = entries.find(entry => entry.composite &&
    entry.intents?.some(intent => normalized(intent) === normalized(brief)));
  if (exactComposite) return matched(exactComposite, brief);

  const beats = brief.split(/\b(?:and\s+then|followed\s+by|after\s+that|then)\b/i).map(beat => beat.trim()).filter(Boolean);
  if (beats.length < 2) return selectBeat(entries, brief);
  const selections = beats.map(beat => selectBeat(entries, beat));
  if (selections.every(selection => selection.action === 'hold')) return selections[0];
  if (selections.every(selection => selection.matches.length || selection.action === 'hold')) {
    const matches = selections.flatMap(selection => selection.matches);
    const composite = entries.find(entry => entry.composite && selections.every(selection => selection.matches[0] === entry.id));
    if (composite) return matched(composite, brief);
    return decision('combine', 'The request specifies successive beats. Keep their fixed layers and settle the first beat before starting the next.', matches, {
      sequence: selections.map((selection, index) => ({brief: beats[index], ...selection})),
    });
  }
  // Some entries already contain a sequence, such as two swipes through one stack.
  const whole = selectBeat(entries, brief);
  if (whole.matches.length && selections.every((selection, index) => selection.matches.includes(whole.matches[0]) ||
      selection.action === 'missing' && /^(?:swipe|tap|press|slide|move)\s+(?:it\s+)?again\b/i.test(beats[index]))) {
    return whole;
  }
  return decision('missing', 'At least one beat has no supported motion. Resolve that beat before combining scenes.', [], {
    sequence: selections.map((selection, index) => ({brief: beats[index], ...selection})),
  });
}
