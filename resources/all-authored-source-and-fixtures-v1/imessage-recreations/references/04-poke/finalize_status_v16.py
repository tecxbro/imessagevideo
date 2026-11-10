"""Publish source04 status after actual canonicalv16 exports and delivered-file QA."""
from pathlib import Path
import hashlib,json,subprocess,collections
p=Path(__file__).parent;root=p.parent.parent;output=root/'outputs/04-poke';scene=output/'final-v16/scene.json';sha=hashlib.sha256(scene.read_bytes()).hexdigest();data=json.loads(scene.read_text());counts=collections.Counter();exports={}
def walk(nodes):
    for layer in nodes:
        counts[layer['type']]+=1
        walk(layer.get('children',[]))
walk(data['layers'])
for method in ['remotion','gsap']:
    movie=output/(method+'.mp4');meta=json.loads((output/(method+'.mp4.render.json')).read_text())
    if Path(meta['scene']).resolve()!=scene.resolve()or meta.get('sceneSHA256')!=sha:raise ValueError(method+' is stale')
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,avg_frame_rate,nb_frames,duration','-of','json',str(movie)]))['streams'][0]
    if (probe['width'],probe['height'],probe['r_frame_rate'],probe['avg_frame_rate'],probe['nb_frames'])!=(1440,1080,'30000/1001','30000/1001','1283'):raise ValueError(method+' cadence/geometry differs')
    exports[method]={'path':str(movie.relative_to(root)),'sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'bytes':movie.stat().st_size,'probe':probe,'render_seconds':meta['seconds'],'sceneSHA256':sha}
scanpath=root/'verification/timeline-scans/04-poke-v16/scan.json';peakpath=root/'verification/final/04-poke/source-gsap-v16/report.json';paritypath=output/'qa-v16-engine-parity/report.json';scan=json.loads(scanpath.read_text());peaks=json.loads(peakpath.read_text());parity=json.loads(paritypath.read_text())
if scan['frames_scanned']!=1283:raise ValueError('Incomplete delivered-file scan')
review=json.loads((p/'qa-v16-review.json').read_text())
if review.get('status')!='completed':raise ValueError('Native peak review is not complete')
if review.get('reviewed_picture_sha256')!=exports['gsap']['sha256']:raise ValueError('Peak review targets another picture export')
status={'final_scene':str(scene.relative_to(root)),'final_scene_sha256':sha,'fps_rational':'30000/1001','fps':30000/1001,'width':1440,'height':1080,'frames':1283,'duration':1283*1001/30000,'actual_scene_nodes':sum(counts.values()),'native_layer_counts':dict(counts),'exports':exports,'raster_policy':'Genuine static photos/maps/Memoji/logos and individually masked screen-transparent device hardware. Native editable UI/text/bubbles/sheets/controls/waveforms. No source video or complete reference frame output layers. Canonical asset-manifest records all referenced dependency hashes, including verified font subsets.','qa':{'timeline_scan':str(scanpath.relative_to(root)),'frames_scanned':scan['frames_scanned'],'mean_native_mae':scan['mean_native_mae'],'maximum_native_mae':scan['maximum_native_mae'],'native_peak_report':str(peakpath.relative_to(root)),'native_peak_summary':peaks['summary'],'engine_parity_report':str(paritypath.relative_to(root)),'engine_parity_summary':parity['summary'],'native_peak_review':'references/04-poke/qa-v16-review.json'},'prior_v7_full_scan':{'mean_native_mae':10.8430304,'maximum_native_mae':71.4735588},'changed_ranges_v15_to_v16_inclusive':json.loads((p/'changed-ranges-v16.json').read_text())['ranges'],'status':'Independent full1283-frame native primary exports and delivered-file every-frame/native-peak/engine-parity QA complete. No1:1 perfection certification.','known_residuals':review['known_residuals'],'audio':'Picture renders; root production workflow manages reference audio separately.'}
(p/'recreation-status.json').write_text(json.dumps(status,indent=2));final=json.loads((p/'final-v16-scene.json').read_text());final.update(status);(p/'final-scene.json').write_text(json.dumps(final,indent=2));print(json.dumps({'sceneSHA256':sha,'nodes':sum(counts.values()),'scan':{k:scan[k]for k in['frames_scanned','mean_native_mae','maximum_native_mae']},'exports':exports},indent=2))
