from pathlib import Path
import re,json,hashlib,gzip,shutil
import cv2,numpy as np
R=Path(__file__).resolve().parent
src=R/'reasoning-neutral-candidate.json';dst=R/'reasoning-neutral-compact.json'
spec=json.loads(src.read_text());before=after=verticesBefore=verticesAfter=0
for band in spec['replacement']['children']:
    if not band['id'].startswith('reason-neutral-native-'):continue
    for path in band['children']:
        old=path['d'];before+=len(old);loops=[]
        for loop in re.findall(r'M([^Z]+)Z',old):
            a=np.array(list(map(float,re.findall(r'-?\d+(?:\.\d+)?',loop))),np.float32).reshape(-1,2)
            verticesBefore+=len(a)
            b=cv2.approxPolyDP(a,.08,True).reshape(-1,2)
            if len(b)<3:b=a
            verticesAfter+=len(b)
            def fmt(x):return f'{float(x):.3f}'.rstrip('0').rstrip('.')
            loops.append('M'+fmt(b[0,0])+' '+fmt(b[0,1])+' '+' '.join('L'+fmt(x)+' '+fmt(y)for x,y in b[1:])+' Z')
        path['d']=' '.join(loops);after+=len(path['d'])
spec['contourSimplification']={'maxGeometricTolerancePx':.08,'verticesBefore':verticesBefore,'verticesAfter':verticesAfter,'pathBytesBefore':before,'pathBytesAfter':after,'method':'Closed-contour Ramer-Douglas-Peucker via OpenCV, preserved loop/hole winding; physical native source gate required.'}
dst.write_text(json.dumps(spec,separators=(',',':')));print(json.dumps(spec['contourSimplification']),flush=True)
# Superseded private input is reversibly archived only after exact decompressed SHA proof.
records=[]
for file in [src,R/'reasoning-neutral-house-probe.json']:
    original=hashlib.sha256(file.read_bytes()).hexdigest();archive=Path(str(file)+'.gz')
    with file.open('rb')as incoming,gzip.open(archive,'wb',compresslevel=6)as outgoing:shutil.copyfileobj(incoming,outgoing,1024*1024)
    h=hashlib.sha256()
    with gzip.open(archive,'rb')as incoming:
        for block in iter(lambda:incoming.read(1024*1024),b''):h.update(block)
    assert h.hexdigest()==original
    records.append({'file':str(file),'originalSHA256':original,'archive':str(archive),'archiveSHA256':hashlib.sha256(archive.read_bytes()).hexdigest(),'bytesBefore':file.stat().st_size,'bytesAfter':archive.stat().st_size,'decompressedSHA256Verified':True});file.unlink()
(R/'neutral-private-archives.json').write_text(json.dumps(records,indent=2))
