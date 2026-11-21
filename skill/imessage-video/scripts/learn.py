#!/usr/bin/env python3
"""Register, search, edit and replay measured declarative motion scenes."""
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

import frames

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / 'assets/seed/runtime/scripts/engines/render_pillow.py'
FRAMES = ROOT / 'scripts/frames.py'
ENGINES = {'pillow': (ENGINE,), 'svg': tuple(ENGINE.with_name(name) for name in
           ('render_svg.mjs', 'common.mjs', 'rasterize_svg.py'))}
ID_PATTERN = re.compile(r'[a-z0-9][a-z0-9-]{0,79}')
IMAGE_TYPES = {'.png': 'PNG', '.jpg': 'JPEG', '.jpeg': 'JPEG', '.webp': 'WEBP'}
FONT_TYPES = {'.ttf', '.otf'}
LAYERS = {'group', 'text', 'rect', 'image', 'circle', 'path'}
NUMERIC = set('x y width height radius originX originY scaleX scaleY rotation opacity strokeWidth blur fontSize lineHeight letterSpacing start end'.split())
ENUMS = {'textAnchor': {'start','middle','end'}, 'textDecoration': {'none','underline','line-through'},
         'preserveAspectRatio': {'none','xMidYMid meet','xMidYMid slice'}, 'fontStyle': {'normal','italic','oblique'}}
PAINT = re.compile(r'[\w#.,() %+-]+')
ASSET_KINDS = {'authored', 'licensed-independent', 'user-supplied-independent'}


def require(test, message):
    if not test:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n')


def digest(path):
    with Path(path).open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def slug(text):
    require(isinstance(text, str) and ID_PATTERN.fullmatch(text), 'ID must be a lowercase slug')
    return text


SEARCH_STOPWORDS = set('a an the to of in on at for as by via from with and or but this that these those my our your its it is are was were should would can could please me make show find give use using want video videos motion motions effect effects animation animations scene scenes something where which what while through into then'.split())


def words(value):
    return set(re.findall(r'[a-z0-9]+', value.casefold())) - SEARCH_STOPWORDS


def local_file(root, name, assets=False):
    rel = Path(name)
    require(not rel.is_absolute() and '..' not in rel.parts and rel.parts, 'Expected a relative project file')
    require(not assets or rel.parts[0] == 'assets', 'Scene assets must live under assets/')
    path = root / rel
    require(path.resolve().is_relative_to(root.resolve()) and path.is_file(), f'Missing or external file: {name}')
    return path


def scalar(v):
    return type(v) in (str, int, float, bool) and (type(v) != float or math.isfinite(v))


def bindings(scene, recipe, overrides):
    for name, value in overrides.items():
        require(name in recipe['parameters'], f'Unknown parameter: {name}')
        require(scalar(value), 'Use a string, boolean or finite number')
        path = recipe['parameters'][name]
        require(isinstance(path, str) and path.startswith('/'), f'Invalid parameter pointer: {name}')
        parts = [p.replace('~1', '/').replace('~0', '~') for p in path[1:].split('/')]
        require(not any(p in ('src','type','id','d','fonts','gradients') for p in parts), 'Use asset replacement for media, and retain scene structure')
        parent = scene
        for field in parts[:-1]:
            parent = parent[int(field)] if isinstance(parent, list) else parent[field]
        field = int(parts[-1]) if isinstance(parent, list) else parts[-1]
        old = parent[field]
        same_type = type(old) is type(value) or (type(old) in (int,float) and type(value) in (int,float))
        require(scalar(old) and same_type, f'Type mismatch for {name}')
        parent[field] = value


def safe_value(prop, val):
    if prop in NUMERIC:
        require(type(val) in (int,float) and math.isfinite(val), f'Expected finite number for {prop}')
    elif prop in ENUMS:
        require(isinstance(val,str) and val in ENUMS[prop], f'Unknown {prop} value')
    elif prop == 'fontWeight':
        require(re.fullmatch(r'(normal|bold|[1-9]00)',str(val)), 'Unsupported font weight')
    elif prop in ('fontFamily','family'):
        require(isinstance(val,str) and re.fullmatch(r'[\w .,\-]+',val), 'Invalid font family')
    elif prop in ('fill','stroke','color','background'):
        require(isinstance(val,str) and PAINT.fullmatch(val) and 'url(' not in val.lower(), 'Use literal paint colors')
    elif prop == 'text':
        require(isinstance(val,str), 'Text must be a string')
    else:
        raise ValueError(f'Unsupported animated or styling property: {prop}')


def check_scene(scene, folder, assets):
    require(type(scene.get('width')) == int and type(scene.get('height')) == int and min(scene['width'],scene['height']) > 0, 'Invalid canvas')
    require(scene['fps'] > 0 and scene['duration'] > 0, 'Invalid scene timebase')
    require(isinstance(scene.get('layers'), list) and scene['layers'], 'A scene requires layers')
    require(not scene.get('gradients'), 'Learned path scenes accept solid paints only')
    refs = set()
    ids = set()
    def walk(node):
        require(node['type'] in LAYERS, f"Unsupported layer: {node['type']}")
        name = node.get('id')
        require(isinstance(name, str) and name and name not in ids, f'Empty or duplicate layer ID: {name}')
        ids.add(name)
        if node['type'] == 'image':
            refs.add(node['src'])
        for prop, val in node.items():
            if prop in NUMERIC or prop in ENUMS or prop in ('fontWeight','fontFamily','fill','stroke','text'):
                safe_value(prop,val)
        for field in ('clip','shadow'):
            for prop, val in node.get(field,{}).items():
                require(prop in NUMERIC or (field == 'shadow' and prop == 'color'), f'Invalid {field} property')
                safe_value(prop,val)
        for prop,keys in node.get('keyframes', {}).items():
            require(keys and isinstance(keys,list),'Keyframe tracks cannot be empty')
            for point in keys:
                require(type(point.get('t')) in (int,float) and math.isfinite(point['t']),'Invalid keyframe time')
                safe_value(prop,point['value'])
        for child in node.get('children', []):
            walk(child)
    for layer in scene['layers']:
        walk(layer)
    if 'background' in scene:
        safe_value('background',scene['background'])
    for f in scene.get('fonts', []):
        safe_value('family',f['family'])
        if 'weight' in f: safe_value('fontWeight',f['weight'])
        if 'style' in f: safe_value('fontStyle',f['style'])
        refs.add(f['src'])
    require(refs == set(assets), 'Declare every image and font exactly once in assets')
    for name, record in assets.items():
        file = local_file(folder, name, assets=True)
        require(record.get('kind') in ASSET_KINDS and record.get('credit'), f'Independent asset provenance required: {name}')
        ext = file.suffix.lower()
        if ext in IMAGE_TYPES:
            with file.open('rb') as f:
                require(b'<svg' not in f.read(300).lower(), 'SVG assets are not accepted')
            with Image.open(file) as im:
                require(im.format == IMAGE_TYPES[ext] and getattr(im,'n_frames',1)==1, 'Only static raster image assets are accepted')
                im.verify()
        else:
            require(ext in FONT_TYPES and file.read_bytes()[:4] in (b'OTTO',b'\0\1\0\0'), 'Expected a static image or an sfnt font')
    return ids


def bundle_files(folder):
    return {p.relative_to(folder).as_posix(): digest(p) for p in sorted(folder.rglob('*')) if p.is_file() and p != folder/'manifest.json'}


def renderer_files(recipe):
    name = recipe.get('renderer','pillow')
    require(isinstance(name,str) and name in ENGINES, 'Supported learned scene renderers: pillow or svg')
    return ENGINES[name]


def render_options(recipe):
    if 'antialias' not in recipe:
        return []
    scale = recipe['antialias']
    require(recipe.get('renderer', 'pillow') == 'pillow' and type(scale) is int and 1 <= scale <= 4,
            'Antialias needs a Pillow scale of 1–4')
    return ['--aa', str(scale)]


def render(folder, recipe, overrides, replacements, out, project=None):
    with tempfile.TemporaryDirectory(prefix='motion-replay-') as temp:
        clean = Path(temp)
        scene = read(folder/'scene.json')
        for name in recipe['assets']:
            src = local_file(folder, name, assets=True)
            target = clean / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(replacements.get(name, src), target)
        require(set(replacements) <= set(recipe['assets']), 'Asset replacement targets must already be declared')
        bindings(scene, recipe, overrides)
        check_scene(scene, clean, recipe['assets'])
        write(clean/'scene.json',scene)
        files = renderer_files(recipe)
        options = render_options(recipe)
        runner = ['node',str(files[0])] if recipe.get('renderer')=='svg' else [sys.executable,'-I',str(files[0])]
        env = {**os.environ, 'IMESSAGE_VIDEO_PYTHON': sys.executable}
        subprocess.run([*runner,'--scene',str(clean/'scene.json'),'--out',str(out), *options],
                       cwd=clean,env=env,check=True,stdout=sys.stderr)
        if project:
            shutil.copytree(clean, project)
            runtime = project/'renderer'
            runtime.mkdir()
            for file in files:
                shutil.copyfile(file,runtime/file.name)
            write(project/'replay.json',{'renderer':recipe.get('renderer','pillow'),
                 'command':(['node'] if recipe.get('renderer')=='svg' else ['python3','-I']) +
                    ['renderer/'+files[0].name, '--scene','scene.json','--out','render.mp4', *options],
                 'renderer_files':{f.name:digest(f) for f in files},'overrides':overrides,
                 'asset_replacements':{k:digest(file) for k,file in replacements.items()}})


def compare(reference, output, evidence, recipe):
    checks = recipe['checks']
    command = [sys.executable, str(FRAMES), str(reference), str(output), '--out', str(evidence),
               '--require-structure-match', '--max-pts-error-ms', str(checks.get('max_pts_error_ms', 0)),
               '--max-mae', str(checks['max_mae'])]
    for name, rect in checks['rois'].items():
        require(re.fullmatch(r'[A-Za-z0-9_.-]+', name) and len(rect)==4 and all(type(n)==int for n in rect), 'Invalid named ROI')
        command += ['--roi', name + ':' + ','.join(map(str,rect))]
    result = subprocess.run(command, stdout=sys.stderr)
    require((evidence/'report.json').is_file(), 'Comparison failed to produce a report')
    return result.returncode, read(evidence/'report.json')


def peak_changes(path, rois, meta):
    size = (meta['width'],meta['height'])
    baseline = {}
    peaks = dict.fromkeys(rois, 0.)
    with frames.decoder(path) as stream:
        for index in range(meta['frame_count']):
            frame = frames.read_frame(stream,size,index,path)
            for name,(x,y,w,h) in rois.items():
                cut = np.asarray(frame.crop((x,y,x+w,y+h)),dtype=np.int16)
                if not index:
                    baseline[name] = cut
                else:
                    peaks[name] = max(peaks[name], float(np.abs(cut-baseline[name]).mean()))
    return peaks


def validate_recipe(recipe, scene, root):
    slug(recipe['id'])
    renderer_files(recipe)
    render_options(recipe)
    for name in ('title','description'):
        require(isinstance(recipe.get(name),str) and recipe[name].strip(), f'Missing {name}')
    for name in ('fits','avoid','moving','fixed','tags'):
        items = recipe.get(name)
        require(isinstance(items,list) and (items or name in ('fixed','tags')) and all(isinstance(x,str) and x.strip() for x in items), f'Invalid {name}')
    require(isinstance(recipe.get('parameters'),dict) and recipe['parameters'], 'Declare editable JSON pointers')
    require(isinstance(recipe.get('assets'), dict), 'Declare assets ({} for a generated scene)')
    ids = check_scene(scene, root, recipe['assets'])
    require(set(recipe['moving']+recipe['fixed']) <= ids, 'moving/fixed must name actual layer IDs')
    require(not set(recipe['moving']) & set(recipe['fixed']), 'A layer cannot both move and stay fixed')
    for key,pointer in recipe['parameters'].items():
        require(ID_PATTERN.fullmatch(key) and isinstance(pointer,str) and pointer.startswith('/'), 'Invalid parameter name or pointer')
        v = scene
        for part in pointer[1:].split('/'):
            part = part.replace('~1','/').replace('~0','~')
            v = v[int(part)] if isinstance(v,list) else v[part]
        bindings(scene, recipe, {key:v})
    source = recipe['source']
    require(isinstance(source.get('label'),str) and source['label'].strip() and type(source.get('start_frame'))==int and source['start_frame']>=0,'Describe the original and first frame of the supplied comparison clip')
    require(isinstance(source.get('observation'),str) and source['observation'].strip(),'Record measured movement/timing evidence')
    checks = recipe['checks']
    require(checks.get('rois') and type(checks['max_mae']) in (int,float) and math.isfinite(checks['max_mae']) and 0<=checks['max_mae']<255, 'Set named moving ROIs and a finite per-frame pixel tolerance')
    require(checks.get('negative_control',{}).get('set') and checks['negative_control'].get('reason'), 'Declare a deliberate motion mistake and why the ROI must catch it')
    require(isinstance(checks.get('reason'),str) and checks['reason'].strip(), 'Explain the comparison tolerance and regions')


@contextmanager
def locked(library):
    with (library/'.publish.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def verify(folder):
    manifest = read(folder/'manifest.json')
    require(bundle_files(folder) == manifest['files'], f'Integrity check failed for {folder.name}')
    pinned = manifest.get('renderer_files')
    if pinned:
        actual = {f.name:digest(f) for f in renderer_files(read(folder/'recipe.json'))}
        require(actual == pinned, 'The saved recipe uses a different renderer version. Restore that renderer or re-verify the entry before replay.')
    return manifest


def prepare_clip(reference, evidence, recipe, selection=None, crop=None):
    source = recipe['source']
    claimed = source.pop('original_sha256', None)
    if not selection and not crop:
        clip = evidence/('reference' + reference.suffix.lower())
        shutil.copyfile(reference, clip)
        if claimed:
            require(claimed == digest(clip), 'For a measured excerpt of another file use --frames on the original')
            source['original_sha256'] = claimed
        return clip
    require(selection and re.fullmatch(r'\d+:\d+',selection), 'Use --frames FIRST:EXCLUSIVE_END with a native capture')
    first,last = map(int,selection.split(':'))
    require(last > first and first==source['start_frame'],'Frame window must agree with source.start_frame')
    source_hash = digest(reference)
    require(not claimed or claimed==source_hash,'Original SHA-256 mismatch')
    source.update(original_sha256=source_hash,end_frame_exclusive=last)
    filters = [f'trim=start_frame={first}:end_frame={last}']
    if crop:
        require(re.fullmatch(r'\d+,\d+,\d+,\d+',crop),'Crop syntax is X,Y,W,H in native pixels')
        x,y,w,h = map(int,crop.split(','))
        require(w>0 and h>0,'Empty crop')
        geom = subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','json',str(reference)],text=True)
        bounds = json.loads(geom)['streams'][0]
        require(x+w<=bounds['width'] and y+h<=bounds['height'],'Crop is outside the source')
        filters.append(f'crop={w}:{h}:{x}:{y}:exact=1')
        source['crop_xywh']=[x,y,w,h]
    filters.append('setpts=PTS-STARTPTS')
    # NUT preserves finer CFR timestamps than Matroska's millisecond clock.
    clip = evidence/'reference.nut'
    subprocess.run(['ffmpeg','-nostdin','-v','error','-xerror','-noautorotate','-i',str(reference),'-map','0:v:0','-vf',','.join(filters),'-an','-sn','-dn','-c:v','ffv1','-fps_mode','passthrough',str(clip)],check=True)
    require(digest(reference)==source_hash,'Source changed during measurement')
    return clip


def register(library, path, reference, selection=None, crop=None):
    recipe = read(path)
    root = path.parent
    source_scene = local_file(root, recipe.get('scene','scene.json'))
    scene = read(source_scene)
    validate_recipe(recipe, scene, root)
    entries = library/'entries'
    entries.mkdir(parents=True, exist_ok=True)
    require(reference.is_file(), 'Missing measured reference clip')
    with tempfile.TemporaryDirectory(dir=library, prefix='.register-') as staging:
        folder = Path(staging)/'entry'
        evidence = folder/'evidence'
        evidence.mkdir(parents=True)
        write(folder/'scene.json', scene)
        for name in recipe['assets']:
            dest = folder/name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(local_file(root,name,assets=True),dest)
        scene_key = hashlib.sha256(json.dumps(bundle_files(folder), sort_keys=True).encode()).hexdigest()
        recipe['scene'] = 'scene.json'
        clip = prepare_clip(reference,evidence,recipe,selection,crop)
        recipe['source']['clip_sha256'] = digest(clip)
        recipe['source']['comparison_clip'] = clip.relative_to(folder).as_posix()
        write(folder/'recipe.json',recipe)
        render(folder, recipe, {}, {}, folder/'preview.mp4')
        code, report = compare(clip, folder/'preview.mp4', evidence/'comparison', recipe)
        require(code == 0 and report['structure_within_tolerance'] and report['limits_passed'] is True and report['compared_frames']>=2, 'Replay failed frame/clock/region comparison; no entry published')
        if selection:
            first,last = map(int,selection.split(':'))
            require(report['compared_frames']==last-first,'Requested window extends beyond the available original footage')
        require(report['inputs']['source']['sha256']==digest(clip) and report['inputs']['output']['sha256']==digest(folder/'preview.mp4'), 'Comparison did not measure the saved files')
        levels = {role:peak_changes(f,recipe['checks']['rois'],report['inputs'][role]) for role,f in
                  [('source',clip),('output',folder/'preview.mp4')]}
        require(any(min(levels['source'][name], levels['output'][name]) >= 1 for name in levels['source']),
                'No named ROI shows a measurable movement in both source and replay; tighten the ROI or fix the scene')
        write(evidence/'measured-change.json',levels)
        control = evidence/'negative.mp4'
        render(folder, recipe, recipe['checks']['negative_control']['set'], {}, control)
        code, negative = compare(clip, control, evidence/'control', recipe)
        require(code != 0 and negative['structure_within_tolerance'] and negative['limits_passed'] is False and negative['compared_frames']==report['compared_frames'], 'Deliberate mistake was not detected on the same frame clock; no entry published')
        require(negative.get('failures') and any('mae' in str(x).lower() for x in negative['failures']), 'Control did not produce a measured pixel failure')
        roi_names = recipe['checks']['rois']
        require(any(negative['metrics'][name]['max_frame_mae'] > recipe['checks']['max_mae']
                    and min(levels['source'][name],levels['output'][name])>=1 for name in roi_names),
                'Negative control must break a region that actually moves in the real and reconstructed clips')
        for report_data, report_dir, result in [(report,'comparison',folder/'preview.mp4'),(negative,'control',control)]:
            report_data['inputs']['source']['path'] = clip.relative_to(folder).as_posix()
            report_data['inputs']['output']['path'] = result.relative_to(folder).as_posix()
            write(evidence/report_dir/'report.json', report_data)
        # The renderer's optional sidecar refers to its scratch checkout. Replace
        # temporary machine paths with the canonical paths needed for a replay.
        for movie in (folder/'preview.mp4',control):
            sidecar = Path(str(movie) + '.render.json')
            if sidecar.is_file():
                log = read(sidecar)
                log['scene'] = 'scene.json'
                log['out'] = movie.relative_to(folder).as_posix()
                if movie == control:
                    log['parameter_overrides'] = recipe['checks']['negative_control']['set']
                write(sidecar,log)
        for output in (folder/'preview.mp4', control):
            sidecar = output.with_name(output.name+'.render.json')
            if sidecar.is_file():
                build = read(sidecar)
                build['scene'] = 'scene.json'
                build['out'] = output.relative_to(folder).as_posix()
                write(sidecar, build)
        write(folder/'manifest.json', {'schema':1,'scene_sha256':scene_key,'renderer_files':{f.name:digest(f) for f in renderer_files(recipe)},'files':bundle_files(folder)})
        destination = entries/recipe['id']
        with locked(library):
            if destination.exists():
                old = verify(destination)
                if old['scene_sha256']==scene_key and read(destination/'recipe.json') == recipe and old.get('renderer_files')==read(folder/'manifest.json')['renderer_files']:
                    return destination
                raise ValueError(f'Already registered with other evidence or edits: {recipe["id"]}. Use a new versioned ID.')
            for candidate in entries.iterdir():
                if candidate.is_dir() and read(candidate/'manifest.json')['scene_sha256']==scene_key:
                    raise ValueError(f'This scene is already registered as {candidate.name}')
            folder.rename(destination)
        return destination


def summary(folder):
    r = read(folder/'recipe.json')
    keys = ('id','title','description','fits','avoid','moving','fixed','parameters','tags','source')
    return {**{k:r[k] for k in keys},'renderer':r.get('renderer','pillow'),'verified':'frame-compared','preview':str(folder/'preview.mp4'),
            'scene':str(folder/'scene.json'),'evidence':str(folder/'evidence/comparison/report.json'),'still':str(folder/'evidence/comparison/worst.png')}


def library_path(library=None):
    return Path(library or os.getenv('IMESSAGE_VIDEO_MOTION_LIBRARY') or ROOT/'assets/library').expanduser().resolve()


def show(library, motion_id):
    folder = library_path(library)/'entries'/slug(motion_id)
    verify(folder)
    return summary(folder)


def search(library=None, query=''):
    library = library_path(library)
    if query.strip() and ID_PATTERN.fullmatch(query.strip()) and (library/'entries'/query.strip()/'recipe.json').is_file():
        return [summary(library/'entries'/query.strip())]
    tokens = words(query)
    if query.strip() and not tokens:
        return []
    hits = []
    for folder in sorted((library/'entries').glob('*')):
        if not folder.is_dir(): continue
        item = summary(folder)
        positive = words(' '.join([item['id'],item['title'],item['description'],*item['tags'],*item['fits'],*item['moving'],*item['fixed']]))
        primary = words(item['title']+' '+' '.join(item['tags']))
        matches = len(tokens & positive) + len(tokens & primary)
        if not tokens or matches:
            hits.append((matches,item))
    return [item for _,item in sorted(hits,key=lambda row:(-row[0],row[1]['id']))]


def pairs(items, parse):
    result = {}
    for item in items:
        name, sep, value = item.partition('=')
        require(sep and name not in result,'Expected unique name=value overrides')
        result[name] = parse(value)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--library', type=Path, default=None)
    sub = p.add_subparsers(dest='cmd',required=True)
    reg = sub.add_parser('register')
    reg.add_argument('candidate', type=Path)
    reg.add_argument('--reference', type=Path, required=True)
    reg.add_argument('--frames', help='Original first:exclusive-end frame range')
    reg.add_argument('--crop', help='Native X,Y,W,H for a local motion study')
    find = sub.add_parser('list')
    find.add_argument('words', nargs='*')
    find.add_argument('--json', action='store_true')
    sub.add_parser('show').add_argument('id')
    play = sub.add_parser('replay')
    play.add_argument('id')
    play.add_argument('--out', type=Path, required=True)
    play.add_argument('--set', action='append', default=[])
    play.add_argument('--asset', action='append', default=[])
    play.add_argument('--project', type=Path)
    args = p.parse_args()
    library = library_path(args.library)
    if args.cmd=='register':
        saved = register(library,args.candidate.resolve(),args.reference.resolve(),args.frames,args.crop)
        print(json.dumps(summary(saved),indent=2))
        return
    if args.cmd=='list':
        hits = search(library,' '.join(args.words))
        print(json.dumps(hits,indent=2) if args.json else '\n'.join(row['id']+'  '+row['title'] for row in hits))
        return
    folder = library/'entries'/slug(args.id)
    manifest = verify(folder)
    if args.cmd=='show':
        print(json.dumps(summary(folder),indent=2))
        return
    out = args.out.resolve()
    require(out.suffix.lower()=='.mp4' and not out.exists() and not out.is_relative_to(library), 'Use a new MP4 path outside the catalog')
    proj = args.project.resolve() if args.project else None
    require(not proj or (not proj.exists() and not proj.is_relative_to(library) and not out.is_relative_to(proj)), 'Use a new project directory outside the catalog, separate from the output')
    expected = {f.name:digest(f) for f in renderer_files(read(folder/'recipe.json'))}
    recorded = manifest.get('renderer_files',{ENGINE.name:manifest.get('renderer_sha256')})
    require(expected==recorded,'Bundled renderer changed; revalidate this saved motion before replay')
    out.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=out.parent,prefix='.replay-') as stage:
        film = Path(stage)/'output.mp4'
        editable = Path(stage)/'editable' if proj else None
        render(folder,read(folder/'recipe.json'),pairs(args.set,json.loads),pairs(args.asset,lambda a:Path(a).resolve()),film,editable)
        if proj:
            proj.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(editable,proj)
        os.link(film,out)
    print(out)


if __name__=='__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, IndexError, subprocess.CalledProcessError) as exc:
        sys.exit(f'Motion library: {exc}')
