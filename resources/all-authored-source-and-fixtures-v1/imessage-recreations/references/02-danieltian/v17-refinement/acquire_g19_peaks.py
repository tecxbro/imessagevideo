from pathlib import Path
import json,hashlib,importlib.util
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];SCAN=ROOT/'verification/timeline-scans/02-danieltian-v19/scan.json';D=ROOT/'verification/final/02-danieltian/source-gsap-v19/native-peaks'
scan=json.loads(SCAN.read_text());scene=ROOT/'outputs/02-danieltian/final-v19/scene.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert scan['sceneSHA256']==sha(scene)
reference=ROOT/'references/02-danieltian/source.mp4';candidate=ROOT/'outputs/02-danieltian/gsap.mp4';assert sha(reference)==scan['referenceSHA256'];assert sha(candidate)==scan['candidateSHA256']
frames=sorted(q['reference_frame']for q in scan['peaks']);assert len(frames)==24
spec=importlib.util.spec_from_file_location('source_compare',ROOT/'verification/compare.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
D.mkdir(parents=True,exist_ok=True);batches={}
for role,file in [('reference',reference),('candidate',candidate)]:
    info=m.probe(file);batches[role]=m.batch_native_frames(file,[f/30 for f in frames],info,None,D/role)
records=[]
for frame in frames:
    row={'frame':frame}
    for role in['reference','candidate']:row[role]={'path':str(batches[role][frame]),'PNG_SHA256':sha(batches[role][frame])}
    records.append(row)
(D/'mapping.json').write_text(json.dumps({'sourceScanSHA256':sha(SCAN),'sceneSHA256':sha(scene),'referenceVideoSHA256':sha(reference),'candidateVideoSHA256':sha(candidate),'acquisition':'Independent permanent native24frame batch decode per video using tested exact-index FFmpeg selector. Source/candidate/movie hashes stable, no subsequent encoder permitted before review.','rows':records},indent=2))
for page in range(4):
    rows=records[page*6:(page+1)*6];canvas=Image.new('RGB',(1280,380*len(rows)),'white');draw=ImageDraw.Draw(canvas)
    for i,row in enumerate(rows):
        for col,role in enumerate(['reference','candidate']):
            image=Image.open(row[role]['path']).convert('RGB').resize((640,360));canvas.paste(image,(col*640,i*380+20));draw.text((col*640,i*380),str(row['frame'])+' '+role,fill='red')
    canvas.save(D/f'contact-{page+1}.jpg')
print('Complete24native source/candidate pairs',str(D),flush=True)
