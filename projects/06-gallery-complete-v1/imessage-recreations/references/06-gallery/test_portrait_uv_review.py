"""Separate static photographic UV registration from independent circle camera."""
from pathlib import Path
import sys,json,copy,numpy as np
from PIL import Image
R=Path('/workspace/imessage-recreations');P=R/'verification/fidelity-review/06-portrait614';BASE=R/'outputs/06-gallery/final-v20';sys.path.insert(0,str(R/'engines'));import render_pillow as rp
S=json.load(open(P/'local-fit.scene.json'));rp.register_fonts(S,str(BASE));f=614;g=next(n for n in S['layers']if n.get('semanticPhotoId')=='rene-final11-group-79'and n.get('start',0)<=f/30<n.get('end',99));st=rp.state(g,f/30);child=g['children'][0];N=512;im=Image.open(child['src']).convert('RGBA');alpha=im.getchannel('A');rgb=im.convert('RGB');rdx=child['width']*st['scaleX'];rdy=child['height']*st['scaleY'];rx=st['x'];ry=st['y'];cx=rx+rdx/2;cy=ry+rdy/2;blur=st['blur']*st['scaleX'];ref=np.array(Image.open(P/'source/000614.png'),dtype=float);rows=[]
for dx,dy,bx,by in [(1702.538,1702.538,1354.538,1458.69),(1702.538,1702.538,cx,cy),(1750,1750,cx,cy),(1650,1700,cx,cy),(rdx*1.05,rdy*1.05,cx,cy),(rdx*.95,rdy*.95,cx,cy)]:
 x=bx-dx/2;y=by-dy/2;uv=rgb.transform((N,N),Image.Transform.AFFINE,(dx/rdx,0,(x-rx)*N/rdx,0,dy/rdy,(y-ry)*N/rdy),Image.Resampling.BICUBIC,fillcolor='white').convert('RGBA');uv.putalpha(alpha);file=P/f'uv79-{len(rows)}.png';uv.save(file);q=copy.deepcopy(S);n=next(z for z in q['layers']if z['id']==g['id']);n['children'][0]['src']=str(file);v=dict(x=x,y=y,scaleX=dx/N,scaleY=dy/N,blur=blur/(dx/N));n['keyframes'].update({k:[dict(t=f/30,value=value)]for k,value in v.items()});out=rp.render(q,f/30,str(BASE));cost=float(abs(np.array(out,dtype=float)-ref).mean());r=dict(index=len(rows),dx=dx,dy=dy,cx=bx,cy=by,fullMAE=cost);rows.append(r);print(r,flush=True)
 if cost==min(v['fullMAE']for v in rows):out.save(P/'uv79-best.png');(P/'uv79-best.scene.json').write_text(json.dumps(q,indent=2))
(P/'uv79-tests.json').write_text(json.dumps(rows,indent=2))
