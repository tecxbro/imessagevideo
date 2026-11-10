"""Read-only video/cache review; writes qualification artifacts in this directory only."""
from pathlib import Path
import json,hashlib,importlib.util
from PIL import Image,ImageDraw
import numpy as np,cv2
D=Path(__file__).resolve().parent;R=D.parents[3];O=R/'outputs/02-danieltian';EXPECTED='729c783aa3a13f87c2e61d9a409a492adff9d27208ae6e092c3edfc2c2e8abee'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('native_compare',R/'verification/compare.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
requests={'source':[528,854,890],'gsap':[528,854,890],'pillow':[528],'motion-canvas':[890],'remotion':[854],'html':[854]};videoFiles={};cacheFiles={};metadata={};decoded={};sourceHashes={}
for method,frames in requests.items():
    file=R/'references/02-danieltian/source.mp4'if method=='source'else O/(method+'.mp4');videoFiles[method]=file;sourceHashes[method]=sha(file);info=m.probe(file);decoded[method]=m.batch_native_frames(file,[f/30 for f in frames],info,None,D/'decoded'/method)
    if method!='source':
        meta=json.loads(Path(str(file)+'.render.json').read_text());assert meta.get('sceneSHA256',meta.get('sceneSha256'))==EXPECTED;metadata[method]=meta;cacheFiles[method]={frame:Path(meta['frameDirectory'])/f'{frame:06d}.png'for frame in frames}
def array(path):return np.asarray(Image.open(path).convert('RGB')).astype(np.float32)
def metric(a,b,mask=None):
    delta=abs(a-b)
    if mask is not None:delta=delta[mask]
    if delta.size==0:return None
    return{'pixels':int(delta.size//3),'mae':float(delta.mean()),'rmse':float(np.sqrt(np.mean(delta*delta))),'maxChannel':int(delta.max()),'pixelsOver8':int((delta.max(-1)>8).sum())}
def regions(g):
    gray=cv2.cvtColor(g,cv2.COLOR_RGB2GRAY);gx=cv2.Sobel(gray,cv2.CV_32F,1,0,ksize=3)/8;gy=cv2.Sobel(gray,cv2.CV_32F,0,1,ksize=3)/8;edge=cv2.dilate((np.hypot(gx,gy)>8).astype(np.uint8),np.ones((5,5),np.uint8))>0;foreground=np.max(abs(g-253),axis=2)>12;bg=cv2.dilate(foreground.astype(np.uint8),np.ones((7,7),np.uint8))==0
    return{'edge':edge,'foregroundInterior':foreground&~edge,'flatBackground':bg}
rows=[]
for method,frame in[('pillow',528),('motion-canvas',890),('remotion',854),('html',854)]:
    g=array(decoded['gsap'][frame]);candidate=array(decoded[method][frame]);source=array(decoded['source'][frame]);rawG=array(cacheFiles['gsap'][frame]);rawC=array(cacheFiles[method][frame]);masks=regions(g);delta=abs(g-candidate);total=float(delta.sum());changed=delta.max(2)>8
    edgeShare=0.0
    if total:
        edgeShare=float(delta[masks['edge']].sum()/total)
    row={'method':method,'frame':frame,'sceneSHA256':EXPECTED,'candidateMovieSHA256':sourceHashes[method],'gsapMovieSHA256':sourceHashes['gsap'],'sourceMovieSHA256':sourceHashes['source'],'decodedVsGSAP':metric(g,candidate),'rawPNGvsGSAP':metric(rawG,rawC),'sourceVsGSAP':metric(source,g),'sourceVsCandidate':metric(source,candidate),'decodedToOwnRawPNG':metric(rawC,candidate),'regionMetrics':{name:metric(g,candidate,mask)for name,mask in masks.items()},'absoluteErrorShareOnEdges':edgeShare,'over8PixelShareOnEdges':float((changed&masks['edge']).sum()/max(1,changed.sum())),'decodedPNG_SHA256':sha(decoded[method][frame]),'rawPNG_SHA256':sha(cacheFiles[method][frame])}
    rows.append(row)
    views=[('Source',source),('G19',g),(method,candidate),('8x difference',np.minimum(255,delta*8))];canvas=Image.new('RGB',(1920,290),'white');draw=ImageDraw.Draw(canvas)
    for col,(label,im)in enumerate(views):
        view=Image.fromarray(np.clip(im,0,255).astype('uint8')).resize((480,270));canvas.paste(view,(col*480,20));draw.text((col*480,0),f'{frame} {label}',fill='red')
    canvas.save(D/f'{method}-{frame}-contact.jpg')
for method,file in videoFiles.items():assert sha(file)==sourceHashes[method],('Movie changed during review',method)
(D/'metrics.json').write_text(json.dumps({'sceneSHA256':EXPECTED,'readOnlyMastersAndCaches':True,'movieHashes':sourceHashes,'maskDefinition':'Edge: GSAP decoded luma Sobel gradient>8, dilated2px. Foreground: RGB distance from253>12. Interior: foreground excludingedges. Flatbackground: outside3pxforeground dilation.','rows':rows},indent=2));print(json.dumps(rows,indent=2),flush=True)
