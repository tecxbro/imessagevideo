"""Independent white f2→f3 motion and post-move selection state; no board camera edit."""
from pathlib import Path
import copy,json
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent; ROOT=D.parent.parent
M=D/'root-white-pawn-v19'; M.mkdir(exist_ok=True)
def find(layers,identity):
 for layer in layers:
  if layer['id']==identity:return layer
  found=find(layer.get('children',[]),identity)
  if found is not None:return found

def prepare():
 a=np.array(Image.open(D/'measurements/native-transition/000233.png').convert('RGB'))
 patch=a[357:593,557:641].copy()
 # Recover the authentic static selected cells/undo UI. Remove the independent
 # moving pawn; the original sprite supplies its ink on the measured trajectory.
 for yy in range(85,157):
  left=np.median(patch[yy,:14],axis=0);right=np.median(patch[yy,74:],axis=0)
  for xx in range(14,74):patch[yy,xx]=np.clip(left+(right-left)*(xx-14)/60,0,255)
 Image.fromarray(patch).save(M/'post-move-selection-233.png')
 base=json.loads((ROOT/'outputs/05-linq/final-v18/scene.json').read_text());pawn=find(base['layers'],'broad-v5-image-17')
 sprite=np.array(Image.open(ROOT/'outputs/05-linq/final-v18'/pawn['src']).convert('RGBA'))
 white=(sprite[:,:,:3].min(2)>200)&(sprite[:,:,3]>200);rr=np.where(white.sum(1)>=3)[0];offset=int(rr[0]);poses=[]
 for n in range(226,233):
  src=np.array(Image.open(D/'measurements/native-transition'/f'{n:06}.png').convert('RGB'))
  r=src[430:535,574:618];mask=(r.min(2)>200)&(r.max(2)-r.min(2)<35);yy=np.where(mask.sum(1)>=3)[0]
  y=float(430+yy[0]-offset)
  poses.append({'frame':n,'y':y,'referenceCoreTop':int(430+yy[0])})
 (M/'measurements.json').write_text(json.dumps({'spriteWhiteCoreLocalTop':offset,'poses':poses,'materialFrame':233,'materialBounds':[557,357,641,593],'pawnRemovedBoundsWithinMaterial':[14,85,74,157]},indent=2)+'\n')
 return poses

def apply_white_pawn(scene):
 poses=json.loads((M/'measurements.json').read_text())['poses'];board=find(scene['layers'],'broad-v5-group-20');pawn=find(board['children'],'broad-v5-image-17');selection=find(board['children'],'v10-selection-art')
 # Preserve every earlier value and the exact original settled425 after232.
 pawn['keyframes']['y']=[q for q in pawn['keyframes']['y']if q['t']<=225/30]+[{'t':p['frame']/30,'value':p['y'] if p['frame']<232 else 425,'ease':'linear'}for p in poses]
 for k in selection['keyframes']['opacity']:
  if 228<=round(k['t']*30)<=238:k['value']=0
 new={'id':'root-white-pawn-post-move-selection-v19','type':'image','src':str((M/'post-move-selection-233.png').resolve()),'x':405,'y':357,'width':84,'height':236,'start':228/30,'end':239/30,'semanticText':'Selected f3 cell and undo control on f2','sourceFrame':233,'sourceBounds':[557,357,641,593],'editability':'One bounded authentic static app UI material; moving white pawn is removed and independently animated. Board and camera are preserved.'}
 board['children'].insert(board['children'].index(pawn),new)
 return scene

if __name__=='__main__':
 prepare();source=ROOT/'outputs/05-linq/final-v18/scene.json';s=json.loads(source.read_text())
 def absolutize(layers):
  for l in layers:
   if l.get('src')and not l['src'].startswith('data:'):l['src']=str((source.parent/l['src']).resolve())
   absolutize(l.get('children',[]))
 absolutize(s['layers'])
 for f in s.get('fonts',[]):f['src']=str((source.parent/f['src']).resolve())
 apply_white_pawn(s);out=ROOT/'outputs/05-linq/root-white-pawn-v19';out.mkdir(exist_ok=True);(out/'scene.json').write_text(json.dumps(s,indent=2)+'\n');print(M/'measurements.json');print(out/'scene.json')
