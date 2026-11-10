"""Actual all-frame cross-method parity; no source-fidelity inference from engine identity."""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[2];OUT=R/'outputs/02-danieltian';EXPECTED='729c783aa3a13f87c2e61d9a409a492adff9d27208ae6e092c3edfc2c2e8abee';p=argparse.ArgumentParser();p.add_argument('--method',choices=['remotion','html'],required=True);args=p.parse_args();method=args.method
sha=lambda file:hashlib.sha256(Path(file).read_bytes()).hexdigest()
a=json.loads((OUT/'gsap.mp4.render.json').read_text());b=json.loads((OUT/f'{method}.mp4.render.json').read_text());workflow=json.loads((OUT/f'v19-{method}-workflow.json').read_text());assert workflow['stage']=='encoded-final-pc709';assert a['sceneSHA256']==b['sceneSHA256']==EXPECTED;assert a['frames']==b['frames']==1360
left=Path(a['frameDirectory']);right=Path(b['frameDirectory']);rows=[]
for f in range(1360):
    ap=left/f'{f:06d}.png';bp=right/f'{f:06d}.png';same=sha(ap)==sha(bp)
    if same:row={'frame':f,'PNGByteIdentical':True,'RGBPixelIdentical':True,'RGBMAE':0.0,'RGBMaximum':0}
    else:
        av=np.asarray(Image.open(ap).convert('RGB')).astype('int16');bv=np.asarray(Image.open(bp).convert('RGB')).astype('int16');delta=abs(av-bv);row={'frame':f,'PNGByteIdentical':False,'RGBPixelIdentical':bool(np.all(delta==0)),'RGBMAE':float(delta.mean()),'RGBMaximum':int(delta.max())}
    rows.append(row)
    if f%300==0:print(method,f,flush=True)
report={'sceneSHA256':EXPECTED,'referenceMethod':'gsap','candidateMethod':method,'framesChecked':1360,'allPNGByteIdentical':all(q['PNGByteIdentical']for q in rows),'allRGBPixelIdentical':all(q['RGBPixelIdentical']for q in rows),'meanNativeFrameRGBMAE':float(np.mean([q['RGBMAE']for q in rows])),'maximumFrameRGBMAE':max(q['RGBMAE']for q in rows),'maximumChannelDifference':max(q['RGBMaximum']for q in rows),'RGBDifferentFrames':[q for q in rows if not q['RGBPixelIdentical']],'PNGCompressionOnlyDifferentFrames':[q['frame']for q in rows if q['RGBPixelIdentical']and not q['PNGByteIdentical']],'gsapMovieSHA256':sha(OUT/'gsap.mp4'),'candidateMovieSHA256':sha(OUT/f'{method}.mp4'),'actualFrameDirectories':[str(left),str(right)],'notice':'Cross-method rendering parity is separate from source fidelity. G19 source residual qualification remains in final-v19/source-qualification.json.'};report['movieBytesIdentical']=report['gsapMovieSHA256']==report['candidateMovieSHA256'];(OUT/'final-v19'/f'{method}-gsap-all-native-parity.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items()if k not in['RGBDifferentFrames','PNGCompressionOnlyDifferentFrames']},indent=2))
