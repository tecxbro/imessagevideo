"""Read-only exact-frame physical-chrome measurements, independent of Messages UI."""
from pathlib import Path
import json,subprocess,sys,time
from PIL import Image
from hardware_fit_v13 import fit_hardware
from apply_blue_arrival_v14 import sample
P=Path(__file__).resolve().parent
scene=json.loads((P/'final-v15.scene.json').read_text())
phone=next(layer for layer in scene['layers'] if layer['id']=='p03-204')
process=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-threads','1','-filter_threads','1','-i',str(P/'source.mp4'),'-vf',"select='between(n,495,617)'",'-fps_mode','passthrough','-map','0:v:0','-an','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE)
rows=[]
started=time.time()
try:
    for frame in range(495,618):
        needed=1920*1080*3
        raw=bytearray()
        while len(raw)<needed:
            piece=process.stdout.read(needed-len(raw))
            if not piece:
                break
            raw.extend(piece)
        if len(raw)!=needed:
            raise ValueError(f'Incomplete source native frame{frame}')
        image=Image.frombytes('RGB',(1920,1080),bytes(raw))
        prior={key:sample(phone['keyframes'][key],frame/30) for key in ['x','y','scaleX','scaleY']}
        result=fit_hardware(image,prior,y_radius=120)
        rows.append(dict(frame=frame,old_camera=prior,measurement=result))
finally:
    process.stdout.close()
    if process.poll() is None:
        process.terminate()
    process.wait()
result=dict(scope=[495,617],baseline='final-v15.scene.json',notice='Physical opaque outer-rim/side-button measurements only. UI, header, outgoing bubble, preview and618+menu/backplane have independent cameras and are not inferred from this fit. Every fit retains cost/feature count and review flag; no source frames are stored in this measurement ledger.',elapsed=time.time()-started,frames=rows)
(P/'lunch-chrome-v16-measurements.json').write_text(json.dumps(result,indent=2)+'\n')
print('Measured',len(rows),'frames; reviewrequired',sum(r['measurement']['review_required'] for r in rows),'seconds',result['elapsed'])
