"""Recover a single static lower restaurant document component, not a frame sequence."""
from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates
D=Path(__file__).resolve().parent;R=D.parent.parent;B=R/'outputs/05-linq/final-v19';s=json.load(open(B/'scene.json'))
def absolute(o):
 if isinstance(o,dict):
  for k,v in o.items():
   if k=='src'and isinstance(v,str)and not v.startswith(('data:','http:','https:','/')):o[k]=str((B/v).resolve())
   else:absolute(v)
 elif isinstance(o,list):
  for q in o:absolute(q)
absolute(s);g=next(q for q in s['layers']if q['id']=='rich-group-14');yy,xx=np.mgrid[820:1000,188:774];out=np.ones((*yy.shape,3))*255;filled=np.zeros(yy.shape,bool);records=[]
for f in [1145,1146]:
 y=next(q['value']for q in g['keyframes']['y']if abs(q['t']*30-f)<1e-5);op=next(q['value']for q in g['keyframes']['opacity']if abs(q['t']*30-f)<1e-5);a=np.asarray(Image.open(D/'measurements/native-transition'/f'{f:06}.png').convert('RGB')).astype(float);sy=yy+y;valid=(sy>=0)&(sy<=719)&(~filled);sample=np.stack([map_coordinates(a[:,:,c],[sy,xx],order=1,mode='constant',cval=255,prefilter=False)for c in range(3)],2);rgb=np.clip((sample-255*(1-op))/op,0,255);out[valid]=rgb[valid];filled|=valid;records.append({'sourceFrame':f,'sourceY':y,'parentOpacity':op,'pixelCount':int(valid.sum()),'method':'Reproject shared static document coordinates and uncompose the existing parent opacity once.'})
asset=D/'assets/restaurant-lower-static-v20.png';Image.fromarray(np.uint8(np.rint(out))).save(asset)
node={'type':'image','id':'v20-restaurant-static-lower-document','src':str(asset.resolve()),'x':188,'y':820,'width':586,'height':180,'start':1144/30,'end':1149/30,'semanticText':'$30–90 per person; Reported by249 people; Find a table','editability':'One authentic static lower app-document artwork extension, independently positioned under the unchanged native document camera/opacity. Internal UI text is bitmap. No source frame sequence.','sourceFrames':[1145,1146],'sourceDocumentBounds':[188,820,774,1000]};index=next(i for i,q in enumerate(g['children'])if q['id']=='v10-restaurant-document');g['children'].insert(index+1,node);(D/'scene-restaurant-bottom-v20.json').write_text(json.dumps(s,indent=2)+'\n');(D/'restaurant-bottom-v20-elements.json').write_text(json.dumps(node,indent=2)+'\n');(D/'restaurant-bottom-v20-provenance.json').write_text(json.dumps({'records':records,'staticDocumentBounds':[188,820,774,1000],'sourceReferenceRole':'Two original views of the same unchanged lower UI; highest-opacity view supplies every available pixel, second supplies the newly exposed static bottom. One runtime texture only.','unfilledPixelsAssumedWhite':int((~filled).sum()),'oldDocumentHeight':860},indent=2)+'\n');print('static lower UI',asset,records)
