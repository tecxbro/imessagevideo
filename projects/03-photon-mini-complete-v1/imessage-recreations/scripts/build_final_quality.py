#!/usr/bin/env python3
"""Collect hash-bound source, renderer and mux evidence for the final package."""
from pathlib import Path
import hashlib,json

ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads((ROOT/path).read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    hold_path=ROOT/'verification/delivery-holds.json'
    holds=json.loads(hold_path.read_text()) if hold_path.exists() else {'holds':[]}
    unresolved=[q for q in holds['holds'] if q['status']!='resolved']
    if unresolved:raise ValueError('Known delivery holds remain: '+', '.join(q['reference']+'/'+q['method'] for q in unresolved))
    state=read('delivery-state.json')
    validation=read('verification/delivery-validation.json')
    parity=read('verification/method-parity/report.json')['comparisons']
    if validation['errors'] or validation['validated']!=30:
        raise ValueError('Thirty current audio deliveries must pass validation first')
    if len(parity)!=24:raise ValueError('Expected four dense method comparisons for each of six scenes')
    rows=[]
    for identity,entry in state['scenes'].items():
        scene=ROOT/entry['scene'];digest=sha(scene)
        scan=read(entry['timeline_scan'])
        picture=ROOT/'outputs'/identity/'gsap.mp4';picture_hash=sha(picture)
        reference_hash=sha(ROOT/'references'/identity/'source.mp4')
        if scan.get('sceneSHA256')!=digest or scan.get('candidateSHA256')!=picture_hash:
            raise ValueError('Stale source scan: '+identity)
        if scan.get('referenceSHA256')!=reference_hash:
            raise ValueError('Source changed after timeline scan: '+identity)
        peak=read(str(Path(entry['source_report']).parent/'report.json'))
        if peak['candidate'].get('sha256')!=picture_hash or peak['reference'].get('sha256')!=reference_hash:
            raise ValueError('Stale peak comparison: '+identity)
        methods=[q for q in parity if q['reference']==identity]
        if len(methods)!=4:raise ValueError('Incomplete method coverage: '+identity)
        for q in methods:
            candidate=picture.with_name(q['method']+'.mp4')
            if q['sceneSHA256']!=digest or q['gsapSHA256']!=picture_hash or q['candidateSHA256']!=sha(candidate):
                raise ValueError('Stale method comparison: '+identity+'/'+q['method'])
            if q['requiresDiagnosis'] and not q.get('diagnosis'):
                raise ValueError('Unreviewed method discrepancy: '+identity+'/'+q['method'])
        deliveries=[q for q in validation['videos'] if q['reference']==identity]
        if len(deliveries)!=5 or any(q['sceneSHA256']!=digest or not q.get('picturePacketsUnchanged') for q in deliveries):
            raise ValueError('Stale or changed muxed pictures: '+identity)
        rows.append(dict(reference=identity,scene=entry['scene'],sceneSHA256=digest,
            sourceScan=entry['timeline_scan'],sourcePeakReview=entry['source_report'],
            sourceFramesCompared=scan['frames_scanned'],meanSourceRGBError=scan['mean_native_mae'],
            maximumSourceRGBError=scan['maximum_native_mae'],separatedErrorPeaks=scan['peaks'],
            methodFramesCompared=sum(q['frames'] for q in methods),
            methodComparisons=[dict({k:q[k] for k in ['method','frames','meanSSIM','minimumSSIM','requiresDiagnosis']},
                diagnosisReasons=q.get('diagnosisReasons',[]),diagnosis=q.get('diagnosis')) for q in methods],
            soundtrackVersions=5,picturePacketsUnchanged=True))
    result=dict(status='Measured recreations with residual differences; pixel identity is not claimed',
        sourceFramesCompared=sum(r['sourceFramesCompared'] for r in rows),
        methodFramesCompared=sum(r['methodFramesCompared'] for r in rows),
        completedVideos=30,encodingProfile=state['encoding_profile'],videos=rows,
        availableMethods=['Remotion','GSAP','HTML/SVG','Pillow + FFmpeg','Motion Canvas'],
        figma=read('figma/status.json'),
        editability='Independent scene layers, numeric timing/cameras and semantic vector outlines. Bounded original photos, rich UI/card interiors, hardware and short optical component poses retain bitmap pixels; those internal pixels are not live editable text.',
        limitations=['Source compression and its unspecified color metadata limit decoder-independent pixel comparison.',
            'Residual differences in measured edge placement, artwork deformation, blur, typography and optical material remain. The source scans and native peak reports show their actual magnitude.',
            'Dense renderer parity compares each method to GSAP and does not establish source identity.'],
        resolvedDeliveryHolds=holds['holds'],
        evidence='Source comparisons cover every retained native frame; four other methods are compared densely to that measured GSAP timeline. All thirty audio versions preserve the independently rendered H.264 packet payloads.')
    destination=ROOT/'verification/final-quality.json';destination.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['completedVideos','sourceFramesCompared','methodFramesCompared','status']},indent=2))

if __name__=='__main__':main()
