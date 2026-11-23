import {readFileSync} from 'node:fs';

export const catalog = JSON.parse(readFileSync(new URL('./catalog.json', import.meta.url), 'utf8'));
export const byId = new Map(catalog.entries.map(entry => [entry.id, entry]));

function normalize(text) {
  return text.normalize('NFKD').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
}

function rank(query, entry) {
  const words = ` ${normalize(query)} `;
  const matches = entry.signals.flatMap(({part, weight, phrases}) => {
    const phrase = phrases
      .filter(value => words.includes(` ${normalize(value)} `))
      .sort((a, b) => b.length - a.length)[0];
    return phrase ? [{part, phrase, weight}] : [];
  });
  return {
    id: entry.id,
    title: entry.title,
    score: matches.reduce((total, match) => total + match.weight, 0),
    matches,
    moves: entry.moves,
    staysFixed: entry.staysFixed,
    preview: entry.preview
  };
}

export function search(query) {
  const candidates = catalog.entries.map(entry => rank(query, entry))
    .filter(candidate => candidate.score > 0)
    .sort((a, b) => b.score - a.score || a.id.localeCompare(b.id));
  const [first, second] = candidates;
  // Generic words can return candidates. A selection needs an independent
  // description of a distinctive object or behavior and a clear lead.
  const decisive = first?.matches.some(match => match.weight >= 4);
  const matched = decisive && first.score >= 5 && first.score - (second?.score ?? 0) >= 2;
  const status = matched ? 'match' : first ? 'ambiguous' : 'no-match';
  const question = status === 'ambiguous' ? 'Which object moves, and what stays fixed?' : undefined;
  return {query, status, selected: matched ? first.id : null, ...(question && {question}), candidates};
}
