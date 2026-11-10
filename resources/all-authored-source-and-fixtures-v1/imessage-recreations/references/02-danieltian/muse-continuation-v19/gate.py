from pathlib import Path
from PIL import Image,ImageDraw
import json,numpy as np,hashlib
R=Path(__file__).resolve().parent;ROOT=R.parents[2];O=ROOT/'outputs/02-danieltian/muse-continuation-v19';P=O/'prototype-01';SRC=R.parent/'assets/middle-every-frame';spec=json.load(open(R/'patch-spec.json'));poses={p['frame']:p for p in json.load(open(R/'existing-poses.json'))};clones={p['frame']:p for p in spec['complements']};frames=json.load(open(P/'capture.json'))['frameIndices'];rows=[]
for n in frames:
 paths=[SRC/f'source-{n:04}.png',O/f'baseline-native18/{n:06}.png',P/f'{n/30:.3f}.png'];a,b,c=[np.array(Image.open(p).convert('RGB')).astype(float) for p in paths];mask=np.zeros(a.shape[:2],bool)
 if n in clones:
  z=poses[n];q=clones[n]
  for x,y,w,h in [(z['x'],z['y'],126*z['scaleX'],126*z['scaleY']),(q['x'],q['y'],q['width'],q['height'])]:
   x1=max(0,int(np.floor(x))-3);x2=min(1920,int(np.ceil(x+w))+3);y1=max(0,int(np.floor(y))-3);y2=min(1080,int(np.ceil(y+h))+3);mask[y1:y2,x1:x2]=True
 else:assert np.array_equal(b,c),('outside native guard changed',n)
 delta=abs(b-c);before=abs(a-b);after=abs(a-c);outside=float(delta[~mask].sum());assert outside==0,(n,'non-avatar pixels changed',outside);q=dict(frame=n,beforeMAE=float(before.mean()),afterMAE=float(after.mean()),nativeVsV18MAE=float(delta.mean()),nonAvatarChangedSum=outside,source=str(paths[0]),before=str(paths[1]),candidate=str(paths[2]),candidateSHA256=hashlib.sha256(paths[2].read_bytes()).hexdigest())
 if n in clones:q.update(avatarRegionBeforeMAE=float(before[mask].mean()),avatarRegionAfterMAE=float(after[mask].mean()))
 rows.append(q);print(n,q['beforeMAE'],q['afterMAE'],'avatars',q.get('avatarRegionBeforeMAE'),q.get('avatarRegionAfterMAE'))
for k,ns in enumerate([range(666,670),range(676,680),range(701,705)],1):
 rowHeights=[];rects=[]
 for n in ns:
  z=poses[n];q=clones[n];top=max(0,int(min(z['y'],q['y']))-15);bottom=min(1080,int(max(z['y']+126*z['scaleY'],q['y']+q['height']))+16);rects.append((245,top,425,bottom));rowHeights.append(bottom-top+24)
 im=Image.new('RGB',(540,sum(rowHeights)),'white');d=ImageDraw.Draw(im);offset=0
 for n,box,rh in zip(ns,rects,rowHeights):
  q=next(x for x in rows if x['frame']==n)
  for j,label in enumerate(['source','before','candidate']):im.paste(Image.open(q[label]).convert('RGB').crop(box),(180*j,offset+24));d.text((180*j,offset),f'{n} '+label,fill='black')
  offset+=rh
 im.save(O/f'photo-contact-{k}.png')
changed=[q for q in rows if q['frame'] in clones];report=dict(baseSceneSHA256=spec['baseSceneSHA256'],helperSHA256=hashlib.sha256((R/'apply.py').read_bytes()).hexdigest(),patchSHA256=hashlib.sha256((R/'patch-spec.json').read_bytes()).hexdigest(),nativeFrames=frames,changedNativeFrames=len(changed),guardNativeFrames=[n for n in frames if n not in clones],allNativeGuardsExact=True,allNonAvatarPixelsExact=True,all12ChangedStatesImprove=all(q['afterMAE']<q['beforeMAE'] for q in changed),changedMeanBefore=float(np.mean([q['beforeMAE'] for q in changed])),changedMeanAfter=float(np.mean([q['afterMAE'] for q in changed])),all20MeanBefore=float(np.mean([q['beforeMAE'] for q in rows])),all20MeanAfter=float(np.mean([q['afterMAE'] for q in rows])),rows=rows,notice='Actual lossless native source/V18/candidate PNGs, no interpolated screenshots or rounded seek labels. Existing actor camera/asset/lifecycle remain unchanged. Only12photo crossfade states change. Incoming701fullartwork is viewport-cropped with full original aspect/size. Exact native endpoints retained because weak block residue fails original-art correlation and adding a ghost worsensL1.');(O/'source-gate.json').write_text(json.dumps(report,indent=2));assert report['all12ChangedStatesImprove'];print(json.dumps({k:v for k,v in report.items() if k!='rows'}))
