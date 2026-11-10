from pathlib import Path
import json,numpy as np,sys,copy
sys.path.insert(0,'/tmp/imessage-food-cv');import cv2
from PIL import Image
from scipy import ndimage
R=Path(__file__).resolve().parent

def weighted_median(values,weights):
    order=np.argsort(values)
    return float(values[order][np.searchsorted(np.cumsum(weights[order]),weights.sum()/2)])

def source(f):return np.asarray(Image.open(R/'source-native'/f'source-{f:04d}.png').convert('RGB')).astype(float)
def native(folder,f):return np.asarray(Image.open(R/folder/f'{f/30:.3f}.png').convert('RGB')).astype(float)
records={}
for first,last in [(770,778),(920,926)]:
    for f in range(first,last+1):
        s=source(f);b=native('native-letter-base',f);c=native('native-candidate',f);delta=c-b;mask=delta>8;alpha=weighted_median(((s-b)/np.maximum(delta,.01))[mask],delta[mask]);records[str(f)]=float(np.clip(alpha,0,1))
labelrows=json.loads((R/'label-measurements.json').read_text())['rows']
for row in labelrows:
    f=row['frame']
    if not row['needsCorrection']:continue
    c=native('native-candidate',f);s=source(f);left,top,right,bottom=row['matchedGlyphBounds'];box=(slice(max(0,int(top)-1),min(1080,int(bottom)+2)),slice(int(left)-1,int(right)+2));cc=c[box];ss=s[box];ink=253-cc;mask=ink>25;ratio=(253-ss)/np.maximum(ink,.01);row['opacity']=float(np.clip(weighted_median(ratio[mask],ink[mask]),0,1))
(R/'label-measurements-refined.json').write_text(json.dumps({'rows':labelrows},indent=2))
avdata=json.loads((R/'avatar-measurements.json').read_text());rows=avdata['rows'];chat=json.loads((R/'chat-original.json').read_text());av=next(n for n in chat['children']if n['id']=='middle-avatar-how-about');im=av['children'][0];art=np.asarray(Image.open(im['src']).convert('RGBA'));hsv=cv2.cvtColor(art[:,:,:3],cv2.COLOR_RGB2HSV);m=(hsv[:,:,0]>158)&(hsv[:,:,0]<178)&(hsv[:,:,1]>12)&(art[:,:,3]>127);yy,xx=np.nonzero(m);local=np.array([xx.min(),yy.min(),xx.max()+1,yy.max()+1])*[126/art.shape[1],126/art.shape[0],126/art.shape[1],126/art.shape[0]]
for f in [811,812]:
    a=source(f).astype('uint8');hsv=cv2.cvtColor(a[850:1080,330:495],cv2.COLOR_RGB2HSV);mask=(hsv[:,:,0]>158)&(hsv[:,:,0]<178)&(hsv[:,:,1]>12)&(hsv[:,:,2]>100);lab,n=ndimage.label(mask);sizes=np.bincount(lab.ravel());sizes[0]=0;yy,xx=np.nonzero(lab==sizes.argmax());left,top,right,bottom=[xx.min()+330,yy.min()+850,xx.max()+331,yy.max()+851];diameter=109;scale=diameter/(local[2]-local[0]);pose={'x':float((left+right)/2-diameter/2-local[0]*scale),'y':float(top-local[1]*scale),'scaleX':float(scale),'scaleY':float(scale)};row=next(q for q in rows if q['frame']==f);row.update({'measuredPose':pose,'sourceColorBounds':[int(left),int(top),int(right),int(bottom)],'needsCorrection':True,'partialEntry':True})
for row in rows:
    if not row.get('needsCorrection'):continue
    f=row['frame'];p=row['measuredPose'];M=np.float32([[p['scaleX']*126/art.shape[1],0,p['x']],[0,p['scaleY']*126/art.shape[0],p['y']]]);full=cv2.warpAffine(art.astype('float32'),M,(1920,1080),flags=cv2.INTER_LINEAR);alpha=full[:,:,3:]/255;c=full[:,:,:3]*alpha+253*(1-alpha);s=source(f);mask=(c[:,:,1]<200)&(c[:,:,0]-c[:,:,1]>35)&(alpha[:,:,0]>.8);ink=253-c;use=mask[:,:,None]&(ink>30);ratio=(253-s)/np.maximum(ink,.01);row['opacity']=float(np.clip(weighted_median(ratio[use],ink[use]),0,1))
(R/'avatar-measurements-refined.json').write_text(json.dumps({'rows':rows},indent=2));(R/'copy-opacity-refined.json').write_text(json.dumps(records,indent=2));print('copy',records);print('label',[(q['frame'],round(q.get('opacity',0),3))for q in labelrows if q['needsCorrection']]);print('orb',[(q['frame'],round(q.get('opacity',0),3))for q in rows if q.get('needsCorrection')])
