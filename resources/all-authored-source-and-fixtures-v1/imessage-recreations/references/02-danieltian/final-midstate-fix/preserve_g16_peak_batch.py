from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,os
ROOT=Path.cwd()
OUT=ROOT/'verification/final/02-danieltian/source-gsap-v16/native-peaks'
OUT.mkdir(parents=True,exist_ok=True)
scan=json.loads((ROOT/'verification/timeline-scans/02-danieltian-v16/scan.json').read_text())
frames=sorted(q['reference_frame']for q in scan['peaks'])
assert frames[0]==240 and len(frames)==24
known=ROOT/'verification/final/02-danieltian/source-gsap-v14/native-peaks/reference/000001.png'
def pixels(path):return hashlib.sha256(Image.open(path).convert('RGB').tobytes()).hexdigest()
expected=pixels(known)
candidates=[]
for directory in Path('/tmp').glob('native-comparison-*'):
    first=directory/'reference/000001.png'
    if first.exists()and len(list((directory/'candidate').glob('*.png')))==24:
        if pixels(first)==expected:candidates.append(directory)
assert len(candidates)==1,('Need one current complete source02 batch',list(map(str,candidates)))
batch=candidates[0]
records=[]
for index,frame in enumerate(frames,1):
    row={'frame':frame}
    for role in['reference','candidate']:
        source=batch/role/f'{index:06d}.png'
        destination=OUT/role/source.name
        destination.parent.mkdir(exist_ok=True)
        if not destination.exists():os.link(source,destination)
        row[role]={'path':str(destination),'PNG_SHA256':hashlib.sha256(destination.read_bytes()).hexdigest()}
    records.append(row)
(OUT/'mapping.json').write_text(json.dumps({'sourceScanSHA256':hashlib.sha256((ROOT/'verification/timeline-scans/02-danieltian-v16/scan.json').read_bytes()).hexdigest(),'referenceVideoSHA256':scan['referenceSHA256'],'candidateVideoSHA256':scan['candidateSHA256'],'sceneSHA256':scan['sceneSHA256'],'acquisition':'Protected complete native decoder PNGs from the active G16 --batch-native compare, prior to temporary cleanup. First source240 RGB is identical to independently acquired known240. Final completed comparison report must match all selected frame indices and candidate video hash.','rows':records},indent=2))
for page in range(4):
    selected=records[page*6:(page+1)*6]
    out=Image.new('RGB',(1280,380*len(selected)),'white')
    draw=ImageDraw.Draw(out)
    for row_index,row in enumerate(selected):
        for column,role in enumerate(['reference','candidate']):
            image=Image.open(row[role]['path']).convert('RGB').resize((640,360))
            out.paste(image,(column*640,row_index*380+20))
            draw.text((column*640,row_index*380),f"{row['frame']} {role}",fill='red')
    out.save(OUT/f'contact-{page+1}.jpg')
print('Protected and composed24actual native source/candidate peak pairs',str(OUT))
