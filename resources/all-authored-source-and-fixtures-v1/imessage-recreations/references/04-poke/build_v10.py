"""Close independently diagnosed every-frame v9 transition peaks."""
from pathlib import Path
import copy,json
from v8_utils import at,track,amend
p=Path(__file__).parent;root=p.parent.parent;scene=json.loads((root/'outputs/04-poke/final-v9/scene.json').read_text());by={l['id']:l for l in scene['layers']};fps=scene['fps']
# Native heading registration supersedes ambiguous translucent-white/blue edges.
rows=json.loads((p/'measurements-v8/calendar-glyph-camera-v10.json').read_text())['measurements'];track(by['p0100'],'y',rows,'sheet_y');by['p0100']['start']=rows[0]['time']
for name in['p0100','p0068','p0066']:by[name]['end']=261/fps
by['p0109']['start']=261/fps
# Entry was measured but its legacy visibility gate hid the first four frames.
rows=json.loads((p/'measurements-v8/restaurant-entry-v10.json').read_text())['measurements'];visible=[r for r in rows if 'sheet_y'in r];by['p0255']['start']=visible[0]['time'];by['p0231']['start']=visible[0]['time'];track(by['p0255'],'y',visible,'sheet_y');track(by['p0231'],'opacity',rows,'scrim_opacity')
# Before-first-keyframe values hold in the schema: explicitly keep early UI sharp.
for name in['p0292','p0298','p0230','p0259','p0262','p0372','p0427']:
    by[name].setdefault('keyframes',{})['blur']=[dict(t=0,value=0),dict(t=709/fps,value=0),dict(t=710/fps,value=8,ease='hold'),dict(t=719/fps,value=2),dict(t=728/fps,value=0)]
for name in['p0292','p0298','p0372','p0427']:by[name]['start']=710/fps
# Measured native found/check/result motion on both sides of the710camera cut.
components=json.loads((p/'measurements-v8/components-v10.json').read_text())['measurements'];found=[];selected=[]
for r in components:
    if r['frame']>729:continue
    matches=[c for c in r['gray']if 400<c['width']<1100 and 40<c['height']<220 and c['bbox'][1]>150]
    if matches:
        c=max(matches,key=lambda c:c['area']);b=c['bbox'];s=c['width']/945;found.append(dict(frame=r['frame'],time=r['time'],x=b[0],y=b[1],scaleX=s,scaleY=s))
    matches=[c for c in r['selected']if 300<c['width']<900 and 60<c['height']<260 and c['bbox'][1]>400]
    if matches:
        c=max(matches,key=lambda c:c['area']);b=c['bbox'];s=c['width']/768;selected.append(dict(time=r['time'],x=b[0],y=b[1],scaleX=s,scaleY=s))
for name,poses in [('p0230',found),('p0262',selected)]:
    for prop in['x','y','scaleX','scaleY']:track(by[name],prop,poses)
check=[dict(time=r['time'],x=r['x']+27*r['scaleX'],y=r['y']+198*r['scaleX'],scaleX=r['scaleX'],scaleY=r['scaleY'])for r in found]
for prop in['x','y','scaleX','scaleY']:track(by['p0259'],prop,check)
# Actual grid camera continues after40s; complete authentic tiles prevent late
# exposure of old partial edge fallbacks.
poses=json.loads((p/'measurements-v8/grid-held-camera-v10.json').read_text())['measurements'];assets=json.loads((p/'assets/grid-native-v8-provenance.json').read_text());held=[l for l in scene['layers']if l.get('start')==1169/fps and l.get('end')==1215/fps]
if len(held)!=24:raise ValueError('Expected24held service tiles')
for i,g in enumerate(held):
    gx,gy,sx,sy=[at(g,k,1169/fps)for k in['x','y','scaleX','scaleY']]
    if i%6 in[0,5]:g['children']=[dict(id='v10-held-art-'+str(i),type='image',src=assets[i]['asset'],x=0,y=0,width=225,height=225)]
    rows=[dict(time=r['time'],x=r['x']+gx*r['scale'],y=r['y']+gy*r['scale'],scaleX=sx*r['scale'],scaleY=sy*r['scale'])for r in poses]
    for prop in['x','y','scaleX','scaleY']:track(g,prop,rows)
# Measured late conversation camera leaves composer/keyboard/hardware fixed.
late=json.loads((p/'measurements-v8/late-phone-v10.json').read_text());reference=next(r for r in late['measurements']if r['frame']==840)
for name in['p0300','p0307','p0310']:
    g=by[name];gx,gy=at(g,'x',840/fps),at(g,'y',840/fps);rows=[dict(time=r['time'],x=gx+r['audio_x']-reference['audio_x'],y=gy+r['audio_y']-reference['audio_y'])for r in late['measurements']if 'audio_y'in r]
    for prop in['x','y']:track(g,prop,rows)
reply=late['reply'];by['p0362']['start']=853/fps;by['p0362']['keyframes']['opacity']=[dict(t=853/fps,value=1)];by['p0362']['keyframes']['x']=[dict(t=853/fps,value=253)]
# Low correlation during the material overlap854–856 still has one unique
# strong match near the monotonic entry path; retain those explicitly diagnosed
# partial-word estimates, not unrelated pre-entry maxima.
for r in late['reply_scores']:
    if 854<=r['frame']<=856:reply.append(dict(frame=r['frame'],time=r['frame']/fps,y=r['y'],score=r['score'],partial_material_overlap=True))
reply=sorted(reply,key=lambda r:r['time']);track(by['p0362'],'y',reply)
fade=[r for r in late['measurements']if r['frame']>=870]
for name in['native28-hardware','p0300','p0307','p0310','p0362','p0372','p0427']:
    track(by[name],'opacity',fade,'phone_opacity');by[name]['end']=29.6
# Per-group utility exit and connection entry, with clipped tops kept censored.
ledger=json.loads((p/'measurements-v8/feature-connect-v10.json').read_text())['records'];mapping={'older_feature_0':'p0448','image_search_generation':'p0454','web_search_browse':'p0460','connect_gmail':'p0468','connect_notion':'p0473','connect_todoist':'p0478','connect_all_tools':'p0482'};cal={}
for role,name in mapping.items():
    for r in ledger:
        matches=[v for v in r['candidate']if v['role']==role and not v['cropped_top']and not v['cropped_bottom']]
        if matches:
            c=matches[0];g=by[name];gx,gy,sx,sy=[at(g,k,r['time'])for k in['x','y','scaleX','scaleY']];cal[role]=dict(left=(c['bbox'][0]-gx)/sx,top=(c['bbox'][1]-gy)/sy,width=c['width']/sx,height=c['height']/sy);break
# Candidate role labels near the overlapping entry were heuristic; calibrate
# new connection rectangles at the unambiguous1129full-column state instead.
reference=next(r for r in ledger if r['frame']==1129)
for role,name in mapping.items():
    if not role.startswith('connect_'):continue
    g=by[name];gx,gy,sx,sy=[at(g,k,reference['time'])for k in['x','y','scaleX','scaleY']]
    candidates=[v for v in reference['candidate']if not v['cropped_top']and not v['cropped_bottom']and abs(v['bbox'][1]-gy)<12]
    if not candidates:raise ValueError('No unambiguous candidate rect '+role)
    c=min(candidates,key=lambda c:abs(c['bbox'][1]-gy));cal[role]=dict(left=(c['bbox'][0]-gx)/sx,top=(c['bbox'][1]-gy)/sy,width=c['width']/sx,height=c['height']/sy)
cal['older_feature_0']=cal['image_search_generation']
for role,name in mapping.items():
    g=by[name];c=cal[role];rows=[]
    for r in ledger:
        matches=[v for v in r['source']if v['role']==role]
        if not matches:continue
        v=matches[0];b=v['bbox'];w=v['width'];ratio=v.get('reference_height_width_ratio')or .217012
        top=v.get('estimated_true_top_y')
        if top is None:top=b[3]-w*ratio
        if v['cropped_bottom']and v['height']<80:
            sx=1;sy=1;x=72
        else:
            sx=w/c['width'];sy=(w*ratio)/c['height'];x=b[0]-c['left']*sx
        rows.append(dict(frame=r['frame'],time=r['time'],x=x,y=top-c['top']*sy,scaleX=sx,scaleY=sy))
    for prop in['x','y','scaleX','scaleY']:track(g,prop,rows)
    if role.startswith('connect_'):g['start']=rows[0]['time']
    else:
        # One final thin clipped strip falls below the ledger's area threshold.
        last,previous=rows[-1],rows[-2];extra=dict(last,frame=last['frame']+1,time=(last['frame']+1)/fps,y=last['y']+(last['y']-previous['y']))
        for prop in['x','y','scaleX','scaleY']:amend(g,prop,[dict(t=extra['time'],value=extra[prop])],extra['time'],extra['time'])
        g['end']=(last['frame']+2)/fps
# Spatial glyph ranking at original1129 selects the genuine TextMedium face.
scene['fonts'].append(dict(family='SF Pro Text',src='assets/SF-Pro-Text-Medium.v10.woff',weight=500))
for g in scene['layers']:
    for child in g.get('children',[]):
        if child['id']=='p0225':child['fontWeight']=400 # preserve prior explicit face
        if child['id']in['p0465','p0470','p0475']:child['fontWeight']=500
        if child['id']in['p0466','p0471','p0476']:child['fill']='#7e7d80'
from v10_early_chat import apply as early_apply
early_apply(scene,p)
from v10_final_components import apply as component_apply
component_apply(scene,p)
from v10_connect_fade import apply as fade_apply
fade_apply(scene,p)
from v10_logo_component import apply as logo_apply
logo_apply(scene,p)
scene['title']='Poke Apple Messages launch — native recreation v10 measured full timeline'
scene['source']['notes']+=' V10 native all-frame diagnosis: calendar heading registration and exact261cut; actual575restaurant entry; explicit zero blur before710phone cut; dense found/check/result motion; measured late conversation/reply and uniform phone fade; independent utility exit/connect-entry trajectories with censored bounds; complete genuine service tiles and dense late camera. No new source-frame layers.'
(p/'scene-v10-candidate.json').write_text(json.dumps(scene,indent=2,ensure_ascii=False));print('Built v10')
