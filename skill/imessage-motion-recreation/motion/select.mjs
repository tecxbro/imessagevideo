/** Offline brief selection. Hard constraints come before catalog similarity. */

const ALIASES = [
  [/\b(?:top (?:line|label|caption|title)|name at the top|(?:venue|place|shop|storefront|chat|conversation|thread) name|masthead|headline|header|title)\b/g, 'heading'],
  [/\b(?:avatars?|headshots?|portraits?|profile (?:photos|pictures))\b/g, 'avatar'],
  [/\b(?:images?|pictures?|thumbnails?|photographs?|imagery|stills)\b/g, 'photos'],
  [/\b(?:photo|pics?)\b/g, 'photos'],
  [/\b(?:side to side horizontally|side to side|laterally|sideways|horizontally)\b/g, 'horizontal'],
  [/\b(?:beneath|below|underneath)\b/g, 'under'],
  [/\b(?:above|atop)\b/g, 'over'],
  [/\blabel(?= (?:over|under) (?:the )?photos\b)/g, 'heading'],
  [/\b(?:stay(?:s|ing)? put|hold(?:s|ing)? still|remain(?:s|ing)? (?:fixed|still|in place)|stay(?:s|ing)? (?:fixed|still|in place|glued to (?:the )?top)|lock(?:ed)? in place)\b/g, 'fixed'],
  [/\b(?:exactly )?(?:at|in) (?:its|their) (?:current|original) (?:position|spot)\b/g, 'fixed'],
  [/\b(?:right |exactly )?where (?:it is|they are)\b/g, 'fixed'],
  [/\bsit(?:s)? (?:exactly )?as (?:it is|they are)\b/g, 'fixed'],
  [/\b(?:stationary|unmoving|motionless|anchored|pinned|unchanged|static)\b/g, 'fixed'],
  [/\b(?:don['’]t|doesn['’]t|shouldn['’]t|mustn['’]t|won['’]t|can['’]t)\b/g, 'not'],
  [/\b(?:scroll(?:s|ing|ed)?|glid(?:e[sd]?|ing)|drift(?:s|ing|ed)?|cruis(?:e[sd]?|ing)|travel(?:s|l?ing|l?ed)?|slid(?:e[sd]?|ing)|pan(?:s|ning|ned)?|translat(?:e[sd]?|ing))\b/g, 'slide'],
  [/\bmotion blur\b/g, 'blur'],
  [/\b(?:animat(?:e[sd]?|ing)|mov(?:e[sd]?|ing))\b/g, 'move'],
  [/\b(?:twirl(?:s|ing)?|spin(?:s|ning)?|rotat(?:e[sd]?|ing))\b/g, 'rotate'],
  [/\bfad(?:e[sd]?|ing)\b/g, 'fade'],
  [/\b(?:come together|gather(?:s|ing)?|converg(?:e[sd]?|ing))\b/g, 'assemble'],
  [/\b(?:scale down|get(?:s|ting)? smaller|contract(?:s|ing)?)\b/g, 'shrink'],
  [/\bcent(?:er|re)d\b/g, 'center'],
  [/\b(?:scale up|get(?:s|ting)? bigger|grow(?:s|ing)?|enlarge(?:s|d)?)\b/g, 'expand'],
  [/\b(?:full size|full screen)\b/g, 'fullscreen'],
  [/\b(?:darken(?:s|ing|ed)?|dim(?:s|ming|med)?)\b/g, 'dim'],
  [/\b(?:rise[sd]?|rising|ascend(?:s|ing|ed)?|come(?:s)? up|bring(?:s)? up|lift(?:s|ing|ed)?)\b/g, 'rise'],
  [/\bupwards?\b/g, 'up'],
  [/\bdownwards?\b/g, 'down'],
  [/\bvertically\b/g, 'vertical'],
  [/\b(?:compose(?:r)? bar|input (?:box|field)|message (?:box|field)|typing field|draft field|reply input|text entry)\b/g, 'composer'],
  [/\b(heading and (?:the )?)input\b/g, '$1composer'],
  [/\b(?:old|older|earlier|previous|prior|existing) (?:chat )?(?:messages|rows|bubbles|texts)\b/g, 'transcript'],
  [/\b(?:every|all) (?:chat )?(?:bubble|bubbles|messages)\b/g, 'transcript'],
  [/\b(?:conversation|conversations|group thread|message thread|chat thread)\b/g, 'chat'],
  [/\bchat (?=(?:over|under) (?:it|them)\b)/g, 'transcript '],
  [/\b(?:nudg(?:e[sd]?|ing)|shift(?:s|ing|ed)?)\b/g, 'shift'],
  [/\b(?:answer(?:s|ed|ing)?|respond(?:s|ed|ing)?|responses?)\b/g, 'reply'],
  [/\b(?:sent|sending|sends)\b/g, 'send'],
  [/\btyping progress\b/g, 'type draft'],
  [/\b(?:typed|typing|types)\b/g, 'type'],
];

const STOP = new Set(('a an and are at be can could do enough for from get had has have he her him how i if in into is it its just let lets like make me my of on one only our out please put so some that the their them there these they this those to us use want was we were what when where which who will with would you your should can t s show see viewer notice stays place keep whole under over around then avoid without no not never as yet while itself every each exactly').split(' '));
const GENERAL = new Set(['move', 'slide', 'fixed', 'photo', 'heading', 'chat', 'control', 'button', 'card', 'message', 'screen', 'carousel', 'swipe', 'text', 'camera']);
const ACTOR_NAME = 'heading|photos|avatar|composer|camera|background|controls|buttons?|chat|viewport|transcript';
const ACTOR = new RegExp('\\b(' + ACTOR_NAME + ')\\b', 'g');
const MOTION = 'slide|move|rise|drop|shift|sweep|rotate|expand|shrink|fade|swipe|bounce|zoom|scroll|animate|bring|ease|assemble';
const QUALIFIER = '(?:the |a |an |all |each |every |both |our |your |these |those |new |existing |current |first |long |wide |small )*';
const PAIR = {
  photos: {id:'photos-under-fixed-heading', fixed:'heading', defaultDirection:'left', adaptDirections:['right']},
  heading: {id:'heading-over-fixed-photos', fixed:'photos', defaultDirection:'right', adaptDirections:['left', 'up', 'down', 'vertical']},
};
const DIRECTION = 'up|down|left|right|vertical|horizontal';
const FIXED_BEFORE = new RegExp('\\b(?:fixed|still|keep|hold|pin|lock|freeze|arrest|immobilize|leave alone|(?:not|never|without|avoid) (?:a |any )?(?:' + MOTION + ')) (?:up |down )?' + QUALIFIER + '$');
const FIXED_AFTER = new RegExp('^ (?:that |which |should |must |can |will |does |are |is |all |both |remains? |stays? |stay )*(?:fixed\\b|(?:not|never) (?:' + MOTION + ')\\b|alone\\b|still\\b)');
const MOVE_BEFORE = new RegExp('\\b(' + MOTION + ') (' + DIRECTION + ' )?' + QUALIFIER + '$');
const DESCRIBED_TARGET = new RegExp('^\\s*(?:only |just |please )?(' + MOTION + ') (' + DIRECTION + ' )?(?:the |a |an |each |my |our |your )(?:[a-z]+ ){0,4}$');
const MOVE_AFTER = new RegExp('^ (?:that |which |itself |themselves |alone |should |must |will |would |to )*(' + MOTION + ')(?:s|es)?\\b(?: (?:to (?:the )?)?(' + DIRECTION + ')\\b)?');
const DIRECTION_AFTER = new RegExp('^ (?:(?:over|under|behind) (?:it|them) )?(?:to (?:the )?)?(' + DIRECTION + ')\\b');
const COORDINATED = new RegExp('\\b(photos|heading) and ' + QUALIFIER + '(photos|heading) (?:both )?(' + MOTION + ')(?:s|es)?\\b');
const JOINT_TARGET = new RegExp('\\b(' + MOTION + ') ' + QUALIFIER + '(photos|heading) and ' + QUALIFIER + '(photos|heading)\\b');
const JOINED_ACTORS = new RegExp('\\b(' + ACTOR_NAME + ') and ' + QUALIFIER + '(' + ACTOR_NAME + ')\\b', 'g');
const LOCAL_PHOTO_ACTION = /\b(?:reorder|rearrange|reflow|grid density|photos? picker|select(?:ed)? (?:one|a) photos|(?:one|single) photos .* (?:viewer|slot))\b/;

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
  return input.split(/[,;.!?]+|\b(?:while|whereas|but|although)\b/i).map(normalized).filter(Boolean);
}

function briefRoles(input) {
  const fixed = new Set();
  const moving = new Map();
  const mentioned = new Set();
  const usesHeading = /\bheading\b/.test(normalized(input));
  for (const line of clauses(input)) {
    const clause = usesHeading ? line.replace(/\bfilmstrip\b/g, 'photos') : line;
    const setInMotion = /^\s*(?:only |just |please )?(?:set|put) /.test(clause) && /\bin motion\b/.test(clause);
    const holdInPlace = /^(?:only |just |please )?(?:keep|hold|leave)\b/.test(clause);
    const fixedAfter = after => FIXED_AFTER.test(after) || holdInPlace && /^ in place\b/.test(after);
    let firstActor = true;
    for (const match of clause.matchAll(ACTOR)) {
      const name = nameOf(match[1]);
      const before = clause.slice(0, match.index);
      const after = clause.slice(match.index + match[0].length).replace(/^ (?:strip|rail|row|grid|band|text)\b/, '');
      mentioned.add(name);
      // Other thumbnails can hold their slots while the selected thumbnail moves.
      if (name === 'photos' && /\b(?:other|remaining|unselected|neighboring) $/.test(before)) continue;
      if (setInMotion && firstActor) {
        moving.set(name, {verb: 'move'});
        firstActor = false;
        continue;
      }
      firstActor = false;
      if (fixedAfter(after) || FIXED_BEFORE.test(before) && !(/\bkeep (?:the )?$/.test(before) && MOVE_AFTER.test(after))) {
        fixed.add(name);
        continue;
      }
      const preceding = before.match(MOVE_BEFORE) ?? before.match(DESCRIBED_TARGET);
      const following = after.match(MOVE_AFTER);
      const verb = preceding?.[1] ?? following?.[1];
      const direction = preceding?.[2]?.trim() ?? following?.[2] ??
        (preceding ? after.match(DIRECTION_AFTER)?.[1] : undefined) ?? (verb === 'rise' ? 'up' : undefined);
      if (verb) {
        moving.set(name, {verb, direction});
      }
    }
    for (const pair of clause.matchAll(JOINED_ACTORS)) {
      if (fixedAfter(clause.slice(pair.index + pair[0].length))) {
        fixed.add(nameOf(pair[1]));
        fixed.add(nameOf(pair[2]));
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
const TECHNIQUES = new Set('bounce camera cut dim fade flip zoom rotate spin slide rise shake explode tilt blur pulse strobe wobble send swipe'.split(' '));
const CAPABILITIES = {
  zoom: ['scale', 'scal', 'pinch'],
  slide: ['shift', 'drag', 'rail'],
  fade: ['opacity', 'dissolve'],
};

function avoidedTechniques(input) {
  return [...normalized(input).matchAll(FORBID)].map(match => stem(match[1])).filter(word => TECHNIQUES.has(word));
}

function requestedSpecial(input) {
  return [...input.matchAll(SPECIAL)].filter(match => !/\b(?:without|avoid|no|never|not) (?:a |an |any |the )?$/.test(input.slice(0, match.index)))
    .map(match => match[0]);
}

function uses(moving, technique) {
  return moving.has(technique) || CAPABILITIES[technique]?.some(word => moving.has(word));
}

function adaptation(input) {
  return EDITS.filter(([pattern]) => pattern.test(input)).map(([, kind]) => kind);
}

function matched(entry, request, candidates = [], content = {}) {
  const changes = [...adaptation(request), ...Object.keys(content)];
  const action = changes.length ? 'adapt' : 'retrieve';
  return decision(action, entry.fits ?? entry.notice ?? entry.moves, [entry.id], {
    candidates,
    ...(changes.length && {changes, conditions: 'Keep the motion’s moving and fixed layers. Check the entry’s editable fields for the requested changes.'}),
    ...(Object.keys(content).length && {content}),
  });
}

function directionChoice(entry, motion, direction) {
  if (!direction || direction === motion.defaultDirection || direction === 'horizontal') return {};
  if (entry.editable?.includes('direction') && motion.adaptDirections.includes(direction)) {
    return {content: {direction: direction === 'vertical' ? 'up' : direction}};
  }
  return {issue: `travels ${motion.defaultDirection}, requested ${direction}`};
}

function roleMatch(entries, roles, input) {
  const {fixed, moving, mentioned} = roles;
  const conflict = [...fixed].find(actor => moving.has(actor));
  if (conflict) return decision('missing', `The request asks for the ${conflict} to move and stay fixed in the same beat.`);
  if (!mentioned.has('photos') || !mentioned.has('heading')) return null;
  if (LOCAL_PHOTO_ACTION.test(input)) return null;
  const relational = /\b(?:under|over|through|behind)\b/.test(input);
  for (const [actor, motion] of Object.entries(PAIR)) {
    const movement = moving.get(actor);
    if (!movement || !(fixed.has(motion.fixed) || relational) || moving.size > 1) continue;
    const entry = entries.find(candidate => candidate.id === motion.id);
    if (!entry) continue;
    const compatible = /^(?:move|slide|sweep|shift|bring|ease|rise)$/.test(movement.verb);
    if (!compatible || avoidedTechniques(input).includes('slide')) continue;
    const {issue, content} = directionChoice(entry, motion, movement.direction);
    if (issue) {
      return decision('missing', `The nearest entry keeps the requested layers fixed, but it ${issue}.`, [], {
        candidates: [{id: entry.id, score: 0, signals: [actor, motion.fixed], issues: [issue]}],
      });
    }
    return matched(entry, input, [], content);
  }
  return null;
}

function indexEntry(entry) {
  const main = [entry.id, entry.title, entry.moves, ...(entry.intents ?? [])].join(' ');
  const examples = [entry.title, ...(entry.intents ?? [])].map(words);
  const techniqueDescription = [entry.title, entry.moves].join(' ');
  const negated = avoidedTechniques(techniqueDescription);
  return {
    entry,
    primary: new Set(words(main)),
    context: new Set(words([entry.fits, entry.notice, entry.fixed].join(' '))),
    moving: new Set(words(entry.moves)),
    actualMovers: briefRoles(entry.moves).moving,
    techniques: new Set(words(techniqueDescription).filter(word => !negated.includes(word))),
    fixed: new Set(words(entry.fixed)),
    examples,
    all: normalized([main, entry.fits, entry.notice].join(' ')),
  };
}

function rank(entries, input, roles) {
  const special = requestedSpecial(normalized(input));
  const forbidden = avoidedTechniques(input);
  const allWords = words(input).filter(word => !forbidden.includes(word));
  const queryWithoutNegation = new Set(allWords);
  const pairs = new Set(allWords.slice(1).map((word, index) => allWords[index] + ' ' + word));
  const indexed = entries.map(indexEntry);
  const counts = new Map([...queryWithoutNegation].map(word => [word, indexed.filter(record => record.primary.has(word)).length]));
  return indexed.map(({entry, primary, context, moving, fixed, examples, all, techniques, actualMovers}) => {
    let content;
    const movesActor = actor => actor === 'transcript' ? actualMovers.has(actor) : moving.has(stem(actor));
    const issues = [...special.filter(phrase => !all.includes(phrase)).map(phrase => `requires ${phrase}`),
      ...forbidden.filter(word => uses(techniques, word)).map(word => `uses ${word}`)];
    for (const actor of roles.fixed) {
      if (movesActor(actor) && (actor === 'transcript' || !fixed.has(stem(actor))))
        issues.push(`moves the requested fixed ${actor}`);
    }
    for (const [actor, movement] of roles.moving) {
      const actual = actualMovers.get(actor);
      if (!movesActor(actor)) issues.push(fixed.has(stem(actor))
        ? `fixes the requested moving ${actor}`
        : `does not describe a moving ${actor}`);
      if (actor === 'transcript' && actual && movement.direction && actual.direction !== movement.direction)
        issues.push(`does not describe the transcript moving ${movement.direction}`);
      if (TECHNIQUES.has(movement.verb) && !uses(moving, movement.verb)) issues.push(`requires ${movement.verb} on the ${actor}`);
      const photoPair = PAIR[actor];
      if (photoPair?.id !== entry.id) continue;
      const direction = directionChoice(entry, photoPair, movement.direction);
      if (direction.issue) issues.push(direction.issue);
      content = direction.content;
    }
    const signals = [...queryWithoutNegation].filter(word => primary.has(word));
    const distinctive = signals.filter(word => !GENERAL.has(word));
    const relevance = signals.reduce((score, word) => {
      const rarity = 1 + Math.log((indexed.length + 2) / ((counts.get(word) ?? 0) + 2));
      return score + (GENERAL.has(word) ? 0.7 : rarity);
    }, 0);
    const contextScore = [...queryWithoutNegation].filter(word => context.has(word) && !primary.has(word)).length * 0.28;
    const phraseScore = examples.reduce((best, example) => Math.max(best, example.slice(1)
      .filter((word, index) => pairs.has(example[index] + ' ' + word)).length * 1.75), 0);
    const assigned = [...roles.moving.keys()].filter(movesActor).length * 1.5
      + [...roles.fixed].filter(actor => fixed.has(stem(actor))).length * 1.2;
    const score = Math.round((relevance + contextScore + phraseScore + assigned) * 100) / 100;
    return {id: entry.id, score, signals, distinctive, issues, ...(content && {content})};
  }).filter(candidate => candidate.score > 0)
    .sort((a, b) => Number(Boolean(a.issues.length)) - Number(Boolean(b.issues.length)) || b.score - a.score || a.id.localeCompare(b.id));
}

function isHold(input, roles) {
  if (roles.moving.size) return false;
  return /^(?:just |please )?(?:still|fixed|steady)(?:$|[.!?]| (?:so|for|to|while|on)\b)/.test(input) || /\b(?:still|steady|fixed)\b/.test(input)
    && /\b(?:everything|whole|entire|both|all of it|frame|shot|screen|completely)\b/.test(input)
    || /\b(?:reading hold|time to read|long enough to read|(?:keep|hold|leave) .* while .* read)\b/.test(input);
}

function selectBeat(entries, request) {
  const input = normalized(request);
  const roles = briefRoles(request);
  const noMotion = /\b(?:without|no|avoid) (?:absolutely |any |extra |a |the )?(?:animation|motion|movement|transitions?)\b/;
  const prohibited = /^(?:please )?(?:not|avoid) (?:animate|move)\b/;
  const movement = /\b(?:slide|move|zoom|cut|reveal|tap|focus|fade|bounce|push|pull|scroll|change|shift|swipe|rotate|assemble|rise|dim|expand|shrink|drag|collapse|spill|shake|highlight|pinch|sharpen|switch|adjust|grow|reframe|bring|send|type)\w*\b/;
  const explicitHold = isHold(input, roles) || noMotion.test(input) || clauses(request).some(clause => prohibited.test(clause));
  const positiveClauses = clauses(request).map(clause => clause.replace(noMotion, '')
    .replace(/\b(?:not|without|no|avoid|never) (?:extra |any |a |the )?(?:animation|movement|animate|move|slide|zoom|cut|fade|bounce|rotate|scroll)\b/g, ''));
  if (explicitHold && !positiveClauses.some(clause => movement.test(clause))) {
    return decision('hold', 'A static reading hold preserves attention on the content and the requested fixed layers.');
  }
  if (/\bcarousel\b/.test(input) && !/\b(?:clip|swipe|photos|heading|card|loop|wrap|dots|next|slide|stack)\b/.test(input)) {
    return decision('missing', 'A carousel can move a strip, dismiss a top card, or switch pages. Specify the moving layer, what stays fixed, and how the next item appears.');
  }
  if (!requestedSpecial(input).length) {
    const route = roleMatch(entries, roles, input);
    if (route) return route;
  }
  const candidates = rank(entries, request, roles).slice(0, 5);
  const [first, second] = candidates.filter(candidate => !candidate.issues.length);
  const decisive = first && first.score >= 3.4 && first.distinctive.length >= 1 && first.signals.length >= 2
    && (!second || first.score - second.score >= Math.max(0.85, first.score * 0.12));
  if (decisive) return matched(entries.find(entry => entry.id === first.id), request, candidates, first.content);
  const reason = candidates.length && !first
    ? 'The nearest catalog entries violate a required motion technique or fixed-layer constraint.'
    : candidates.length
      ? 'The wording has close alternatives. Specify which layer moves, which layer stays fixed, and what the viewer should notice.'
      : 'The catalog has no motion with enough evidence to fit this request.';
  return decision('missing', reason, [], {candidates});
}

function knownComposite(entries, beats) {
  if (beats.length !== 2) return undefined;
  const [first, second] = beats.map(normalized);
  if (requestedSpecial(first).length || requestedSpecial(second).length) return undefined;
  const namedOnScreen = /\b(?:reply|message|text|handset|phone)\b/.test(first);
  const handsetLeaves = /\b(?:handset|phone) (?:leaves?|exits?|falls? off|falls? away|slide off|slide out|drops? out)\b/.test(first)
    && !/\b(?:off|out) (?:to )?(?:the )?right\b/.test(first);
  const physical = /\b(?:real|physical|prop|object|tin|item)\b/.test(first + ' ' + second);
  const tighterCut = /\bcut\b/.test(second) && /\b(?:closer|tighter|close up|closeup)\b/.test(second)
    && !avoidedTechniques(second).includes('cut');
  if (namedOnScreen && handsetLeaves && physical && tighterCut) {
    return entries.find(entry => entry.id === 'screen-to-physical-prop');
  }

  const isChat = /\b(?:bubble|message|text|composer|chat|draft)\b/.test(first + ' ' + second);
  const outgoing = /\b(?:send|outgoing)\b/.test(first) && !avoidedTechniques(first).includes('send');
  const incoming = /\b(?:reply|incoming|receive (?:a |the )?(?:message|text|bubble))\b/.test(second)
    && !/\b(?:not|without|never|no) (?:a |any )?(?:reply|answer|incoming|receive)\b/.test(second);
  const extra = /\b(?:emoji|reaction|react|gloss|crop|zoom|rotate|swipe|left|right|jump|spin|flash|payment)\b/.test(second);
  if (isChat && outgoing && incoming && !extra) return entries.find(entry => entry.composite && entry.id === 'conversation-handoff');
}

function attachmentStackChoice(entries, brief, beats) {
  const [first, ...rest] = beats.map(normalized);
  const frontSwipe = /\b(?:swipe|flick|peel)\b/.test(first) && /\b(?:front|top|foremost|lead)\b/.test(first);
  const nextAttachment = /\b(?:behind|stack|deck|under|next)\b/.test(first) && /\b(?:photos|attachment|attachments|stack)\b/.test(first);
  if (!frontSwipe || !nextAttachment || requestedSpecial(first).length || avoidedTechniques(first).includes('swipe')) return null;
  const repeatedBeat = /^(?:swipe|flick|peel)\b[^.!?]*?\bagain(?:\s*[,.!;]+\s*(?:(?:keep|hold|leave)\b.*)?)?\s*$/i;
  if (rest.some((_, index) => !repeatedBeat.test(beats[index + 1]))) return null;
  const entry = entries.find(candidate => candidate.id === 'messages-attachment-stack');
  if (!entry) return null;
  const repeated = rest.length > 0 || /\b(?:twice|two swipes|2 swipes|second swipe)\b/.test(first);
  const tooMany = rest.length > 1 || /\b(?:three|four|five|[3-9]) (?:swipes|times)\b/.test(first);
  if (tooMany || repeated && !entry.editable?.includes('swipes')) {
    return decision('missing', 'The attachment motion can expose one next card per swipe. This scene does not support the requested number of swipes.');
  }
  if (/\b(?:swipe right|swipe .* to the right)\b/.test(first) || briefRoles(brief).moving.has('composer')) {
    return decision('missing', 'The attachment stack dismisses its front card to the left while its surrounding composer stays fixed.');
  }
  const forbidden = avoidedTechniques(brief).find(word => uses(new Set(words(entry.moves)), word));
  if (forbidden) return decision('missing', `The nearest attachment motion uses ${forbidden}, which the request prohibits.`);
  return matched(entry, brief, [], repeated ? {swipes: 2} : {});
}

export function select(entries, request) {
  if (!Array.isArray(entries)) throw new TypeError('Pass the catalog entries as an array.');
  const brief = String(request ?? '').trim();
  const explicit = entries.find(entry => entry.id.toLowerCase() === brief.toLowerCase());
  if (explicit) return matched(explicit, brief);
  if (!brief) return decision('missing', 'Describe what moves, what stays fixed, and what the viewer should notice.');
  const beats = brief.split(/\b(?:and\s+then|followed\s+by|after\s+that|then)\b/i).map(beat => beat.trim()).filter(Boolean);
  const attachment = beats.length ? attachmentStackChoice(entries, brief, beats) : null;
  if (attachment) return attachment;
  const exact = entries.filter(entry => entry.intents?.some(intent => normalized(intent) === normalized(brief)));
  if (exact.length === 1) return matched(exact[0], brief);
  if (beats.length < 2) return selectBeat(entries, brief);
  const supportedComposite = knownComposite(entries, beats);
  if (supportedComposite) return matched(supportedComposite, brief);
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
