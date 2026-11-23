from pathlib import Path
from PIL import Image
import numpy as np
import json,sys
p=Path(sys.argv[1]);src=Path('/tmp/sidehoe-hyperframes.wG3QA2/source-stage')
orange_left=[357,350,343,337,332,329,327,325,323,321,317,312]
orange_right=[400,405,410,414,413,410,408,406,403,402,401,398]
cyan_left=[442,434,428,420,416,414,412,410,410,410]
cyan_right=[485,491,497,503,506,508,508,507,505,503]
# The gray bubble and first response chip almost touch. Select the observed lower band.
top_guess_no=[491,494,497,500,502,503,503,503,503,503,503,502]
bot_no=[508,517,526,533,537,541,543,544,544,543,542,541]
top_guess_yes=[492,496,501,504,506,507,507,507,506,505]
bot_yes=[510,519,528,536,541,543,544,543,542,541]
def pigments(value):
    return np.rint(np.asarray(value)).astype(int).tolist()

def spec(img,frame,ix):
    i=frame-648-ix*2
    if i<0: return None
    labels=(
      (orange_left,orange_right,top_guess_no,bot_no),
      (cyan_left,cyan_right,top_guess_yes,bot_yes),
    )
    left,right,top,bottom=(list_[i] for list_ in labels[ix])
    h=bottom-top+1;w=right-left+1
    cx=(left+right)/2
    by=top+round(h*.25)
    box_x=[left+round(w*.14),left+round(w*.58)]
    box_y=[top+round(h*.18),min(bottom-2,top+round(h*.88))]
    l,t=box_x[0],box_y[0]
    region=img[t:box_y[1]+1,l:box_x[1]+1]
    y,x=np.where(np.max(region,axis=2)<148)
    end=left+round(w*(.49 if ix else .43))
    nbox=[left+round(w*.16),top+round(h*.26),end-left,round(h*.51)]
    if len(x)>=10:
        nbox=[int(l+x.min()),int(t+y.min()),int(x.max()-x.min()+1),int(y.max()-y.min()+1)]
        shade=int(np.percentile(region[y,x,0],12))
    else:
        shade=71 if i<3 else 35
    lx,rx=left+round(w*.59),min(right-2,left+round(w*.93))
    patch=img[top+2:bottom-1,lx:rx+1]
    red,green,blue=patch.transpose(2,0,1)
    m=(red>141)&(red-blue>38)&(green-blue>8)
    yy,xx=np.where(m)
    rw,eh=round(w*.24),round(h*.63)
    if len(xx)>9:
        emoji=[int(lx+xx.min()-1),int(top+yy.min()+1),int(xx.max()-xx.min()+3),int(yy.max()-yy.min()+3)]
    else:
        emoji=[left+round(w*.65),top+max(2,round(h*.14)),rw,eh]
    points=[]
    for fraction in (.15,.86):
        cut=round(left+w*fraction)
        q=img[top+max(1,round(h*.11)):top+max(3,round(h*.23)),cut-2:cut+3]
        points.append(np.median(q.reshape(-1,3),axis=0))
    if ix:
        g0,g1=[pigments(p) for p in points]
    else:
        tone=int(np.percentile(img[by:bottom-2,left+3:right-2,0],57))
        g0=g1=[tone]*3
    return dict(box=[left,top,right,bottom],gradient=[g0,g1],label=nbox,ink=shade,
                emoji=emoji, focus=1.35 if i<2 else .68)

result={}
for f in range(648,660):
    im=np.asarray(Image.open(src/f'{f:06}.png').convert('RGB'),dtype=np.int16)
    result[str(f)]=[spec(im,f,0),spec(im,f,1)]
    print(f,result[str(f)])
(p/'early-controls.json').write_text(json.dumps(result,indent=2)+'\n')
