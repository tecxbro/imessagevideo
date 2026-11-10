"""Read-only native/encoded qualification of the extreme menu shutter samples."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
R=Path.cwd()
D=R/'verification/method-parity/05-linq/native-review'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rgb(path):
    return np.asarray(Image.open(path).convert('RGB')).astype(float)
def compare(a,b):
    delta=np.abs(a-b)
    return {'mae':float(delta.mean()),'maxChannelDelta':int(delta.max())}
def cosine(a,b):
    return float(a@b/max(np.linalg.norm(a)*np.linalg.norm(b),1e-12))
def mass(plane,box):
    x0,y0,x1,y1=box
    a=plane[y0:y1,x0:x1]
    yy,xx=np.mgrid[y0:y1,x0:x1]
    total=float(a.sum())
    return {'mass':total,'center':[float((a*xx).sum()/max(total,1e-12)),float((a*yy).sum()/max(total,1e-12))],'xProjection':a.sum(0)}
rows=[]
for method,frame in [('pillow',111),('pillow',113),('motion-canvas',112)]:
    paths={'nativeG':R/f'outputs/05-linq/frames-gsap/{frame:06}.png','nativeCandidate':R/f'outputs/05-linq/cache/{method}/{frame:06}.png','encodedG':D/'gsap'/f'encoded-{frame:06}.png','encodedCandidate':D/method/f'encoded-{frame:06}.png'}
    a,b,c,e=[rgb(paths[k])for k in ['nativeG','nativeCandidate','encodedG','encodedCandidate']]
    ia,ib=255-a.mean(2),255-b.mean(2)
    bands=[('Photos',15,145),('AppleCash',145,300),('Polls',300,456),('Store',456,623),('GamePigeon_partial',623,683)] if frame in [111,112] else [('Photos_partial',10,50),('AppleCash',50,210),('Polls',210,377),('Store',377,551),('GamePigeon',551,686)]
    rois=[]
    for name,y0,y1 in bands:
        for kind,(x0,x1)in [('icon',(175,300)),('label',(310,790))]:
            ga,cb=mass(ia,[x0,y0,x1,y1]),mass(ib,[x0,y0,x1,y1])
            rois.append({'row':name,'kind':kind,'bounds':[x0,y0,x1,y1],'inkMassRatio':cb['mass']/max(ga['mass'],1e-12),'centerDelta':[cb['center'][i]-ga['center'][i]for i in range(2)],'horizontalInkProjectionCosine':cosine(ga['xProjection'],cb['xProjection'])})
    rows.append({'method':method,'frame':frame,'nativeCandidateVsNativeG':compare(a,b),'encodedCandidateVsEncodedG':compare(c,e),'candidateEncodedVsOwnNative':compare(b,e),'gsapEncodedVsOwnNative':compare(a,c),'regions':rois,'files':{k:{'path':str(p.relative_to(R)),'sha256':sha(p)}for k,p in paths.items()},'visualFindings':'Both native and encoded views retain the same visible menu rows, labels and icons in the same clipped viewport. Pillow has coarser/harder vertical streak and icon contours; Motion Canvas has smaller blur-profile/sampling differences. No blank frame or missing interior artwork is observed.'})
report={'sceneSHA256':sha(R/'outputs/05-linq/final-v20/scene.json'),'pictureHashes':{m:sha(R/f'outputs/05-linq/{m}.mp4')for m in ['gsap','pillow','motion-canvas']},'rows':rows,'manualViews':[f'{m}-{f}-{k}.jpg'for m,f in [('pillow',111),('pillow',113),('motion-canvas',112)]for k in ['native','encoded']],'authoredTransformAt111':{'outerScaleX':15.863001089967632,'outerScaleY':0.09188875011989424,'inverseScaleX':0.06303977376843517,'inverseScaleY':10.882725020149081},'implementationEvidence':{'pillowEngine':'engines/render_pillow.py','pillowEngineSHA256':sha(R/'engines/render_pillow.py'),'nativeAntialias':1,'groupRasterizationLines':'239–254','bicubicAffineCompositeLine':154,'gaussianFilterLines':'159–165','interpretation':'Opposing nonuniform transforms implement the directional shutter. Pillow rasterizes each group into an integer local surface, applies Gaussian blur there, and bicubic-composites the result. The extreme local compression/expansion therefore permits coarse intermediate sampling and different kernel/edge profiles. This is consistent with observed native streak/block contour differences. The review does not claim a universal exact error decomposition or source-pixel identity.'},'qualification':{'nativeAndEncodedReviewed':True,'missingInteriorArtworkObserved':False,'stateOrLifecycleMismatchObserved':False,'classification':'documented extreme-anisotropic-blur and intermediate-raster/resampling residual','acceptedForFinalMuxWithDocumentedResidual':False,'status':'held_for_dense_AA4_source_refinement','pixelIdentityClaim':False,'sourceIdentityClaim':False},'notice':'Read-only qualification; no master, scene or cache changed. Outlier flag remains present and is explained, not erased. These frames were outside the651 capture union and retained from actual13; current20 scene and picture hashes bind this review.'}
(D/'qualification.json').write_text(json.dumps(report,indent=2)+'\n')
for row in rows:
    print(row['method'],row['frame'],row['nativeCandidateVsNativeG'],row['encodedCandidateVsEncodedG'],'codec',row['candidateEncodedVsOwnNative'])
    print([(r['row'],r['kind'],round(r['inkMassRatio'],4),[round(v,3)for v in r['centerDelta']],round(r['horizontalInkProjectionCosine'],5))for r in row['regions']])
print('qualification',D/'qualification.json')
