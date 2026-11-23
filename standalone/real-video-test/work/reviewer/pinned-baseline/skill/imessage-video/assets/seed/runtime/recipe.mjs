import {readFileSync} from 'node:fs';
import {byId, entries} from './motion/catalog.mjs';
import {buildMotion} from './motion/scene.mjs';
import {select} from './motion/select.mjs';

// JSON stdin keeps arbitrary text, filenames and non-ASCII copy intact.
try {
  const input = JSON.parse(readFileSync(0, 'utf8'));
  let result;
  if (input.action === 'suggest') {
    result = select(entries, input.request);
  } else if (input.action === 'scene') {
    const entry = byId.get(input.id);
    if (!entry) throw new Error('Unknown motion: ' + input.id);
    result = buildMotion(entry, input.content, input.options);
  } else {
    throw new Error('Expected suggest or scene.');
  }
  process.stdout.write(JSON.stringify(result));
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
