#!/usr/bin/env python3
"""Create a portable final review, thirty videos, scene sources and skill archive."""
from pathlib import Path
import argparse,hashlib,json,os,shutil,tempfile,zipfile

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'delivery-package'
METHODS=('remotion','gsap','html','pillow','motion-canvas')
MEDIA_SUFFIXES={'.mp4','.png','.jpg','.jpeg','.zip','.woff','.woff2','.otf','.ttf'}


def sha(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as source:
        for chunk in iter(lambda:source.read(1024*1024),b''):digest.update(chunk)
    return digest.hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


class Stage:
    """Fresh temporary stage; links are allowed only for declared frozen files."""
    def __init__(self,path,link_stage=False):
        self.root=Path(path).absolute()
        if self.root.is_symlink():raise ValueError('Stage must not be a symlink')
        self.root=self.root.resolve()
        for area in ('outputs','deliverables','references','skill','engines','shared','verification','figma'):
            if self.root.is_relative_to((ROOT/area).resolve()):
                raise ValueError('Stage must be outside copied input trees: '+str(self.root))
        if self.root.exists() and (not self.root.is_dir() or any(self.root.iterdir())):
            raise ValueError('Stage must be fresh and empty; choose a unique --stage path: '+str(self.root))
        self.root.mkdir(parents=True,exist_ok=True)
        self.link_stage=link_stage

    def target(self,path):
        path=Path(path)
        if not path.is_absolute():path=self.root/path
        if not path.resolve().is_relative_to(self.root):raise ValueError('Stage path escapes its root: '+str(path))
        path.parent.mkdir(parents=True,exist_ok=True)
        return path

    def copy(self,source,destination,*,immutable=False):
        source=Path(source).resolve(strict=True);destination=self.target(destination)
        if destination.exists():
            if not destination.is_file() or sha(destination)!=sha(source):
                raise ValueError('Existing staged file has different bytes: '+str(destination))
            return str(destination)
        if self.link_stage and immutable:
            # A different filesystem must fail explicitly, not silently consume
            # the independent-copy disk budget that link mode was chosen to save.
            os.link(source,destination)
        else:
            descriptor,temporary=tempfile.mkstemp(prefix='.copy-',dir=destination.parent)
            os.close(descriptor)
            try:shutil.copy2(source,temporary);os.replace(temporary,destination)
            finally:Path(temporary).unlink(missing_ok=True)
        return str(destination)

    def copy_function(self,source,destination):
        return self.copy(source,destination,immutable=Path(source).suffix.lower() in MEDIA_SUFFIXES)

    def tree(self,source,destination):
        source=Path(source)
        if self.root.is_relative_to(source.resolve()):raise ValueError('Stage cannot be inside a copied source tree')
        shutil.copytree(source,self.target(destination),dirs_exist_ok=True,copy_function=self.copy_function)

    def text(self,destination,value):
        destination=self.target(destination)
        descriptor,temporary=tempfile.mkstemp(prefix='.generated-',dir=destination.parent)
        try:
            with os.fdopen(descriptor,'w') as output:output.write(value)
            # Replaces the stage directory entry, including an existing hardlink;
            # never opens a linked input inode for truncation.
            os.replace(temporary,destination)
        finally:Path(temporary).unlink(missing_ok=True)

    def json(self,destination,value):
        self.text(destination,json.dumps(value,indent=2)+'\n')


def export_scene(source,destination,stage):
    source=Path(source).resolve();destination=Path(destination)
    raw=source.read_bytes();digest=hashlib.sha256(raw).hexdigest();scene=json.loads(raw);assets=[];seen={}
    def asset(value):
        if value.startswith('data:'):return
        if value.startswith(('http://','https://')):raise ValueError('Remote runtime asset '+value)
        if Path(value).is_absolute() or '..' in Path(value).parts:
            raise ValueError('Final canonical runtime asset must be portable: '+value)
        if value not in seen:
            original=(source.parent/value).resolve();asset_hash=sha(original);target=stage.target(destination/value)
            if target.exists() and sha(target)!=asset_hash:
                raise ValueError('Existing canonical asset has different bytes: '+str(target))
            stage.copy(original,target,immutable=True)
            seen[value]={'file':value,'sha256':asset_hash,'bytes':original.stat().st_size}
        assets.append(seen[value])
    def walk(layers):
        for layer in layers:
            if layer.get('src'):asset(layer['src'])
            for key in layer.get('keyframes',{}).get('src',[]):asset(key['value'])
            walk(layer.get('children',[]))
    walk(scene['layers'])
    for font in scene.get('fonts',[]):asset(font['src'])
    # Never serialize the parsed object: the delivered canonical must preserve
    # the exact frozen bytes attested by all five rendered videos.
    if sha(source)!=digest:raise ValueError('Canonical changed during export: '+str(source))
    stage.copy(source,destination/'scene.json',immutable=True)
    portable_hash=sha(stage.target(destination/'scene.json'))
    if portable_hash!=digest:raise ValueError('Canonical bytes changed during export')
    stage.json(destination/'provenance.json',{'original_scene':str(source.relative_to(ROOT)),
        'original_sha256':digest,'portable_sha256':portable_hash,'assets':assets})


def check_record(record,state,scene_hashes):
    identity=record['reference'];method=record['method']
    if method not in METHODS or identity not in state['scenes']:raise ValueError('Unknown delivery identity/method')
    picture=ROOT/'outputs'/identity/(method+'.mp4');video=ROOT/'deliverables'/identity/(method+'.mp4')
    if record['picture']!=str(picture.relative_to(ROOT)) or record['with_reference_audio']!=str(video.relative_to(ROOT)):
        raise ValueError('Unexpected delivery path: '+identity+'/'+method)
    if record['sceneSHA256']!=scene_hashes[identity]:raise ValueError('Validation is stale for '+identity)
    if not record.get('picturePacketsUnchanged'):raise ValueError('Missing unchanged-picture validation: '+str(video))
    if sha(picture)!=record['pictureSHA256']:raise ValueError('Current master changed after validation: '+str(picture))
    if sha(video)!=record['muxedSHA256']:raise ValueError('Audio delivery changed after validation: '+str(video))
    capture=load(str(picture)+'.render.json');encoding=capture.get('encoding',{})
    if capture.get('knownIssues'):raise ValueError('Capture reports known issues: '+str(picture))
    if capture.get('sceneSHA256',capture.get('sceneSha256'))!=scene_hashes[identity]:
        raise ValueError('Capture scene hash is stale: '+str(picture))
    if encoding.get('pictureSHA256')!=record['pictureSHA256'] or encoding.get('sceneSHA256')!=scene_hashes[identity]:
        raise ValueError('Capture picture provenance changed: '+str(picture))
    if state.get('encoding_profile') and encoding.get('profile')!=state['encoding_profile']:
        raise ValueError('Capture encoding profile is stale: '+str(picture))
    audio=load(video.with_suffix('.audio.json'))
    if audio.get('sceneSHA256')!=scene_hashes[identity] or audio.get('picture_sha256')!=record['pictureSHA256'] or audio.get('method')!=method:
        raise ValueError('Audio provenance is stale: '+str(video))
    return audio


def check_manifest(state,manifest,records,scene_hashes,audio_metadata):
    videos=manifest['videos'];identities=[v['id'] for v in videos]
    if len(identities)!=len(set(identities)) or set(identities)!=set(state['scenes']):
        raise ValueError('Manifest must contain exactly the current references')
    for video in videos:
        identity=video['id']
        if video.get('sceneSHA256')!=scene_hashes[identity]:raise ValueError('Manifest scene is stale: '+identity)
        candidates=[c for c in video['candidates'] if c['reference_audio']]
        expected={(identity,method) for method in METHODS};seen=set()
        for candidate in candidates:
            key=(identity,Path(candidate['path']).stem)
            if key not in expected or key in seen:raise ValueError('Duplicate/unknown audio manifest candidate: '+candidate['path'])
            seen.add(key);record=records[key]
            if candidate['path']!=record['with_reference_audio'] or candidate.get('provenance')!=audio_metadata[key]:
                raise ValueError('Manifest audio path/provenance is stale: '+candidate['path'])
            for field in ('width','height','r_frame_rate','nb_frames'):
                if str(candidate['meta'].get(field))!=str(record['probe'].get(field)):
                    raise ValueError('Manifest video metadata is stale: '+candidate['path'])
            if abs(float(candidate['meta']['duration'])-float(record['probe']['duration']))>1e-6:
                raise ValueError('Manifest video duration is stale: '+candidate['path'])
        if seen!=expected:raise ValueError('Manifest requires five validated audio methods: '+identity)


def validate_inputs(state,manifest,validation):
    expected={(identity,method) for identity in state['scenes'] for method in METHODS}
    rows=validation.get('videos',[]);keys=[(r['reference'],r['method']) for r in rows]
    if len(state['scenes'])!=6 or len(expected)!=30 or validation.get('errors') or validation.get('validated')!=30 or validation.get('expected')!=30:
        raise ValueError('Final package requires all thirty validated current videos')
    if len(keys)!=30 or len(set(keys))!=30 or set(keys)!=expected:
        raise ValueError('Validation must cover each of six references/five methods exactly once')
    hold_path=ROOT/'verification/delivery-holds.json'
    if hold_path.exists() and any(q['status']!='resolved' for q in load(hold_path)['holds']):
        raise ValueError('Known delivery holds must be resolved before packaging')
    browser=load(ROOT/'verification/review-browser.json')
    if not browser.get('passed') or len(browser.get('checks',[]))!=30:
        raise ValueError('Thirty working review playback checks must pass before packaging')
    if browser.get('manifestSHA256')!=sha(ROOT/'delivery-manifest.json') or browser.get('reviewSHA256')!=sha(ROOT/'review.html'):
        raise ValueError('Working review browser validation is stale')
    if {q['path'] for q in browser['checks']}!={r['with_reference_audio'] for r in rows}:
        raise ValueError('Working browser checks must cover the exact thirty audio versions')
    hashes={identity:sha(ROOT/entry['scene']) for identity,entry in state['scenes'].items()}
    records=dict(zip(keys,rows));audio={key:check_record(record,state,hashes) for key,record in records.items()}
    check_manifest(state,manifest,records,hashes,audio)
    return hashes


def verify_license(path):
    with Path(path).open('rb') as source:
        if not source.read(6).startswith(b'{\\rtf1'):raise ValueError('SF Pro license must be a real RTF resource')


def copy_state_evidence(state,stage):
    for entry in state['scenes'].values():
        for key in ('source_report','timeline_scan'):
            if entry.get(key):
                source=ROOT/entry[key]
                if not source.is_file():raise ValueError('Missing state evidence: '+str(source))
                stage.tree(source.parent,source.parent.relative_to(ROOT))
        if entry.get('source_visual_gate'):
            source=ROOT/entry['source_visual_gate']
            if not source.is_file():raise ValueError('Missing source visual gate: '+str(source))
            # A qualification may sit beside the canonical and its assets. Only
            # the pinned file belongs here; do not duplicate that entire tree.
            stage.copy(source,source.relative_to(ROOT))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage',type=Path,default=DEST,help='Fresh empty staging directory (default: delivery-package)')
    parser.add_argument('--link-stage',action='store_true',help='Hardlink only frozen media/canonical files; temporary stage must share their filesystem')
    args=parser.parse_args()
    pins={name:sha(ROOT/name) for name in ('verification/delivery-validation.json','delivery-state.json','delivery-manifest.json','review.html','verification/review-browser.json')}
    for name in ('verification/delivery-holds.json','render-overrides.json'):
        if (ROOT/name).exists():pins[name]=sha(ROOT/name)
    validation=load(ROOT/'verification/delivery-validation.json');state=load(ROOT/'delivery-state.json');manifest=load(ROOT/'delivery-manifest.json')
    def recheck():
        if any(sha(ROOT/name)!=digest for name,digest in pins.items()):raise ValueError('Delivery inputs changed during packaging')
        validate_inputs(state,manifest,validation)
    recheck()
    license_path=ROOT/'shared/fonts/package/Resources/en.lproj/License.rtf'
    verify_license(license_path)
    stage=Stage(args.stage,args.link_stage)
    for record in validation['videos']:
        video=ROOT/record['with_reference_audio'];stage.copy(video,video.relative_to(ROOT),immutable=True)
        stage.copy(video.with_suffix('.audio.json'),video.with_suffix('.audio.json').relative_to(ROOT))
        stage.copy(ROOT/(record['picture']+'.render.json'),Path('deliverables')/record['reference']/(record['method']+'.capture.json'))
    for identity,entry in state['scenes'].items():
        export_scene(ROOT/entry['scene'],Path('scenes')/identity,stage)
        folder=ROOT/'references'/identity
        for pattern in ['source.mp4','source.json','analysis.md','steps*.md','segments.json','asset-provenance*.json']:
            for source in folder.glob(pattern):stage.copy_function(source,stage.root/source.relative_to(ROOT))
    for video in manifest['videos']:
        video['candidates']=[c for c in video['candidates'] if c['reference_audio']]
        for report in video['reports']:
            index=ROOT/report['path']
            if not index.is_file():raise ValueError('Missing detailed review: '+str(index))
            stage.tree(index.parent,index.parent.relative_to(ROOT))
    # State report pins may name report.json or index.html; both need the whole
    # sibling folder even if the review manifest has no detailed-report entry.
    copy_state_evidence(state,stage)
    page=(ROOT/'review.html').read_text();first=page.index('const data=')+len('const data=');last=page.index(';\nconst el=',first)
    stage.text('review.html',page[:first]+json.dumps(manifest).replace('</','<\\/')+page[last:])
    stage.json('delivery-manifest.json',manifest)
    for name in ('README.md','imessage-motion-recreation-skill.zip'):stage.copy_function(ROOT/name,stage.root/name)
    if (ROOT/'render-overrides.json').exists():stage.copy(ROOT/'render-overrides.json','render-overrides.json')
    portable_state=json.loads(json.dumps(state))
    for identity,entry in portable_state['scenes'].items():
        entry['creation_scene_path']=entry['scene'];entry['scene']='scenes/'+identity+'/scene.json'
    stage.json('delivery-state.json',portable_state)
    stage.copy(ROOT/'verification/delivery-validation.json','verification/delivery-validation.json')
    if (ROOT/'verification/delivery-holds.json').exists():
        stage.copy(ROOT/'verification/delivery-holds.json','verification/delivery-holds.json')
        for hold in load(ROOT/'verification/delivery-holds.json')['holds']:
            for evidence in hold.get('evidence',[]):
                source=ROOT/evidence
                if not source.is_file():raise ValueError('Missing hold resolution evidence: '+str(source))
                stage.copy(source,evidence)
    if (ROOT/'verification/final-quality.json').exists():stage.copy(ROOT/'verification/final-quality.json','verification/final-quality.json')
    if (ROOT/'verification/review-browser.json').exists():stage.copy(ROOT/'verification/review-browser.json','verification/review-browser.json')
    for area in ('method-parity','final-encoding'):
        source=ROOT/'verification'/area
        if source.exists():stage.tree(source,Path('verification')/area)
    if (ROOT/'verification/05-raster-parity-607').exists():stage.tree(ROOT/'verification/05-raster-parity-607','verification/05-raster-parity-607')
    for area in ('engines','shared','verification'):
        for source in (ROOT/'skill/imessage-motion-recreation/scripts'/area).glob('*'):
            if source.is_file():stage.copy_function(source,stage.root/area/source.name)
    conditioning=ROOT/'engines/fixtures/pillow-coordinate-conditioning/production-completion.json'
    if conditioning.exists():stage.copy(conditioning,conditioning.relative_to(ROOT))
    for source in (ROOT/'skill/imessage-motion-recreation/scripts').glob('*.py'):stage.copy(source,Path('scripts')/source.name)
    stage.tree(ROOT/'skill/imessage-motion-recreation','skill/imessage-motion-recreation')
    stage.copy(ROOT/'figma/status.json','figma/status.json');stage.copy(ROOT/'shared/fonts/provenance.json','font-licenses/SF-Pro-provenance.json')
    stage.copy(license_path,'font-licenses/SF-Pro-License.rtf')
    for folder in (ROOT/'references').iterdir():
        for source in folder.rglob('OFL.txt'):stage.copy(source,Path('font-licenses')/(folder.name+'-'+source.parent.name+'-OFL.txt'))
    # A same-scene renderer update must not silently swap the capture or review
    # provenance while this temporary stage is being assembled.
    recheck()
    entries={str(source.relative_to(stage.root)):sha(source) for source in stage.root.rglob('*') if source.is_file() and source!=stage.root/'checksums.json'}
    stage.json('checksums.json',entries)
    archive=ROOT/'imessage-recreations-delivery.zip';temporary=archive.with_name(archive.name+'.building-'+str(os.getpid()))
    try:
        with zipfile.ZipFile(temporary,'w') as output:
            for source in sorted(stage.root.rglob('*')):
                if source.is_file():output.write(source,Path('imessage-recreations')/source.relative_to(stage.root),compress_type=zipfile.ZIP_STORED if source.suffix in {'.mp4','.png','.jpg','.zip','.woff','.woff2'} else zipfile.ZIP_DEFLATED)
        if any(sha(stage.root/name)!=digest for name,digest in entries.items()):raise ValueError('Staged files changed while archiving')
        recheck()
        os.replace(temporary,archive)
    finally:temporary.unlink(missing_ok=True)
    print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'files':len(entries)+1,'stage':str(stage.root),'linkStage':args.link_stage},indent=2))

if __name__=='__main__':main()
