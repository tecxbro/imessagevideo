import {spawnSync} from 'node:child_process';
import {copyFileSync, existsSync, mkdirSync, readFileSync, realpathSync, writeFileSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {byId, search} from './search.mjs';

const library = fileURLToPath(new URL('./', import.meta.url));
const root = fileURLToPath(new URL('../../../../', import.meta.url));
const renderer = fileURLToPath(new URL('../../scripts/engines/render_pillow.py', import.meta.url));

function print(value) {
  console.log(JSON.stringify(value, null, 2));
}

function prepareOutput(filename) {
  if (!filename) throw new Error('Provide --out PATH.');
  const destination = path.resolve(filename);
  const dir = path.dirname(destination);
  mkdirSync(dir, {recursive: true});
  // The renderer resolves the scene path through directory symlinks.
  return path.join(realpathSync(dir), path.basename(destination));
}

function options(args, allowed) {
  const result = {};
  while (args.length) {
    const flag = args.shift();
    const name = flag.startsWith('--') ? flag.slice(2) : '';
    if (!allowed.includes(name) || Object.hasOwn(result, name)) {
      throw new Error(`Unexpected argument: ${flag}`);
    }
    if (name === 'source') {
      result.source = true;
    } else {
      const value = args.shift();
      if (!value || value.startsWith('--')) throw new Error(`Missing value for ${flag}.`);
      result[name] = value;
    }
  }
  return result;
}

function run(executable, args) {
  const child = spawnSync(executable, args, {stdio: ['ignore', process.stderr, 'inherit']});
  if (child.error) throw child.error;
  if (child.status !== 0) {
    throw new Error(`${executable} stopped with ${child.signal ?? `exit status ${child.status}`}.`);
  }
}

async function writeScene(entry, configName, destination) {
  const {buildCatalogScene} = await import('./blocks.mjs');
  const configFile = configName ? path.resolve(configName) : null;
  const config = JSON.parse(readFileSync(configFile ?? path.join(library, entry.defaults), 'utf8'));
  const configDirectory = path.dirname(configFile ?? path.join(library, entry.defaults));
  const scene = buildCatalogScene(entry.id, config);
  const rebase = layers => {
    for (const layer of layers) {
      if (layer.type === 'image' && layer.src && !layer.src.startsWith('data:')) {
        if (layer.src.includes('://')) throw new Error('Artwork must be a local file.');
        const source = path.resolve(configDirectory, layer.src);
        if (!existsSync(source)) throw new Error(`Artwork file is missing: ${source}`);
        layer.src = path.relative(path.dirname(destination), realpathSync(source));
      }
      if (layer.children) rebase(layer.children);
    }
  };
  rebase(scene.layers);
  writeFileSync(destination, JSON.stringify(scene, null, 2) + '\n');
}

export async function motionCommand(args) {
  const command = args.shift();
  if (!command || command === '--help') {
    console.log('motion search "describe the motion" | motion show ID | motion preview ID [--out VIDEO.mp4] [--source] | motion scene ID [--config FILE.json] --out SCENE.json | motion render ID [--config FILE.json] [--python PYTHON] --out VIDEO.mp4');
    return;
  }
  if (command === 'search') {
    const query = args.join(' ').trim();
    if (!query) throw new Error('Describe a motion to search for.');
    print(search(query));
    return;
  }
  if (!['show', 'preview', 'scene', 'render'].includes(command)) {
    throw new Error(`Unknown motion command: ${command}. Run motion --help.`);
  }
  const id = args.shift();
  const entry = byId.get(id);
  if (!entry) throw new Error(`Unknown motion: ${id ?? 'provide a catalog ID'}`);
  if (command === 'show') {
    options(args, []);
    const {signals, ...detail} = entry;
    print({
      ...detail,
      preview: path.join(library, entry.preview),
      defaults: path.join(library, entry.defaults),
      implementation: path.join(library, 'blocks.mjs')
    });
    return;
  }
  if (command === 'preview') {
    const opts = options(args, ['out', 'source']);
    if (opts.source) {
      const source = entry.evidence;
      if (!source.localMovie) throw new Error('This motion has no local source film interval. See motion show.');
      const movie = path.join(root, source.localMovie);
      if (!existsSync(movie)) throw new Error('Source film is missing. Run python3 tools/sync_library.py from the checkout root.');
      const out = prepareOutput(opts.out);
      if (path.extname(out).toLowerCase() !== '.mp4') throw new Error('Provide an .mp4 preview path.');
      if (out === movie) throw new Error('Choose an output path separate from the source film.');
      const [first, last] = source.framesInclusive;
      run('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', '-i', movie,
        '-map', '0:v:0', '-map_metadata', '-1', '-write_tmcd', '0', '-vf', `trim=start_frame=${first}:end_frame=${last + 1},setpts=PTS-STARTPTS`,
        '-an', '-fps_mode', 'passthrough', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out]);
      print({id, preview: out, framesInclusive: source.framesInclusive});
    } else {
      const stored = path.join(library, entry.preview);
      if (!existsSync(stored)) throw new Error(`Catalog preview is missing: ${entry.preview}`);
      const preview = opts.out ? prepareOutput(opts.out) : stored;
      if (preview !== stored) copyFileSync(stored, preview);
      print({id, preview, kind: 'editable-motion-preview'});
    }
    return;
  }
  const opts = options(args, command === 'render' ? ['config', 'out', 'python'] : ['config', 'out']);
  const out = prepareOutput(opts.out);
  const extension = command === 'render' ? '.mp4' : '.json';
  if (path.extname(out).toLowerCase() !== extension) throw new Error(`Provide a ${extension} output path.`);
  const scene = command === 'scene' ? out : out.slice(0, -4) + '.scene.json';
  if (opts.config && (existsSync(scene) ? realpathSync(scene) : scene) === realpathSync(opts.config)) throw new Error('Choose an output path separate from the config.');
  await writeScene(entry, opts.config, scene);
  if (command === 'render') {
    run(opts.python ?? 'python3', [renderer, '--scene', scene, '--out', out]);
  }
  print({id, scene, ...(command === 'render' && {video: out})});
}
