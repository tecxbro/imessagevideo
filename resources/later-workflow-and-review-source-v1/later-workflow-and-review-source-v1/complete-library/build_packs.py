#!/usr/bin/env python3
"""Build complete private packs without mutating any frozen delivery."""
from pathlib import Path
import collections,hashlib,json,os,shutil,zipfile
ROOT=Path(__file__).resolve().parents[1];OUT=Path('/dev/shm/imessage-complete-library');OUT.mkdir(exist_ok=True)
PREFIX='imessage-recreations/'
IDS=['01-photonhq','02-danieltian','03-photon-mini','04-poke','05-linq','06-gallery'];METHODS=['remotion','gsap','html','pillow','motion-canvas']
def sha(data):return hashlib.sha256(data).hexdigest()
def digest(path):return hashlib.file_digest(path.open('rb'),'sha256').hexdigest()
def js(value):return (json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode()
records=[]
def package(name,payload,category,extra=None):
    target=OUT/(name+'.zip');temp=target.with_suffix('.zip.tmp');checks={}
    with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for rel,value in sorted(payload.items()):
            data=value.read_bytes() if isinstance(value,Path) else value
            z.writestr(PREFIX+rel,data);checks[rel]=sha(data)
        z.writestr(PREFIX+'PACK-CHECKSUMS.json',js(checks))
    os.replace(temp,target)
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        for rel,h in checks.items():assert sha(z.read(PREFIX+rel))==h
    record={'id':name,'path':str(target),'bytes':target.stat().st_size,'sha256':digest(target),'files':len(checks)+1,'category':category,'all_payload_checksums_pass':True,**(extra or {})};records.append(record)
    print(json.dumps({k:v for k,v in record.items() if k!='path'}),flush=True)
    (ROOT/'complete-library/packs.json').write_bytes(js({'archives':records}))
    return record

with zipfile.ZipFile(ROOT/'imessage-recreations-delivery.zip') as src:
    names=src.namelist();common={}
    for n in names:
        rel=n.removeprefix(PREFIX)
        if rel.startswith(('engines/','scripts/','shared/','font-licenses/','figma/')) or rel in ['delivery-state.json','delivery-manifest.json','render-overrides.json']:
            common[rel]=src.read(n)
    common['tools/render_example.py']=(ROOT/'complete-library/render_example.py').read_bytes()
    for ident in IDS:
        payload=dict(common)
        starts=[f'scenes/{ident}/',f'references/{ident}/',f'deliverables/{ident}/',f'verification/timeline-scans/{ident}',f'verification/final/{ident}/']
        for n in names:
            rel=n.removeprefix(PREFIX)
            if any(rel.startswith(s) for s in starts):payload[rel]=src.read(n)
        # Include every authored per-example program, even when it is historical.
        for path in sorted((ROOT/'references'/ident).rglob('*')):
            if path.is_file() and path.suffix in {'.py','.mjs','.jsx','.js','.sh','.css','.html','.ts','.tsx'} and '__pycache__' not in path.parts:
                payload[str(path.relative_to(ROOT))]=path
        for method in METHODS:
            wrapper=f'''#!/usr/bin/env python3\nfrom pathlib import Path\nimport subprocess,sys\nroot=Path(__file__).resolve().parents[2]\nraise SystemExit(subprocess.call([sys.executable,str(root/'tools/render_example.py'),'--example','{ident}','--method','{method}',*sys.argv[1:]],cwd=root))\n'''
            payload[f'examples/{ident}/render-{method}.py']=wrapper.encode()
        payload['README-COMPLETE-EXAMPLE.md']=f'''# Complete example: {ident}

This private project contains the full accepted scene JSON and every declared
image/font asset, genuine shared implementations for all five completed methods,
the original reference movie, five final reference-audio MP4s and their provenance,
native source-comparison evidence and all retained per-example authoring programs.

The source implementation is one measured scene plus real shared adapters. The
five small examples/{ident}/render-METHOD.py files are explicit entry wrappers;
they do not pretend that five independent standalone code projects were authored.
Underlying React/Remotion code is engines/remotion-entry.jsx, GSAP and HTML runtime
code is engines/render.mjs +web-runtime.mjs +common.mjs, native Motion Canvas is
engines/render_motion_canvas.mjs +motion-canvas-runtime.mjs, and Pillow is
engines/render_pillow.py. Figma was not a completed method; its prototype is marked.

Install Node dependencies with `cd engines && npm ci`, Python dependencies from
engines/requirements.txt into a virtualenv, and Chromium +FFmpeg/ffprobe. Set
CHROME_PATH to the verified browser executable. Get the separate environment-font
pack for the pinned Linux fallbacks; respect its original licenses.

Run from this project root:
`python tools/render_example.py --example {ident} --method gsap --dry-run`
`python tools/render_example.py --example {ident} --method all`

The cold-build runner creates fresh frame caches, applies measured Pillow AA
overrides, performs full-range BT.709 encoding, then muxes the supplied audio using
the explicit Rene cut when relevant. It writes new results to new-deliverables.
Existing deliverables are frozen comparison targets. Use --checkpoint FRAME for
a single native-frame capability check. Fonts/renderers/encoders must be matched
before expecting the same pixels; code completeness is not a fresh full-render claim.

Historical authoring programs can refer to old working paths and superseded inputs.
They are included as the requested complete authored code, not the cold-render path.
Full source history/provenance and silent masters are separately indexed in the
private library. Per-file SHA256 values are in PACK-CHECKSUMS.json.
'''.encode()
        # Resolve every relative runtime image/font before publishing a pack.
        scene=json.loads(payload[f'scenes/{ident}/scene.json']);assets=[]
        def walk(layers):
            for layer in layers:
                if layer.get('src') and not layer['src'].startswith(('data:','http:','https:')):assets.append(layer['src'])
                walk(layer.get('children',[]))
        walk(scene['layers']);assets += [f['src'] for f in scene.get('fonts',[]) if not f['src'].startswith(('data:','http:','https:'))]
        for asset in assets:
            key=os.path.normpath(f'scenes/{ident}/'+asset);assert key in payload,(ident,key)
        package(ident+'-complete-v1',payload,'projects',{'example':ident,'methods':METHODS,'runtime_asset_paths_verified':len(set(assets)),'final_reference_audio_videos':5})

# Original frozen delivery is preserved byte-for-byte and divided later, not repacked.
records.append({'id':'frozen-visual-delivery-v1','path':str(ROOT/'imessage-recreations-delivery.zip'),'bytes':(ROOT/'imessage-recreations-delivery.zip').stat().st_size,'sha256':digest(ROOT/'imessage-recreations-delivery.zip'),'files':5765,'category':'originals','frozen_archive':True})

payload={}
for ident in IDS:
    for method in METHODS:
        for path in [ROOT/'outputs'/ident/(method+'.mp4'),ROOT/'outputs'/ident/(method+'.mp4.render.json')]:
            assert path.is_file(),path;payload[str(path.relative_to(ROOT))]=path
package('silent-picture-masters-v1',payload,'originals',{'silent_videos':30})

# All authored executable source, including retained experiments/coordinators.
ext={'.py','.mjs','.jsx','.js','.ts','.tsx','.css','.html','.sh','.cjs','.sql'}
skip={'node_modules','.venv','__pycache__','.git','cache','caches','remotion-bundle','node-compile-cache','package'}
payload={};areas=['engines','scripts','references','verification','figma','shared','outputs','audio-recreation','skill-upgrade','complete-library']
for area in areas:
    for p in (ROOT/area).rglob('*'):
        rel=p.relative_to(ROOT)
        if p.is_file() and p.suffix in ext and not any(s in skip for s in rel.parts) and rel.parts[:2]!=('shared','fonts'):
            payload[str(rel)]=p
for area in ['engines/fixtures','figma']:
    for p in (ROOT/area).rglob('*'):
        if p.is_file() and not any(x in skip for x in p.relative_to(ROOT).parts):payload[str(p.relative_to(ROOT))]=p
for name in ['engines/native-engine-compatibility.json','engines/native-engine-corrections.json','engines/alternative-capabilities.json','engines/capabilities.json','render-overrides.json']:
    if (ROOT/name).is_file():payload[name]=ROOT/name
for name in ['photon-audit.json','mini-poke-audit.json','linq-rene-audit.json','audio-audit.json']:
    payload['complete-library/'+name]=ROOT/'complete-library'/name
payload['SOURCE-SCOPE.json']=js({'definition':'All retained authored executable code under the enumerated project areas, real engine fixtures/provenance and the completeness audits. Accepted scene/data/assets are in complete example packs and frozen delivery.','areas':areas,'code_files':len(payload),'excluded':'Installed dependencies/venvs, third-party font installer resources, caches and duplicate staging trees. Historical programs may require old measurement data; the accepted cold-build path is the case scene plus genuine adapters.'})
package('all-authored-source-and-fixtures-v1',payload,'sources')

audit=json.loads((ROOT/'complete-library/audio-audit.json').read_text());payload={}
for item in audit['recommended_complete_audio_pack_members']:
    p=ROOT/item['path'];assert p.stat().st_size==item['bytes'] and digest(p)==item['sha256'];payload[item['path']]=p
for item in audit['critical_additions_exact']['files']:payload[item['path']]=ROOT/item['path']
payload['audio-recreation/scripts/render_example.py']=ROOT/'complete-library/render_example.py'
payload['audio-recreation/videos.json']=Path('/workspace/sites/message-motion/dist/videos.json')
payload['audio-recreation/README-COMPLETE.md']=b'''# Complete UI audio source

This new private bundle closes the frozen supplement's missing six mix reports,
two original licensed stock archives, and captured source pages. It contains the
pinned generated music, original new-music stems, final UI/music/mix stems, all
source/config snapshots, cue source/normalized schedules, prepared/raw licensed
effects, synthesis source, tests and12finished UI-only/quiet-music preview MP4s.

No-music rebuild: python audio-recreation/scripts/render_ui.py --id05-linq --no-music
(Insert a space between --id and05-linq.) Default UI-with-music also has its pinned
mixes/ID/music.flac and mix-report.json. No fresh AI generation is required.

For preview muxing, materialize the matching complete visual case and copy its
silent outputs/ID/gsap.mp4 from the silent-master pack. The old source-specific
packager additionally expects the original Sites checkout paths; use the portable
library workflow instead. Cue re-derivation requires the original canonical scene
paths from delivery-state; already accepted canonical schedules need no scene read.
Raw HTTP headers, cookies and signed download-link JSON are intentionally absent.
The missing-input audit and PACK-CHECKSUMS.json make these boundaries explicit.
'''
package('complete-ui-audio-source-v1',payload,'audio',{'canonical_audio_reports':6,'known_missing_inputs_closed':10})

# Capture the exact freely redistributable Linux fallback files plus their licenses.
payload={};fontpaths=[Path('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'),Path('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'),Path('/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf'),Path('/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),Path('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf')]
for p in fontpaths:
    assert p.is_file();payload['environment/fonts/'+p.name]=p
for folder in ['fonts-liberation','fonts-dejavu-core','fonts-noto-color-emoji']:
    p=Path('/usr/share/doc')/folder/'copyright';assert p.is_file();payload['environment/licenses/'+folder+'-copyright.txt']=p
payload['environment/licenses/Apache-2.0.txt']=Path('/usr/share/common-licenses/Apache-2.0')
for p in (ROOT/'shared/fonts').glob('*.otf'):payload[str(p.relative_to(ROOT))]=p
for p in (ROOT/'references').rglob('*'):
    if p.is_file() and p.suffix in {'.ttf','.otf','.woff','.woff2'}:payload[str(p.relative_to(ROOT))]=p
payload['shared/fonts/provenance.json']=ROOT/'shared/fonts/provenance.json'
payload['shared/fonts/license-repair.json']=ROOT/'shared/fonts/license-repair.json'
payload['font-licenses/SF-Pro-License.rtf']=ROOT/'delivery-package-final/font-licenses/SF-Pro-License.rtf'
payload['environment/README.md']=b'''# Pinned font dependencies (private)

Accepted case packs contain their exact primary font subsets. This supplement
preserves original full font inputs and the actual Linux fallback files used for
Arial and missing chess/house/music symbols, with original licenses and provenance.
Do not replace the observed family/charset fallback rules with a sans-only alias;
U+265F used Noto Color Emoji. See complete-library/mini-poke-audit.json for the
exact codepoint matches, font hashes, package/configuration versions and commands.
Respect Apple and other provider license terms. This private pack is not publicly
redistributed by the motion gallery. System package installation still uses official
providers; no vendor installer, node_modules, Python venv or browser binary is bundled.
'''
package('font-inputs-and-linux-fallbacks-v1',payload,'sources')
(ROOT/'complete-library/packs.json').write_bytes(js({'archives':records}))
