"""Faint selected-card title registration with explicit foreground occlusion mask."""
from pathlib import Path
import sys,json,numpy as np
from PIL import Image
from scipy import ndimage
from v8_utils import at
p=Path(__file__).parent;root=p.parent.parent;s=json.loads((root/'outputs/04-poke/final-v14/scene.json').read_text());fps=s['fps'];g=next(l for l in s['layers']if l['id']=='p0262');ref=702;t=ref/fps;gx,gy,sx,sy=[at(g,k,t)for k in['x','y','scaleX','scaleY']];a=np.array(Image.open(p/f'measurements-v8/decoded/{ref:06}.png').convert('RGB'));x0,y0=int(gx+190*sx),int(gy+42*sy);x1,y1=int(gx+400*sx),int(gy+90*sy);roi=a[y0:y1,x0:x1];yy,xx=np.where(roi.max(2)<100);box=[int(xx.min()+x0),int(yy.min()+y0),int(xx.max()+x0+1),int(yy.max()+y0+1)];localx=(box[0]-gx)/sx;localy=(box[1]-gy)/sy;alpha=np.clip((228-a[box[1]:box[3],box[0]:box[2]].mean(2))/228,0,1);tw=round(alpha.shape[1]*.5/sx);th=round(alpha.shape[0]*.5/sy);tpl=np.array(Image.fromarray((alpha*255).astype('uint8')).resize((tw,th),Image.Resampling.LANCZOS)).astype(float)/255;target_text_x=662+localx*.5;left=max(0,int(round(802-target_text_x)));tpl=tpl[:,left:];template_global_x=target_text_x+left;out=[];source_frames=list(range(762,790))+[799]
for n in source_frames:
    row=dict(frame=n,time=n/fps,expected_control_g_y=at(g,'y',n/fps),control_actor_active=g.get('start',0)<=n/fps<g.get('end',s['duration']))
    for role,file in[('source',p/f'measurements-v8/decoded/{n:06}.png')]:
        a=np.array(Image.open(file).convert('RGB')).mean(2);best=None
        for y in range(242,263):
            for x in range(round(template_global_x)-3,round(template_global_x)+4):
                patch=255-a[y:y+th,x:x+tpl.shape[1]];yy,xx=np.mgrid[y:y+th,x:x+tpl.shape[1]];mask=~((xx>=800)&(xx<=818)&(yy>=332)&(yy<=377));mask&=~((xx>=640)&(xx<=850)&(yy>=125)&(yy<=190));v=tpl[mask];q=patch[mask]
                if len(v)<80:continue
                v=v-v.mean();q=q-q.mean();den=np.linalg.norm(v)*np.linalg.norm(q)
                if den<1:continue
                score=float(v.dot(q)/den)
                if best is None or score>best['correlation']:
                    amp=float(v.dot(q)/max(1,v.dot(v)));best=dict(title_tail_x=x,title_ink_y=y,inferred_g_y=y-localy*.5,inferred_photo_y=y-localy*.5+8.5,correlation=score,glyph_contrast=amp,visible_pixels=int(mask.sum()))
        row[role]=best
    out.append(row);print(row,flush=True)
(p/'measurements-v8/selected-header-title-late-v15.json').write_text(json.dumps(dict(method='Original702selected-title alpha template, projected to0.5scale; last visibleglyphs beyondx802. Weighted zero-mean correlation excludes foregroundheaderchevron andDynamicIsland. Native coordinate hypotheses require control recovery and source confidence; no opaque/censored position is forced.',reference_frame=ref,reference_title_bbox=box,title_local_origin=[localx,localy],target_template_shape=list(tpl.shape),measurements=out),indent=2))
