#!/usr/bin/env python3
"""Normalize visually grounded UI events without deriving sounds from music."""
from pathlib import Path
from fractions import Fraction
import json,hashlib,collections
ROOT=Path(__file__).resolve().parents[2];CUES=ROOT/'audio-recreation/ui-cues'
SOURCES={'01-photonhq':'01-events.json','02-danieltian':'02-events.json','03-photon-mini':'03-photon-mini.events.json','04-poke':'04-poke.events.json','05-linq':'05-linq-ui-cues.json','06-gallery':'06-gallery-ui-cues.json'}
KINDS={'typing','typing_burst','delete','text_select','tap','message_send','message_arrival','panel_open','panel_close','control_appear','cart_update'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 records=[]
 for ident,name in SOURCES.items():
  p=CUES/name;source=json.loads(p.read_text());picture=json.loads((ROOT/'audio-recreation/mixes'/ident/'mix-report.json').read_text())['picture']
  frames=picture['frames'];n=picture['fps_numerator'];d=picture['fps_denominator']
  if source.get('frames',source.get('framecount'))!=frames:raise ValueError('Frame count mismatch '+ident)
  events=[];seen=set()
  for index,raw in enumerate(source['events']):
   e=dict(raw);frame=e.get('preview_frame',e['frame']);kind=e['kind'];assert isinstance(frame,int) and 0<=frame<frames and kind in KINDS
   assert frame==e['frame'],'Use preview scheduling frame explicitly'
   t=Fraction(frame*d,n)
   if abs(float(t)-float(e['time']))>1e-6:raise ValueError('Timebase mismatch '+ident)
   key=(frame,kind,str(e.get('group','')))
   if key in seen:raise ValueError('Duplicate event '+str(key))
   seen.add(key);e.update(frame=frame,time=float(t),sample_offset_48000=round(t*48000),event_id=e.get('id',f'{ident}:{kind}:{frame}:{index}'))
   events.append(e)
  events.sort(key=lambda e:(e['frame'],e['kind'],e.get('group','')))
  scene=source.get('canonical_scene',source.get('scene'));scene_path=scene if isinstance(scene,str) else scene['path'];scene_sha=source.get('canonical_scene_sha256') if isinstance(scene,str) else scene['sha256']
  if sha(ROOT/scene_path)!=scene_sha:raise ValueError('Scene changed '+ident)
  result={'schema':'message-motion-ui-events/1','id':ident,'fps_numerator':n,'fps_denominator':d,'fps':n/d,'frames':frames,'sample_count':picture['sample_count'],'duration':picture['rendered_duration_s'],'scheduling_picture':'accepted GSAP reconstruction; zero-based native frame','canonical_scene':scene_path,'canonical_scene_sha256':scene_sha,'source_cues':name,'source_cues_sha256':sha(p),'music_transients_used_as_timing':False,'reference_audio_samples_used':False,'hardware_keypress_timing_claimed':False,'one_key_per_visible_batch':True,'optional_inferred_events_rendered':False,'events':events,'counts':dict(collections.Counter(e['kind'] for e in events)),'exclusions':source.get('exclusions',source.get('excluded_visuals',[]))}
  out=CUES/('canonical-'+ident+'.json');out.write_text(json.dumps(result,indent=2)+'\n');records.append({'id':ident,'file':str(out.relative_to(ROOT)),'sha256':sha(out),'events':len(events),'counts':result['counts']})
 # Specific observed anchors prevent regression to beat-driven or decorative typing.
 byid={i['id']:json.loads((ROOT/i['file']).read_text()) for i in records}
 assert [(e['kind'],e['frame']) for e in byid['01-photonhq']['events']]==[('tap',70)]
 typ02=[e['frame'] for e in byid['02-danieltian']['events'] if e['kind'] in ['typing','typing_burst']]
 assert len(typ02)==32 and min(typ02)==105 and max(typ02)==159 and not any(128<=f<=142 for f in typ02)
 assert [e['frame'] for e in byid['05-linq']['events'] if e['kind']=='typing']==[23,25,30,31,34,39,40,43,45,48,50,54,56,59,61,64,69,70,73,75,78,80,83]
 assert not any(e['kind'] in ['typing','typing_burst','delete'] for e in byid['06-gallery']['events'])
 (CUES/'canonical-manifest.json').write_text(json.dumps({'status':'pass','total':sum(r['events'] for r in records),'records':records,'policy':'Use actual visible UI actions; no music-beat timing, title/AI typing, invented backspaces, or inferred optional gestures.'},indent=2)+'\n')
 print(json.dumps({'status':'pass','total_events':sum(r['events'] for r in records),'films':records},indent=2))
if __name__=='__main__':main()
