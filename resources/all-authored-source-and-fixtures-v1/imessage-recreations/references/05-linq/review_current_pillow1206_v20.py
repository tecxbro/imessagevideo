"""Read-only current-picture/native qualification of Pillow's worst SSIM frame."""
from pathlib import Path
import hashlib,json,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFilter

R=Path.cwd();D=R/'verification/method-parity/05-linq/native-review/current-1206'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rgb(p):return np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
def compare(a,b):
 d=np.abs(a-b)
 return {'mae':float(d.mean()),'maxChannelDelta':int(d.max()),'differentPixels':int(np.any(d,axis=2).sum())}
sources={'native-gsap.png':R/'outputs/05-linq/frames-gsap/001206.png','native-pillow.png':R/'outputs/05-linq/cache/pillow/001206.png','source-1218.png':R/'references/05-linq/assets/root-late-measure/frame-1218.png','native-gsap-1218.png':R/'outputs/05-linq/frames-gsap/001218.png','native-pillow-1218.png':R/'outputs/05-linq/cache/pillow/001218.png'}
for name,src in sources.items():
 dst=D/name
 if not dst.exists():shutil.copy2(src,dst)
 assert sha(src)==sha(dst)
paths={k:D/f'{k}.png'for k in ['source','native-gsap','native-pillow','encoded-gsap','encoded-pillow']}
im={k:rgb(p)for k,p in paths.items()}
regions={'airport_labels':[80,45,888,135],'ATL_airplane_SFO':[70,170,890,282],'flat_blue_sky':[280,130,420,170],'white_panel':[74,352,882,720],'passenger_gate_seat':[95,395,855,520],'date_boarding':[120,580,850,700],'left_hardware':[0,0,42,720],'right_hardware':[920,0,960,720]}
rois=[]
for name,(x0,y0,x1,y1)in regions.items():
 cut=lambda key:im[key][y0:y1,x0:x1]
 rois.append({'name':name,'bounds':[x0,y0,x1,y1],'nativePvsG':compare(cut('native-pillow'),cut('native-gsap')),'sourceVsNativeP':compare(cut('source'),cut('native-pillow')),'sourceVsNativeG':compare(cut('source'),cut('native-gsap'))})
g=im['native-gsap'];v=np.zeros(g.shape[:2],dtype=np.int16)
v[:,1:]=np.maximum(v[:,1:],np.abs(g[:,1:]-g[:,:-1]).max(2));v[1:]=np.maximum(v[1:],np.abs(g[1:]-g[:-1]).max(2))
mask=np.asarray(Image.fromarray((v>=12).astype('uint8')*255).filter(ImageFilter.MaxFilter(7)))>0
delta=np.abs(g-im['native-pillow'])
edge={'definition':'NativeG adjacent-channel contrast>=12, expanded by3pixels via7×7 maximum filter. This is an observed spatial error attribution, not a universal exact filter model.','pixels':int(mask.sum()),'totalPixels':int(mask.size),'nativeErrorFractionWithinBand':float(delta[mask].sum()/delta.sum()),'withinBandMAE':float(delta[mask].mean()),'outsideBandMAE':float(delta[~mask].mean())}
for mode,keys in [('native',['source','native-gsap','native-pillow']),('encoded',['source','encoded-gsap','encoded-pillow'])]:
 sheet=Image.new('RGB',(960*3,744),'#eeeeee');draw=ImageDraw.Draw(sheet)
 for j,k in enumerate(keys):sheet.paste(Image.fromarray(im[k].astype('uint8')),(j*960,24));draw.text((j*960+4,4),f'1206 {k}',fill='black')
 sheet.save(D/f'{mode}-triptych.jpg',quality=96)
# Native-resolution text/edge crops make the dark ringing and preserved glyphs
# inspectable without reducing the original 960px image.
for title,box in [('airport',(70,45,890,135)),('code',(70,170,890,282)),('passenger',(95,395,855,520))]:
 x0,y0,x1,y1=box;w,h=x1-x0,y1-y0;sheet=Image.new('RGB',(w*3,h+24),'#eee');draw=ImageDraw.Draw(sheet)
 for j,k in enumerate(['source','native-gsap','native-pillow']):sheet.paste(Image.open(paths[k]).convert('RGB').crop(box),(j*w,24));draw.text((j*w+4,4),k,fill='black')
 sheet.save(D/f'native-{title}-detail.png')
qpaths={k:D/f'{k}-1218.png'for k in ['source','native-gsap','native-pillow']}
sheet=Image.new('RGB',(3*400,180),'#eee');draw=ImageDraw.Draw(sheet)
for j,(name,p)in enumerate(qpaths.items()):
 sheet.paste(Image.open(p).convert('RGB').crop((300,560,700,716)),(j*400,24));draw.text((j*400+3,3),f'1218 {name}',fill='black')
sheet.save(D/'barcode-1218-detail.png')
parity=json.load(open(R/'verification/method-parity/05-linq/pillow.json'));picture=R/'outputs/05-linq/pillow.mp4'
assert sha(picture)==parity['candidateSHA256']=='34143aa92f1179e6231e0e8126a4ca2a9c20c888650df994e95a3569deadb504'
report={'status':'qualified_with_explicit_native_edge_material_and_resampling_residual','sceneSHA256':sha(R/'outputs/05-linq/final-v20/scene.json'),'pillowPictureSHA256':sha(picture),'gsapPictureSHA256':sha(R/'outputs/05-linq/gsap.mp4'),'sourcePictureSHA256':sha(R/'references/05-linq/source.mp4'),'nativeFrame':1206,'nativeTime':40.2,'currentEncodedFullTimelineParity':{'frames':parity['frames'],'meanSSIM':parity['meanSSIM'],'minimumSSIM':parity['minimumSSIM'],'minimumFrame':parity['peaks'][0]['frame'],'requiresDiagnosis':parity['requiresDiagnosis']},'comparisons':{'nativePVsG':compare(im['native-pillow'],im['native-gsap']),'encodedPVsG':compare(im['encoded-pillow'],im['encoded-gsap']),'sourceVsNativeG':compare(im['source'],im['native-gsap']),'sourceVsNativeP':compare(im['source'],im['native-pillow']),'sourceVsEncodedP':compare(im['source'],im['encoded-pillow']),'pillowCodecVsOwnNative':compare(im['encoded-pillow'],im['native-pillow']),'gsapCodecVsOwnNative':compare(im['encoded-gsap'],im['native-gsap'])},'regions':rois,'edgeAttribution':edge,'findings':{'visibleUIComplete':True,'missingArtworkObserved':False,'blankOrTruncatedUIObserved':False,'lifecycleOrSemanticMismatchObserved':False,'visibleDetails':'Atlanta GA/TerminalB, SanFrancisco CA/TerminalD, ATL/airplane/SFO, Passenger/NikkiHanse, Gate37, Seat10C, Date2July2026 and Boarding2:50pm are present in source, nativeG/nativeP and encodedG/encodedP. The same lower content is clipped by the viewport in all1206 views.','materialResidual':'Pillow has sharper white airport/code glyph edges with dark surrounding ringing and some panel-edge/detail sampling differences, already visible natively. NativeG and source have softer edge/material profiles. Encoding adds a smaller separate change. These are real visible residuals, not claimed solely ordinary AA or proved original-filter identity.','barcode':'The boarding code is a horizontal barcode, not a square QR. It is outside the visible1206 crop in the original source too. Existing native1218/source1218 are additionally reviewed to verify the barcode and lower UI are present rather than dropped; no new render or sampling experiment was performed.','sourceIdentityClaim':False,'pixelIdentityClaim':False},'manualViews':['native-triptych.jpg','encoded-triptych.jpg','native-airport-detail.png','native-code-detail.png','native-passenger-detail.png','barcode-1218-detail.png'],'files':{p.name:{'path':str(p.relative_to(R)),'sha256':sha(p)}for p in list(paths.values())+list(qpaths.values())},'notice':'Read-only qualification from retained native PNGs and current encoded pictures. No scene, engine, production cache, master or sampler setting changed. Source/G image data are diagnostic only, never substituted into native production output.'}
(D/'qualification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'comparisons':report['comparisons'],'edgeAttribution':edge},indent=2))
