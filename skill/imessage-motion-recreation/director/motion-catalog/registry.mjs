import registry from './registry.json' with {type: 'json'};

export const entries = registry.entries;
const tokenize = value => String(value).toLowerCase().match(/[a-z0-9]+/g) ?? [];
const stop = new Set(['a','an','and','as','can','for','from','how','i','in','into','lets','me','of','someone','the','to','use','want','what','with']);
const terms = value => tokenize(value).filter(word => !stop.has(word));
const searchable = entries.map(entry => ({
  entry,
  phrases: entry.queries.map(query => terms(query).join(' ')),
  words: new Set(terms([entry.id, entry.title, ...entry.queries].join(' ')))
}));

export function getMotion(id) {
  return entries.find(entry => entry.id === id || entry.source?.caseId === id);
}

export function searchMotions(query) {
  const phrase = terms(query).join(' ');
  if (!phrase) return [];
  const exact = getMotion(query.trim().toLowerCase());
  if (exact) return [{entry: exact, matches: [exact.id], score: 100}];

  const tokens = [...new Set(phrase.split(' '))];
  return searchable.flatMap(({entry, phrases, words}) => {
    const matches = tokens.filter(token => words.has(token));
    const phraseMatch = phrases.some(item => item === phrase || (item.includes(' ') && phrase.includes(item)));
    // A lone generic word such as "photos" can't choose UI or establish evidence.
    if (!phraseMatch && matches.length < Math.min(2, tokens.length)) return [];
    const score = matches.length + (phraseMatch ? 8 : 0);
    return [{entry, matches, score}];
  }).sort((a, b) => b.score - a.score);
}
