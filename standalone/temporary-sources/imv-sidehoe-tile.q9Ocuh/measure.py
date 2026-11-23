from pathlib import Path
from PIL import Image
from hashlib import sha256
import sys
import numpy as np
import json

scratch = Path(sys.argv[1])
roi = (742,1260,1245,1790)
phase_roi = (742,1110,1245,2000)
prior = Path('/tmp/imv-upstream.tH7Joz/sidehoe-proven/tile')
canonical = Path('/tmp/imv-goal.9G9Un0/sidehoe-clean-frames')

def read(directory, frame, box=None):
    im = Image.open(directory / f'{frame:06d}.png').convert('RGB')
    if box and im.width == 1000:
        im = im.resize((2000,2000), Image.Resampling.LANCZOS)
    if box:
        im = im.crop(box)
    return np.array(im).astype(np.int16)

def mae(a,b):
    return round(float(np.abs(a-b).mean()),4)

def blue_stats(a):
    r,g,b=a.transpose(2,0,1)
    y,x=np.where((b-r>48)&(g-r>20)&(b-g>12)&(r<190))
    if y.size<50:return dict(pixels=int(y.size),bounds=None)
    return dict(pixels=int(y.size),bounds=[int(x.min()+phase_roi[0]),int(y.min()+phase_roi[1]),int(x.max()+phase_roi[0]+1),int(y.max()+phase_roi[1]+1)])

def summarize(frames):
    out=[]
    for f in frames:
        file = f'{f:06d}.png'
        base=read(scratch/'frozen',f)
        alt=read(scratch/'registered',f)
        src=read(scratch/'source',f,roi)
        src_phase=read(scratch/'source',f,phase_roi)
        frozen_phase=read(scratch/'frozen',f,phase_roi)
        result=dict(frame=f,hash_cached=sha256((canonical/file).read_bytes()).hexdigest(),fresh_lossless_pixels_match_frozen=bool((base==read(canonical,f)).all()),
                    unchanged_lossless=bool((base==alt).all()), native_mae={kind:mae(src,read(scratch/kind,f,roi)) for kind in ('frozen','registered','encoded','frozen-probe-encoded','registered-probe-encoded','prior-encoded')},
                    phase_mae={kind:mae(src_phase,read(scratch/kind,f,phase_roi)) for kind in ('frozen','registered','encoded','frozen-probe-encoded','registered-probe-encoded')},
                    probe_encode_difference=mae(read(scratch/'frozen-probe-encoded',f,phase_roi),read(scratch/'registered-probe-encoded',f,phase_roi)),
                    blue={kind:blue_stats(im) for kind,im in [('source',src_phase),('frozen',frozen_phase),('encoded',read(scratch/'encoded',f,phase_roi)),('registered',read(scratch/'registered',f,phase_roi))]})
        if 614<=f<=619:
            result["previous_revised_lossless"] = mae(src,read(prior/'revised',f,roi))
            result["previous_revised_encoded"] = mae(src,read(prior/'revised-encoded',f-614,roi))
            result["matches_prior_lossless"] = bool((base==read(prior/'baseline',f)).all())
        out.append(result)
    return out
rows=summarize(range(612,624))
(scratch/'metrics.json').write_text(json.dumps(rows,indent=2)+'\n')
for r in rows:print(r['frame'], r['unchanged_lossless'],r['fresh_lossless_pixels_match_frozen'], r['native_mae'], r['phase_mae'],r['blue']['source'],r['blue']['frozen'],r['probe_encode_difference'])
