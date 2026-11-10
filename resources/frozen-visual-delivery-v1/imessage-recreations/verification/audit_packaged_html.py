#!/usr/bin/env python3
"""Check static HTML URLs against the files the delivery packager stages.
Default mode builds a read-only planned-file map; --stage inspects an existing
stage without copying it. Dynamic JS URLs and documentary JSON paths are not
interpreted. The final browser validator covers the main review's dynamic UI.
"""
from pathlib import Path,PurePosixPath
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import argparse,hashlib,importlib.util,json,posixpath,re

ROOT=Path(__file__).resolve().parents[1]


class References(HTMLParser):
    def __init__(self):super().__init__();self.refs=[];self.style=False
    def handle_starttag(self,tag,attrs):
        self.style=tag=='style' or self.style
        for name,value in attrs:
            if not value:continue
            if name in ('href','src','poster'):self.refs.append((tag,name,value))
            if name=='srcset':self.refs.extend((tag,name,p.strip().split()[0]) for p in value.split(',') if p.strip())
            if name=='style':self.css(value)
    def handle_endtag(self,tag):
        if tag=='style':self.style=False
    def handle_data(self,text):
        if self.style:self.css(text)
    def css(self,text):
        self.refs.extend(('style','url',m.strip(' \"\'')) for m in re.findall(r'url\(([^)]+)\)',text))


class Plan:
    def __init__(self):self.files={}
    def copy(self,source,destination,**options):
        source=Path(source);destination=str(PurePosixPath(destination))
        if source.is_file():self.files[destination]=source
    def tree(self,source,destination):
        source=Path(source)
        if source.is_dir():
            for file in source.rglob('*'):
                if file.is_file():self.copy(file,PurePosixPath(destination)/file.relative_to(source))


def planned_files():
    plan=Plan();state=json.loads((ROOT/'delivery-state.json').read_text());manifest=json.loads((ROOT/'delivery-manifest.json').read_text())
    spec=importlib.util.spec_from_file_location('delivery_package',ROOT/'scripts/package_delivery.py');package=importlib.util.module_from_spec(spec);spec.loader.exec_module(package)
    package.copy_state_evidence(state,plan)
    for area in ('method-parity','final-encoding'):
        plan.tree(ROOT/'verification'/area,PurePosixPath('verification')/area)
    plan.tree(ROOT/'verification/05-raster-parity-607','verification/05-raster-parity-607')
    for video in manifest['videos']:
        for report in video['reports']:
            parent=(ROOT/report['path']).parent;plan.tree(parent,parent.relative_to(ROOT))
        for candidate in video['candidates']:
            if candidate['reference_audio']:plan.copy(ROOT/candidate['path'],candidate['path'])
    audit=json.loads((ROOT/'verification/packaging-audit/portable-canonical-assets.json').read_text())
    for scene in audit['scenes']:
        if state['scenes'][scene['reference']]['scene']!=scene['scene']:raise ValueError('Refresh portable asset audit for '+scene['reference'])
        plan.copy(ROOT/scene['scene'],PurePosixPath('scenes')/scene['reference']/'scene.json')
        for asset in scene['assets']:plan.copy((ROOT/scene['scene']).parent/asset['path'],PurePosixPath('scenes')/scene['reference']/asset['path'])
    for identity in state['scenes']:
        folder=ROOT/'references'/identity
        for pattern in ('source.mp4','source.json','analysis.md','steps*.md','segments.json','asset-provenance*.json'):
            for file in folder.glob(pattern):plan.copy(file,file.relative_to(ROOT))
    for name in ('review.html','delivery-state.json','delivery-manifest.json','README.md','imessage-motion-recreation-skill.zip','render-overrides.json','verification/delivery-validation.json','verification/final-quality.json','verification/review-browser.json','verification/delivery-holds.json','figma/status.json'):
        plan.copy(ROOT/name,name)
    base=ROOT/'skill/imessage-motion-recreation/scripts'
    for area in ('engines','shared','verification'):
        for file in (base/area).glob('*'):
            if file.is_file():plan.copy(file,PurePosixPath(area)/file.name)
    for file in base.glob('*.py'):plan.copy(file,PurePosixPath('scripts')/file.name)
    plan.tree(ROOT/'skill/imessage-motion-recreation','skill/imessage-motion-recreation')
    plan.copy(ROOT/'shared/fonts/provenance.json','font-licenses/SF-Pro-provenance.json')
    plan.copy(ROOT/'shared/fonts/package/Resources/en.lproj/License.rtf','font-licenses/SF-Pro-License.rtf')
    return plan.files


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--stage',type=Path);parser.add_argument('--out',type=Path,default=ROOT/'verification/packaging-audit/html-portability.json');args=parser.parse_args()
    if args.stage:
        base=args.stage.resolve();files={str(f.relative_to(base)):f for f in base.rglob('*') if f.is_file()}
    else:files=planned_files()
    pages=[];missing=[];count=0
    for destination,source in sorted(files.items()):
        if not destination.endswith('.html'):continue
        html=source.read_text();parsed=References();parsed.feed(html);links=[]
        for tag,attribute,value in parsed.refs:
            url=urlsplit(value)
            if url.scheme in ('data','blob','http','https','mailto','tel','javascript') or value.startswith('//'):continue
            if not url.path:continue
            path=unquote(url.path)
            target=posixpath.normpath(path.lstrip('/') if path.startswith('/') else posixpath.join(str(PurePosixPath(destination).parent),path))
            present=not url.scheme and not target.startswith('../') and target in files
            row={'tag':tag,'attribute':attribute,'url':value,'target':target,'staged':present};links.append(row);count+=1
            if not present:missing.append({'page':destination,**row,'workingFileExists':(ROOT/target).is_file()})
        pages.append({'page':destination,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'staticLocalReferences':len(links),'missing':sum(not row['staged'] for row in links),'links':links})
    report={'passed':not missing,'mode':'existing-stage' if args.stage else 'planned-current-inputs','stage':str(args.stage) if args.stage else None,'packageScriptSHA256':hashlib.sha256((ROOT/'scripts/package_delivery.py').read_bytes()).hexdigest(),'pages':pages,'htmlPages':len(pages),'staticLocalReferences':count,'missing':missing,'notice':'Static HTMLhref/src/poster/srcset/CSSurl links only; no browser or media/cache write. Original numerical/provenance paths inside JSON are documentary and remain untouched. Planned mode mirrors current copied trees and state evidence; refresh after manifest/viewer changes. Dynamic main-review playback is verified separately by validate_review.mjs.'};args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'htmlPages':len(pages),'staticLocalReferences':count,'missing':missing,'report':str(args.out)},indent=2));return bool(missing)

if __name__=='__main__':raise SystemExit(main())
