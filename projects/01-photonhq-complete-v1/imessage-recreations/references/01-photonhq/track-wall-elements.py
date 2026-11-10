from pathlib import Path
import json,pickle,numpy as np
R=Path('/workspace/imessage-recreations/references/01-photonhq');cache=R/'assets/wall-art/component-cache-local.pkl'
if cache.exists():
 data=pickle.loads(cache.read_bytes());comps=data['comps'];phases=data['phases']
else:
 source=(R/'rebuild-walls-overlap.py').read_text();prefix=source[:source.index('ledger=[];new=[];diagnostics={}')];env={};exec(compile(prefix,'local-component-helper','exec'),env);comps=env['comps'];phases=env['phases'];cache.write_bytes(pickle.dumps(dict(comps=comps,phases=phases),protocol=5))
scene=json.loads((R/'scene-wall-v4.json').read_text());rowgroups={l['id']:l for l in scene['layers'] if l['id'].startswith('wall-art-')};ledger=json.loads((R/'wall-art-provenance.json').read_text());new=[];diag={}
def sample(track,t):
 keys=sorted(track,key=lambda q:q['t'])
 if t<=keys[0]['t']:return keys[0]['value']
 for a,b in zip(keys,keys[1:]):
  if t<=b['t']:
   p=(t-a['t'])/(b['t']-a['t']) if b['t']!=a['t'] else 0;return a['value']+(b['value']-a['value'])*p
 return keys[-1]['value']
for ph in phases:
 name=ph['name'];base=ph['base'];rows=ledger['fitting'][name]['rows'];elements=[]
 for row in rows:
  g=rowgroups[f'wall-art-{name}-row{row["row"]}']
  for child in g['children']:
   box=(child['x'],child['y'],child['x']+child['width'],child['y']+child['height']);co=min(comps[base],key=lambda c:sum(abs(a-b) for a,b in zip(c['box'],box)));elements.append(dict(child=child,co=co,row=g,measurements=[]))
 for n in ph['frames']:
  t=n/30;pairs=[]
  for ei,e in enumerate(elements):
   co=e['co'];x0,y0,x1,y1=co['box'];g=e['row'];tr=g['keyframes'];sx=sample(tr['scaleX'],t);sy=sample(tr['scaleY'],t);px=sample(tr['x'],t)+(x0+x1)/2*sx;py=sample(tr['y'],t)+(y0+y1)/2*sy
   for ci,other in enumerate(comps[n]):
    ox0,oy0,ox1,oy1=other['box'];xr=other['w']/co['w'];yr=other['h']/co['h'];dx=(ox0+ox1)/2-px;dy=(oy0+oy1)/2-py
    if not(.55<xr<1.55 and .07<yr<1.6):continue
    if abs(dx)>280 or abs(dy)>150:continue
    if abs(co['h']-other['h'])>20 and (y0<4 or y1>1076):continue
    err=float(np.mean((co['finger']-other['finger'])**2));limit=.022 if yr<.82 else .009
    if err>limit:continue
    score=err+.00000002*(dx*dx+dy*dy)
    pairs.append((score,err,ei,ci,xr,yr))
  pairs.sort();used_e=set();used_c=set()
  for score,err,ei,ci,sx,sy in pairs:
   if ei in used_e or ci in used_c:continue
   used_e.add(ei);used_c.add(ci);other=comps[n][ci];elements[ei]['measurements'].append(dict(t=t,x=other['box'][0],y=other['box'][1],scaleX=sx,scaleY=sy,error=err))
 for ei,e in enumerate(elements):
  co=e['co'];child=e['child'];ms=e['measurements'];baseanchor=dict(t=base/30,x=child['x'],y=child['y'],scaleX=1,scaleY=1,error=0)
  ms=[m for m in ms if abs(m['t']-base/30)>.001]+[baseanchor];ms.sort(key=lambda m:m['t'])
  if len(ms)<3 or co['h']<20:
   # A clipped edge sliver cannot establish a reliable independent flip; retain measured row camera for that tiny asset.
   g=e['row'];tracks={};times=sorted(set(k['t'] for track in g['keyframes'].values() for k in track));fallback=[]
   for t in times:
    sx=sample(g['keyframes']['scaleX'],t);sy=sample(g['keyframes']['scaleY'],t);fallback.append(dict(t=t,x=sample(g['keyframes']['x'],t)+child['x']*sx,y=sample(g['keyframes']['y'],t)+child['y']*sy,scaleX=sx,scaleY=sy))
   ms=fallback;start=g['start'];end=g['end'];tracks={p:[dict(t=m['t'],value=m[p]) for m in ms] for p in ['x','y','scaleX','scaleY']};tracks['opacity']=g['keyframes']['opacity'];tracks['blur']=g['keyframes']['blur'];fallback_used=True
  else:
   first,last=ms[0],ms[-1];start=max(ph['start'],first['t']-.065);end=min(ph['end'],last['t']+.065);tracks={p:[dict(t=m['t'],value=m[p]) for m in ms] for p in ['x','y','scaleX','scaleY']}
   # Stagger per-element flip entrances/exits rather than fading an entire row.
   for t,m in [(start,first),(end,last)]:
    new_sy=m['scaleY']*.08;new_y=m['y']+(m['scaleY']-new_sy)*child['height']/2
    tracks['x'].append(dict(t=t,value=m['x']));tracks['y'].append(dict(t=t,value=new_y));tracks['scaleX'].append(dict(t=t,value=m['scaleX']));tracks['scaleY'].append(dict(t=t,value=new_sy))
   for p in tracks:tracks[p].sort(key=lambda q:q['t'])
   tracks['opacity']=[dict(t=start,value=0),dict(t=first['t'],value=1),dict(t=last['t'],value=1),dict(t=end,value=0)];tracks['blur']=[dict(t=start,value=2),dict(t=first['t'],value=0),dict(t=last['t'],value=0),dict(t=end,value=2)];fallback_used=False
  node={**child,'id':child['id'].replace('art-','wall-element-'),'start':start,'end':end,'keyframes':tracks,'sourceFrame':base,'sourceBounds':list(co['box']),'editability':'Independently animated static original bubble/call artwork; copy is bitmap.'};new.append(node);diag[node['id']]=dict(phase=name,base_frame=base,measurements=ms,fallback_row_camera=fallback_used,start=start,end=end)
scene['layers']=new+[l for l in scene['layers'] if not l['id'].startswith('wall-art-')];scene['source']['notes']+=' Boundary revision tracks each bubble/card independently with nonuniform scaleY for measured flip entrances, per-element visibility and overlap; shared-row fades were rejected after source13.0 comparison.'
(R/'scene-wall-v4.json').write_text(json.dumps(scene,indent=2));(R/'wall-element-tracking.json').write_text(json.dumps(diag,indent=2));print('Independent wall element tracks',len(new),flush=True)
