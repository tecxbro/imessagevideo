#!/usr/bin/env python3
"""Package this skill and its visuals into an explicitly named new ZIP."""
from pathlib import Path
import argparse,hashlib,json,os,zipfile
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1];out=a.out.resolve()
protected={'imessage-motion-recreation-skill.zip','imessage-motion-recreation-skill-public-update.zip','imessage-motion-recreation-with-ui-audio-skill.zip','imessage-motion-recreation-ui-audio-final-skill.zip'}
if out.name in protected:raise ValueError('Use a new archive name; previous snapshots are frozen.')
if out.is_relative_to(root):raise ValueError('Write the archive outside the skill folder.')
files=[p for p in sorted(root.rglob('*')) if p.is_file() and p.name!='checksums.json' and '__pycache__' not in p.parts and not p.name.endswith(('.tmp','.pyc'))]
library=root/'director/motion-library'
catalog=library/'catalog.json'
authored_previews={
    library/'previews'/f"{entry['id']}.mp4"
    for entry in json.loads(catalog.read_text())['entries']
} if catalog.is_file() else set()
for path in files:
    if path.is_symlink():raise ValueError('Symlink: '+str(path))
    if path in authored_previews:continue
    if path.suffix.lower() in {'.mp4','.mov','.mp3','.m4a','.wav','.flac','.ogg','.ttf','.otf','.woff','.woff2'}:raise ValueError('Keep movies/audio/proprietary fonts external: '+str(path))
checks={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(root/'checksums.json').write_text(json.dumps(checks,indent=2)+'\n');files.append(root/'checksums.json')
out.parent.mkdir(parents=True,exist_ok=True);tmp=out.with_suffix('.zip.tmp')
with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for path in files:z.write(path,'imessage-motion-recreation/'+str(path.relative_to(root)))
os.replace(tmp,out)
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    for name,digest in checks.items():assert hashlib.sha256(z.read('imessage-motion-recreation/'+name)).hexdigest()==digest
report={'path':str(out),'files':len(files),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'all_checksums_pass':True,'contains_visual_atlas':True,'contains_reference_movies_or_proprietary_font_binaries':False}
print(json.dumps(report,indent=2))
