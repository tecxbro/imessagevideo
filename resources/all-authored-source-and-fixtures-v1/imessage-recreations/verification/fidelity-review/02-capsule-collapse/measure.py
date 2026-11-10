from pathlib import Path
from PIL import Image
import numpy as np, json
from scipy import ndimage
root = Path('/workspace/imessage-recreations')
review = root / 'verification/fidelity-review/02-capsule-collapse'
scene = json.load(open(root/'outputs/02-danieltian/final-v12/scene.json'))
assetroot = root/'outputs/02-danieltian/final-v12'
def find(layer, id):
    if layer['id'] == id: return layer
    for child in layer.get('children', []):
        result = find(child, id)
        if result: return result

def colored(image, provider):
    r,g,b = image[:,:,0],image[:,:,1],image[:,:,2]
    if provider == 'lyft': return (r>150)&(g<110)&(b>140)
    if provider == 'airbnb': return (r>170)&(g<120)&(b<150)
    return (r>160)&(g<120)&(b<120)

def components(mask):
    labels, count = ndimage.label(mask)
    stats = [[0,0,0,0,0]]
    for index, box in enumerate(ndimage.find_objects(labels), 1):
        if box is None: stats.append([0,0,0,0,0]); continue
        ys,xs = box
        stats.append([xs.start,ys.start,xs.stop-xs.start,ys.stop-ys.start,int((labels[box]==index).sum())])
    return count+1,labels,np.array(stats),None

bodies = {}
for provider in ['lyft','airbnb','resy']:
    group = next(l for l in scene['layers'] if l['id']=='pb-capsule-'+provider)
    image = np.array(Image.open(assetroot/find(group,'pb-'+provider+'-body')['src']).convert('RGB'))
    yy,xx=np.where(colored(image[:110,:110],provider))
    bodies[provider] = dict(minX=int(xx.min()),minY=int(yy.min()),maxX=int(xx.max()),maxY=int(yy.max()))

results=[]
for frame in range(522,548):
    source=np.array(Image.open(review/'source'/f'{frame-521:04d}.png').convert('RGB'))
    row=dict(frame=frame,providers={})
    for provider,y0,y1 in [('lyft',390,575),('airbnb',550,720),('resy',700,900)]:
        crop=source[y0:y1,640:820]; yy,xx=np.where(colored(crop,provider))
        if not len(xx): continue
        # Restrict to largest colored logo component; other incoming graphics are excluded.
        n, labels, stats, centers = components(colored(crop,provider))
        index=1+stats[1:,4].argmax(); x,y,w,h,area=stats[index]
        X=640+x-bodies[provider]['minX'];Y=y0+y-bodies[provider]['minY']
        region=source[max(0,Y):min(1080,Y+117),X:X+610]
        neutral=(region.max(2)-region.min(2)<5)&(region.min(2)<246)&(region.min(2)>185)
        neutral=ndimage.binary_closing(neutral,structure=np.ones((3,3)))
        n,labs,stats,cents=components(neutral)
        candidates=[i for i in range(1,n)if stats[i,0]<8 and stats[i,3]>60]
        if candidates:
            i=max(candidates,key=lambda i:stats[i,4]);rx,ry,rw,rh,area=stats[i];width=int(rx+rw);bbox=[int(v)for v in stats[i,:4]]
        else:width=None;bbox=None
        row['providers'][provider]=dict(x=int(X),y=int(Y),logo_bbox=[int(x+640),int(y+y0),int(w),int(h)],width=width,border_component=bbox)
    results.append(row)
(review/'measurements.json').write_text(json.dumps(dict(canonical_logo_bounds=bodies,frames=results),indent=2))
for row in results:print(row['frame'],[(name,p['x'],p['y'],p['width'])for name,p in row['providers'].items()])
