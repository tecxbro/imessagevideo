"""Normalize the three source studies; extract only selected native video frames."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image,ImageDraw,ImageFont
import csv,hashlib,io,json,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'skill/imessage-motion-recreation/director'
def read(p):return json.loads(p.read_text())
def js(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def prose(x):return ' '.join(str(v) for v in x) if isinstance(x,list) else str(x)
def sparse(values,n=5):
    if len(values)<=n:return values
    return [values[round(i*(len(values)-1)/(n-1))] for i in range(n)]
def bindings(layers):
    result=[]
    for l in layers[:4]:
        tracks=l.get('property_keyframes',l.get('keyframes',{}))
        if not tracks and l.get('keyframe_examples'):
            tracks={k:v.get('actual_selected_keys',[]) for k,v in l['keyframe_examples'].items()}
        tracks={k:sparse(v) for k,v in tracks.items() if isinstance(v,list) and k!='d'}
        result.append({'id':l.get('id',l.get('layer_id',l.get('node_id'))),'ancestors':l.get('parent_ids',l.get('ancestor_ids',l.get('parent_id'))),
                       'type':l.get('type',l.get('static_properties',{}).get('type')),
                       'literal_key_excerpts':dict(list(tracks.items())[:4])})
    return result

quality=read(ROOT/'verification/final-quality.json');sources={v['reference']:v for v in quality['videos']}
studies=[];source_dir=D/'source-studies';source_dir.mkdir(parents=True,exist_ok=True)
for name in ['photon','mini-poke','linq-rene']:
    shutil.copy2(ROOT/'skill-upgrade'/f'{name}-recipes.json',source_dir/f'{name}-recipes.json')

p=read(ROOT/'skill-upgrade/photon-recipes.json')
pmap={'press-release':['selection-confirm'],'channel-walls':['message-wall'],'compose-send':['conversation-handoff'],'agent-convergence':['card-orbit'],'thread-camera-overlap':['camera-focus','conversation-handoff']}
for r in p['recipes']:
    film=r['range']['reference_id'];examples=r['measured_source_recreation'].get('actual_property_examples',[])
    if not isinstance(examples,list):examples=[]
    studies.append({'id':'photon-'+r['id'],'title':r['title'],'film':film,'starters':pmap[r['id']],
                    'intent':r['director_reading'],'choose':r['director_reading'],
                    'avoid':'Do not substitute a generic spring/orbit for the measured source motion.',
                    'anatomy':prose(r['visual_design_notes']),
                    'caveat':r['measured_source_recreation']['status']+' '+r['new_reusable_choreography']['rule'],
                    'frames':[{'source':a['source_native_frame'],'output':a['output_native_frame'],'label':a['label']} for a in r['atlas']],
                    'range':r['range'],'scene':p['sources'][film]['canonical_scene'],'bindings':bindings(examples),
                    'evidence':{'rich_study':'source-studies/photon-recipes.json','recipe_id':r['id'],'scene_sha256':p['sources'][film]['canonical_scene_sha256']}})

m=read(ROOT/'skill-upgrade/mini-poke-recipes.json');mrecipes={motif:r for r in m['recipes'] for motif in r['motifs']}
mmap={'poke.identity_circle_to_app':['identity-morph'],'mini.rich_card_arrival':['mini-app-expand','selection-confirm'],'mini.sheet_depth':['mini-app-expand','app-drawer'],'mini.world_release':['card-orbit','camera-focus'],'poke.choice_to_message':['selection-confirm','conversation-handoff']}
msources={s['id']:s for s in m['sources']}
for r in m['motifs']:
    recipe=mrecipes[r['id']];film=r['scene']
    studies.append({'id':r['id'].replace('.','-'),'title':r['title'],'film':film,'starters':mmap[r['id']],
                    'intent':recipe['visual_intent'],'choose':prose(recipe['choose_when']),'avoid':prose(recipe['avoid_when']),
                    'anatomy':prose(recipe['hierarchy_back_to_front'])+' '+prose(recipe['camera_clip_states']),
                    'caveat':r['important_disclosure'],
                    'frames':[{'source':a['source_frame'],'output':a['preview_frame'],'label':a['label']} for a in r['recommended_frames']],
                    'range':r['range_inclusive'],'scene':msources[film]['canonical_scene'],'bindings':bindings(r['layers']),
                    'evidence':{'rich_study':'source-studies/mini-poke-recipes.json','motif_id':r['id'],'scene_sha256':msources[film]['canonical_sha256'],
                                'per_frame_morph_states':r.get('per_frame_morph_states'),'sound_hooks':recipe['sound_hooks']}})

l=read(ROOT/'skill-upgrade/linq-rene-recipes.json');lsources={s['id']:s for s in l['sources']}
lmap={'linq-chat-to-mini-app':['mini-app-expand','camera-focus'],'linq-native-control-and-amount':['selection-confirm'],'rene-message-to-action-cascade':['conversation-handoff','selection-confirm'],'rene-word-prop-message-bridge':['identity-morph','camera-focus']}
for r in l['recipes']:
    film={'linq':'05-linq','rene':'06-gallery'}[r['reference']];src=lsources[r['reference']]
    studies.append({'id':r['id'],'title':r['name'],'film':film,'starters':lmap[r['id']],
                    'intent':r['director_intent'],'choose':prose(r['choose_when']),'avoid':prose(r['avoid_when']),
                    'anatomy':prose(r['visual_anatomy']),'caveat':prose(r['failure_traps'])+' Editability: '+json.dumps(r['editability'],ensure_ascii=False),
                    'frames':[{'source':a['source_frame'],'output':a['output_frame'],'label':a['caption']} for a in r['recommended_stills']],
                    'range':r['study_window'],'scene':src['canonical_scene'],'bindings':bindings(r['property_keyframe_snippets']),
                    'evidence':{'rich_study':'source-studies/linq-rene-recipes.json','recipe_id':r['id'],'scene_sha256':src['sceneSHA256'],'sound_anchors':r['sound_anchors']}})

# Decode one set per actual movie, selected with integer n, never decimal -ss.
requests={}
for s in studies:
    assert len(s['frames'])==6,s['id']
    source=ROOT/'references'/s['film']/'source.mp4';render=ROOT/'outputs'/s['film']/'gsap.mp4'
    for frame in s['frames']:
        requests.setdefault(source,set()).add(frame['source']);requests.setdefault(render,set()).add(frame['output'])

def decode(item):
    movie,selected=item;indices=sorted(selected)
    filters="select='"+'+'.join(f'eq(n,{n})' for n in indices)+"',scale=320:180:force_original_aspect_ratio=decrease,pad=320:180:(ow-iw)/2:(oh-ih)/2:white"
    cmd=['ffmpeg','-v','error','-threads','1','-filter_threads','1','-i',str(movie),'-vf',filters,'-fps_mode','passthrough','-frames:v',str(len(indices)),'-pix_fmt','rgb24','-f','rawvideo','pipe:1']
    data=subprocess.check_output(cmd);size=320*180*3;assert len(data)==len(indices)*size,(movie,len(data),len(indices)*size)
    return movie,{n:data[i*size:(i+1)*size] for i,n in enumerate(indices)}
with ThreadPoolExecutor(max_workers=2) as pool:decoded=dict(pool.map(decode,requests.items()))

font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font=ImageFont.truetype(font_path,15);small=ImageFont.truetype(font_path,12);heading=ImageFont.truetype(font_path,23)
(D/'atlas').mkdir(exist_ok=True)
for s in studies:
    canvas=Image.new('RGB',(1920,566),'#f6f5f1');draw=ImageDraw.Draw(canvas)
    draw.text((20,12),s['title'],font=heading,fill='#1c252c');draw.text((20,45),'Top: supplied source  |  Bottom: accepted GSAP reconstruction  |  Native frame indices; downsampled teaching images',font=font,fill='#64717d')
    movie_paths=[ROOT/'references'/s['film']/'source.mp4',ROOT/'outputs'/s['film']/'gsap.mp4']
    receipts=[]
    for i,f in enumerate(s['frames']):
        receipt=dict(f)
        for row,(movie,key) in enumerate(zip(movie_paths,['source','output'])):
            raw=decoded[movie][f[key]];im=Image.frombytes('RGB',(320,180),raw);top=84+row*238
            canvas.paste(im,(i*320,top));draw.text((i*320+9,top+184),('SOURCE ' if row==0 else 'REBUILD ')+str(f[key])+' · '+f['label'][:28],font=small,fill='#1c252c')
            receipt[key+'_thumb_rgb_sha256']=hashlib.sha256(raw).hexdigest()
        receipts.append(receipt)
    out=D/'atlas'/f"{s['id']}.jpg";canvas.save(out,quality=90,subsampling=0,optimize=True)
    s['atlas']='atlas/'+out.name;s['alt']=f"Six phases of {s['title']}; supplied source above, accepted rebuild below, with native frame labels."
    s['atlas_sha256']=hashlib.sha256(out.read_bytes()).hexdigest();s['frames']=receipts

index={'notice':'Actual historical source/candidate native-pixel comparison, not newly rerendered scene states or a perfection score. Images in the atlas are separate selected downsampled teaching phases.','total_native_frames':0,'sources':[]}
for film,v in sources.items():
    scan_path=ROOT/v['sourceScan'];scan=read(scan_path);dest=D/'analysis'/film;dest.mkdir(parents=True,exist_ok=True)
    for name in ['scan.json','frames.csv']:shutil.copy2(scan_path.parent/name,dest/name)
    rows=list(csv.DictReader((dest/'frames.csv').open()));assert len(rows)==v['sourceFramesCompared']
    actual_source=ROOT/'references'/film/'source.mp4';actual_render=ROOT/'outputs'/film/'gsap.mp4'
    assert hashlib.sha256(actual_source.read_bytes()).hexdigest()==scan['referenceSHA256']
    assert hashlib.sha256(actual_render.read_bytes()).hexdigest()==scan['candidateSHA256']
    index['total_native_frames']+=len(rows)
    index['sources'].append({'id':film,'native_frames':len(rows),'scene':v['scene'],'scene_sha256':v['sceneSHA256'],
                            'source_movie_sha256':scan['referenceSHA256'],'accepted_movie_sha256':scan['candidateSHA256'],
                            'csv':film+'/frames.csv','csv_sha256':hashlib.sha256((dest/'frames.csv').read_bytes()).hexdigest(),
                            'scan':film+'/scan.json','mean_native_mae':scan['mean_native_mae'],'maximum_native_mae':scan['maximum_native_mae']})
assert index['total_native_frames']==7499
js(D/'analysis/index.json',index)
catalogue={'version':2,'study_count':len(studies),'native_teaching_pairs':sum(len(s['frames']) for s in studies),
           'evidence_kind':'measured source and accepted reconstruction; new starters are separate adaptations',
           'frame_convention':'Zero-based integer native frames. Rational clocks in source manifests; Rene output1049 maps to source1230. Atlas JPEGs are downsampled teaching images, not native-pixel validation.',
           'studies':studies}
js(D/'catalogue.json',catalogue)
js(ROOT/'skill-upgrade/catalogue-build.audit.json',{'studies':len(studies),'teaching_pairs':catalogue['native_teaching_pairs'],'native_frames':7499,'atlases':len(studies),'all_selected_frame_extractions_exact_count':True,'all_source_and_accepted_movie_hashes_match_scan_evidence':True,'atlas_bytes':sum(p.stat().st_size for p in (D/'atlas').glob('*.jpg'))})
print(json.dumps(read(ROOT/'skill-upgrade/catalogue-build.audit.json')))
