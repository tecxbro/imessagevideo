import {entries as core} from './packs/core.mjs';

import {entries as handoff} from './packs/handoff.mjs';

export const entries = [
  ...core.map(entry => ({...entry, implementation: 'packs/core.mjs'})),
  ...handoff.map(entry => ({...entry, implementation: 'packs/handoff.mjs'})),
];
export const byId = new Map(entries.map(entry => [entry.id, entry]));
if (byId.size !== entries.length) throw Error('Motion IDs must be unique');

export const methods = ['pillow', 'html', 'gsap', 'remotion', 'motion-canvas'];
export const metadata = ({build, ...entry}) => entry;
