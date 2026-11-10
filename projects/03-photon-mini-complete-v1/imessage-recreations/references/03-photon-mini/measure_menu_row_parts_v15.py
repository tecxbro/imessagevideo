"""Measure independently moving copy and photo regions of six static UI assets."""
from pathlib import Path
import sys
import json
import math
import time
import numpy as np
sys.path.insert(0,'/tmp/imessage-food-cv')
import cv2
P = Path(__file__).resolve().parent
D = P/'menu-rows-v15'
cv2.setNumThreads(1)
cv2.setRNGSeed(57117)
sift = cv2.SIFT_create(nfeatures=2500,contrastThreshold=.008,edgeThreshold=12)
assets = json.loads((D/'assets-split.json').read_text())['rows']
whole = json.loads((D/'measurements.json').read_text())['frames']
for asset in assets:
    rgba = cv2.imread(asset['asset'],cv2.IMREAD_UNCHANGED)
    alpha = rgba[:,:,3].astype('float32')/255
    rgb = rgba[:,:,:3].astype('float32')*alpha[:,:,None]+253*(1-alpha[:,:,None])
    height,width = alpha.shape
    split = asset['copy_photo_split_x']
    asset.update(rgb=rgb,alpha=alpha,parts={})
    for role,left,right in [('copy',0,split),('photo',split,width)]:
        mask = np.zeros(alpha.shape,'uint8')
        mask[:-4,left:right] = np.uint8(alpha[:-4,left:right]>0)*255
        points,descriptors = sift.detectAndCompute(cv2.cvtColor(rgb.astype('uint8'),cv2.COLOR_BGR2GRAY),mask)
        asset['parts'][role] = dict(mask=mask,kp=points,desc=descriptors,box=[left,0,right,height-4])

def fit(features, source_points, matcher, prior):
    descriptors = features['desc']
    if descriptors is None:
        return dict(status='missing',cause='No reference descriptors')
    pairs = matcher.knnMatch(descriptors,k=2)
    good = [a for a,b in pairs if a.distance<.72*b.distance]
    result = dict(status='missing',ratio_matches=len(good))
    if len(good)<8:
        return result
    source = np.float32([features['kp'][m.queryIdx].pt for m in good])
    target = np.float32([source_points[m.trainIdx].pt for m in good])
    target[:,0] += 560
    matrix,inside = cv2.estimateAffine2D(source,target,method=cv2.RANSAC,ransacReprojThreshold=1.2,maxIters=5000,confidence=.999)
    if matrix is None:
        return result
    keep = inside[:,0]>0
    count = int(keep.sum())
    predictions = cv2.transform(source[None,:,:],matrix)[0]
    rms = float(np.sqrt(np.mean(np.sum((predictions[keep]-target[keep])**2,axis=1))))
    center = np.append(np.mean(source[keep],axis=0),1)
    distance = float(np.linalg.norm(matrix@center-prior@center))
    singular = np.linalg.svd(matrix[:,:2],compute_uv=False)
    span = np.ptp(source[keep],axis=0)
    result.update(inliers=count,inlier_RMS=rms,semantic_anchor_distance=distance,inlier_span=span.tolist(),candidate_matrix=matrix.tolist())
    valid = count>=10 and rms<1.2 and min(singular)>.2 and max(singular)<2.5 and np.linalg.det(matrix[:,:2])>0 and distance<100 and span[0]>40
    if valid:
        result.update(status='measured',matrix=matrix.tolist())
    return result

def optical(asset,role,matrix,source):
    height,width = asset['alpha'].shape
    left,top,right,bottom = asset['parts'][role]['box']
    points = cv2.transform(np.float32([[[left,top],[right,top],[right,bottom],[left,bottom]]]),matrix)[0]
    x0 = max(0,int(math.floor(points[:,0].min()))-2)
    y0 = max(0,int(math.floor(points[:,1].min()))-2)
    x1 = min(1920,int(math.ceil(points[:,0].max()))+2)
    y1 = min(1080,int(math.ceil(points[:,1].max()))+2)
    if x1<=x0 or y1<=y0:
        return dict(opacity=1.0,optical_status='offstage')
    local = matrix.copy()
    local[:,2] -= [x0,y0]
    rgb = cv2.warpAffine(asset['rgb'],local,(x1-x0,y1-y0),flags=cv2.INTER_LINEAR,borderValue=(253,253,253))
    mask = cv2.warpAffine(asset['parts'][role]['mask'].astype('float32')/255,local,(x1-x0,y1-y0))
    active = (mask>.99)&(np.linalg.norm(rgb-253,axis=2)>35)
    if active.sum()<20:
        return dict(opacity=1.0,optical_status='insufficient_visible_ink')
    template_values = (rgb-253)[active]
    actual_values = (source[y0:y1,x0:x1].astype('float32')-253)[active]
    ratios = np.sum(template_values*actual_values,axis=1)/np.maximum(1,np.sum(template_values*template_values,axis=1))
    opacity = float(np.clip(np.median(ratios),0,1))
    error = float(np.median(np.mean(abs(opacity*template_values-actual_values),axis=1)))
    return dict(opacity=opacity,median_photometric_error=error,visible_ink_pixels=int(active.sum()),optical_status='measured')

records = []
started = time.time()
for frame in whole:
    number = frame['frame']
    source = cv2.imread(str(P/'lunch-native'/f'{number-609:03}.png'))
    points,descriptors = sift.detectAndCompute(cv2.cvtColor(source[:,560:1360],cv2.COLOR_BGR2GRAY),None)
    matcher = cv2.FlannBasedMatcher(dict(algorithm=1,trees=4),dict(checks=64))
    matcher.add([descriptors])
    matcher.train()
    output = dict(frame=number,rows=[])
    for row in frame['rows']:
        if row['status']!='measured':
            continue
        index = row['row']
        prior = np.array(row['matrix'],dtype='float64')
        record = dict(row=index,parts={})
        for role in ['copy','photo']:
            record['parts'][role] = fit(assets[index]['parts'][role],points,matcher,prior)
        output['rows'].append(record)
    for record in output['rows']:
        index = record['row']
        asset = assets[index]
        prior = np.array(next(r for r in frame['rows'] if r['row']==index)['matrix'],dtype='float64')
        for role,part in record['parts'].items():
            if part['status']!='measured':
                borrowed = None
                if role=='copy':
                    for other in output['rows']:
                        other_index = other['row']
                        if other_index==index or assets[other_index]['source_frame']!=asset['source_frame']:
                            continue
                        other_copy = other['parts']['copy']
                        if other_copy['status']!='measured':
                            continue
                        translation = np.eye(3)
                        translation[:2,2] = np.array(asset['source_crop'][:2])-np.array(assets[other_index]['source_crop'][:2])
                        affine = np.vstack([np.array(other_copy['matrix']),[0,0,1]])@translation
                        borrowed = affine[:2]
                        part.update(status='shared_copy_plane',borrowed_from_row=other_index,cause='Same reference frame copy plane; photo selection motion is independent')
                        break
                if borrowed is None:
                    borrowed = prior
                    part.update(status='inherited_whole_plane',cause='Partial/occluded region; validated complete-row prior retained')
                part['matrix'] = borrowed.tolist()
            matrix = np.array(part['matrix'],dtype='float64')
            part.update(optical(asset,role,matrix,source))
    records.append(output)
    if (number-618)%16==0:
        (D/'parts-progress.json').write_text(json.dumps(dict(frames=records,elapsed=time.time()-started),indent=2))
result = dict(scope=[618,729],static_assets='assets-split.json',notice='Independent copy/photo planes use the same six static UI assets. Text and thumbnail load/selection transforms are not assumed rigid. Missing regions are explicitly tagged shared-copy-plane or inherited-whole-plane. No source frame/video playback.',frames=records,elapsed=time.time()-started)
(D/'parts-measurements.json').write_text(json.dumps(result,indent=2))
print('seconds',result['elapsed'])
print({role:sum(row['parts'][role]['status']=='measured' for frame in records for row in frame['rows']) for role in ['copy','photo']})
