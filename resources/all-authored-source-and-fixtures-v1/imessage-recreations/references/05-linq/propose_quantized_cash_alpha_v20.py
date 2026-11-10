"""Read-only alpha-byte calibration; never mutates the parent's candidate."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
R=Path.cwd()
scene_path=R/'outputs/05-linq/final-v19/scene.json'
scene=json.load(open(scene_path))
root=next(q for q in scene['layers'] if q['id']=='linq-measured-v6-group-36')
panel=next(q for q in root['children'] if q['id']=='v10-cash-panel')
image=next(q for q in panel['children'] if q['id']=='v10-cash-panel-ui')
rgba=np.asarray(Image.open(scene_path.parent/image['src']).convert('RGBA')).astype(float)
gray=rgba[:,:,:3].mean(2)
yy,xx=np.mgrid[:gray.shape[0],:gray.shape[1]]
mask=(gray<25)&(rgba[:,:,3]>250)&(xx>20)&(xx<gray.shape[1]-20)&(yy>20)&(yy<gray.shape[0]-20)
# Independent amount/control actors cover otherwise dark pixels in the static plate.
world_x=xx+image['x']
world_y=yy+image['y']
mask &= ~((world_x>=260)&(world_x<=745)&(world_y>=330)&(world_y<=475))
sy,sx=np.where(mask)
sy,sx=sy[::5],sx[::5]
rows=[]
for frame in range(773,838):
    py=next(q['value'] for q in panel['keyframes']['y'] if round(q['t']*30)==frame)
    old_alpha=next(q['value'] for q in panel['keyframes']['opacity'] if round(q['t']*30)==frame)
    old_byte=round(old_alpha*255)
    source_path=R/f'references/05-linq/measurements/composer-v19/native/source-{frame:06}.png'
    if not source_path.exists():
        source_path=R/f'references/05-linq/measurements/native-transition/{frame:06}.png'
    source=np.asarray(Image.open(source_path).convert('RGB')).astype(float)
    old=np.asarray(Image.open(R/f'outputs/05-linq/frames-gsap/{frame:06}.png').convert('RGB')).astype(float)
    wy=sy+round(image['y']+py)
    wx=sx+round(image['x'])
    valid=(wy>=0)&(wy<720)
    ay,ax,wy,wx=sy[valid],sx[valid],wy[valid],wx[valid]
    observed=source[wy,wx].mean(1)
    rendered=old[wy,wx].mean(1)
    material=gray[ay,ax]
    keep=observed<50
    observed,rendered,material=observed[keep],rendered[keep],material[keep]
    if len(observed)<100:
        rows.append({'frame':frame,'oldAlpha':old_alpha,'proposalAlpha':old_alpha,'samples':len(observed),'reason':'Insufficient flat material; preserve measured current state.'})
        continue
    n=np.arange(220,256)[:,None]
    prediction=(255-n)+np.floor(material[None,:]*n/255)
    costs=np.abs(prediction-observed).mean(1)
    best_cost=float(costs.min())
    best=[int(220+i) for i,cost in enumerate(costs) if abs(cost-best_cost)<1e-9]
    chosen=min(best,key=lambda value:abs(value-old_byte))
    old_prediction=(255-old_byte)+np.floor(material*old_byte/255)
    rows.append({'frame':frame,'oldAlpha':old_alpha,'oldByte':old_byte,'proposalByte':chosen,'proposalAlpha':old_alpha if chosen==old_byte else chosen/255,'samples':len(observed),'predictedOldVsActualNativeMAE':float(np.abs(old_prediction-rendered).mean()),'oldBodyMAE':float(np.abs(rendered-observed).mean()),'predictedNewBodyMAE':best_cost})
report={'method':'Empirical 8-bit premultiplied-floor candidate model; read-only proposal. Body pixels only, no runtime data mutation. Actual native revalidation remains required.','rows':rows}
Path('verification/05-cash-quantized-alpha-proposal.json').write_text(json.dumps(report,indent=2)+'\n')
for row in rows:
    if row['frame'] in [777,810,820,828,833,837]:
        print(row)
print('mean old prediction vs actual native',np.mean([r['predictedOldVsActualNativeMAE'] for r in rows if 'predictedOldVsActualNativeMAE' in r]))
