import {readFileSync} from 'node:fs';
import {entries as core} from './packs/core.mjs';

import {entries as handoff} from './packs/handoff.mjs';

import {entries as conversation} from './packs/conversation.mjs';
import {entries as editorial} from './packs/editorial.mjs';
import {entries as inherited} from './packs/inherited.mjs';
import {entries as media} from './packs/media.mjs';

import {entries as feeds} from './packs/feeds.mjs';

import {entries as direction} from './packs/direction.mjs';

const packs = {core, handoff, conversation, editorial, inherited, media, feeds, direction};
export const entries = Object.entries(packs).flatMap(([name, entries]) =>
  entries.map(entry => ({...entry, implementation: `packs/${name}.mjs`})));
export const byId = new Map(entries.map(entry => [entry.id, entry]));
if (byId.size !== entries.length) throw Error('Motion IDs must be unique');

export const methods = ['pillow', 'html', 'gsap', 'remotion', 'motion-canvas'];
export const metadata = ({build, ...entry}) => entry;

let published;
export function describe(entry) {
  if (!published) {
    try {
      const catalog = JSON.parse(readFileSync(new URL('./catalog.json', import.meta.url), 'utf8'));
      published = new Map(catalog.entries.map(row => [row.id, row]));
    } catch (error) {
      if (error.code !== 'ENOENT') throw error;
      published = new Map();
    }
  }
  return published.get(entry.id) ?? metadata(entry);
}
