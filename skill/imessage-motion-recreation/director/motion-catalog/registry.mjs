import registry from './registry.json' with {type: 'json'};

export const entries = registry.entries;
const tokenize = value => String(value).toLowerCase().match(/[a-z0-9]+/g) ?? [];
const stop = new Set(['a','an','and','as','can','for','from','how','i','in','into','lets','me','of','someone','the','to','use','want','what','with','while','that','stays','stay','still']);
const terms = value => tokenize(value).filter(word => !stop.has(word));

// Ordinary-language neighbours for the motion vocabulary in this catalog.
// Only QUERY terms are expanded: a literal vocabulary hit always outranks a
// neighbouring-word hit.
const SYNONYMS = {
  photo: ['photos', 'picture', 'pictures', 'image', 'images', 'pic', 'pics', 'photograph'],
  scroll: ['scrolls', 'scrolling', 'pan', 'pans', 'panning', 'slide', 'slides', 'sliding', 'swipe', 'swipes', 'swiping', 'browse', 'browses', 'browsing', 'move', 'moves', 'moving'],
  horizontal: ['sideways', 'horizontally'],
  counter: ['count', 'counts', 'counting', 'numbers', 'number', 'digits', 'stat', 'stats', 'odometer', 'figures'],
  assemble: ['gather', 'gathers', 'gathering', 'converge', 'converges', 'converging', 'cluster', 'clusters', 'collect', 'montage', 'formation'],
  picker: ['pick', 'choose', 'select', 'option', 'options', 'choice', 'choices', 'slot', 'slots'],
  reply: ['response', 'answer', 'dots', 'indicator'],
  card: ['panel', 'sheet', 'surface'],
  list: ['rows', 'items', 'checklist', 'results'],
  message: ['bubble', 'chat', 'text'],
  send: ['sent', 'sending', 'share'],
  attachment: ['stack', 'bundle', 'pile'],
  grow: ['grows', 'grow', 'expands', 'expand', 'spring', 'springs', 'scale'],
  place: ['venue', 'restaurant', 'spot', 'location'],
  name: ['title', 'header', 'heading'],
  fixed: ['stays', 'static', 'stationary'],
  open: ['opens', 'opening', 'launch', 'launches'],
  device: ['devices', 'phone', 'phones', 'screens'],
  face: ['faces', 'avatar', 'avatars', 'people', 'contacts', 'portraits'],
  time: ['time', 'day', 'date', 'when'],
};
const neighbour = new Map();
for (const group of Object.values(SYNONYMS)) {
  for (const word of group) neighbour.set(word, new Set(group));
}
const expand = words => {
  const out = new Set(words);
  for (const word of words) for (const near of neighbour.get(word) ?? []) out.add(near);
  return out;
};

// Axis hints let "scrolling horizontally" separate a rail from a list.
const familyAxis = {rail: 'h', 'chip-rail': 'h', attachment: 'h', 'list-scroll': 'v', 'sheet-grid': 'v'};
const horizontalWords = new Set(['horizontal', 'horizontally', 'sideways', 'side', 'left', 'right']);
const verticalWords = new Set(['vertical', 'vertically', 'up', 'down', 'upward', 'downward']);
// Measured evidence should win a tie over a plausible adaptation.
const statusBonus = {measured: 1, 'source-informed': 0.5, 'evidence-gap': 0};

const searchable = entries.map(entry => {
  const literal = new Set(terms([
    entry.id, entry.title, entry.family ?? '', entry.description ?? '',
    entry.anatomy?.moving ?? '', entry.anatomy?.fixed ?? '',
    ...entry.queries
  ].join(' ')));
  const near = expand(literal);
  for (const word of literal) near.delete(word);
  return {entry, literal, near,
    phrases: entry.queries.map(query => terms(query).join(' '))};
});

export function getMotion(id) {
  return entries.find(entry => entry.id === id || entry.source?.caseId === id);
}

export function searchMotions(query) {
  const phrase = terms(query).join(' ');
  if (!phrase) return [];
  const exact = getMotion(query.trim().toLowerCase());
  if (exact) return [{entry: exact, matches: [exact.id], score: 100, tier: 'id'}];

  const tokens = [...new Set(phrase.split(' '))];
  const expanded = [...expand(tokens)].filter(token => !tokens.includes(token));
  const axis = tokens.some(t => horizontalWords.has(t)) ? 'h'
    : tokens.some(t => verticalWords.has(t)) ? 'v' : null;
  let results = searchable.flatMap(({entry, literal, near, phrases}) => {
    const direct = tokens.filter(token => literal.has(token));
    const nearHit = tokens.filter(token => near.has(token));
    const loose = expanded.filter(token => literal.has(token));
    const matches = [...new Set([...direct, ...nearHit, ...loose])];
    const phraseMatch = phrases.some(item => item === phrase || (item.includes(' ') && phrase.includes(item)));
    // A lone generic word such as "photos" can't choose UI or establish evidence.
    if (!phraseMatch && matches.length < Math.min(2, tokens.length)) return [];
    let score = direct.length * 3 + nearHit.length * 1.5 + loose.length * 0.5 + (phraseMatch ? 8 : 0)
      + (statusBonus[entry.status] ?? 0);
    const entryAxis = familyAxis[entry.family];
    if (axis && entryAxis) score += entryAxis === axis ? 3 : -2;
    return [{entry, matches, score}];
  }).sort((a, b) => b.score - a.score);
  if (!results.length) return results;
  const top = results[0].score;
  return results.filter(result => result.score >= Math.max(2.5, top * 0.3)).slice(0, 6);
}
