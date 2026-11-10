from pathlib import Path
import json,numpy as np
R=Path('/workspace/imessage-recreations/references/01-photonhq');p=R/'wall-art-provenance.json';d=json.loads(p.read_text());scene=json.loads((R/'scene-wall-v4.json').read_text());groups={l['id']:l for l in scene['layers']};changes=[]
phases={'sms':(8.2,9.5),'calls':(10.666667,11.666667),'imessage':(11.666667,12.966667),'whatsapp':(12.966667,14.2),'telegram':(14.2,15.5)}
for name,ph in d['fitting'].items():
 base=ph['base_frame']/30;rows=ph['rows'];st,en=phases[name]
 raw={r['row']:[m for m in r['measurements'] if abs(m['t']-base)<.001 or m.get('matches',0)>0 and m.get('error',1)<.005] for r in rows}
 for r in rows:
  cleaned=[]
  for m in raw[r['row']]:
   peers=[q for lst in raw.values() for q in lst if abs(q['t']-m['t'])<.001]
   med=np.median([q['scale'] for q in peers]) if peers else 1
   medx=np.median([q['x'] for q in peers]) if peers else 0
   if abs(m['t']-base)<.001 or abs(m['scale']-med)<.025 and abs(m['x']-medx)<100:cleaned.append(m)
   else:changes.append(dict(phase=name,row=r['row'],rejected=m,reason='scale/translation contradicts other rows at same source timestamp'))
  if not any(abs(m['t']-base)<.001 for m in cleaned):cleaned.append(dict(t=base,scale=1,x=0,y=0,matches=0,error=0))
  cleaned.sort(key=lambda m:m['t']);raw[r['row']]=cleaned
 for r in rows:
  ms=raw[r['row']]
  # At unsupported early moments, copy the nearest reliable camera trend while preserving the row's measured vertical differential.
  donor=max(rows,key=lambda q:len(raw[q['row']]))
  donor_ms=raw[donor['row']]
  for dm in donor_ms:
   if any(abs(m['t']-dm['t'])<.001 for m in ms):continue
   if len(ms)>1:
    anchor=min((m for m in ms if abs(m['t']-base)>.001),key=lambda m:abs(m['t']-base))
    da=min(donor_ms,key=lambda m:abs(m['t']-anchor['t']))
    denom=da['scale']-1
    f=(dm['scale']-1)/denom if abs(denom)>.003 else 0
    row=dict(t=dm['t'],scale=dm['scale'],x=dm['x']+f*(anchor['x']-da['x']),y=dm['y']+f*(anchor['y']-da['y']),matches=0,error=None,inferred_from_row=donor['row'])
   else:row={**dm,'matches':0,'inferred_from_row':donor['row']}
   ms.append(row)
  ms.sort(key=lambda m:m['t'])
  def extend(t,left):
   a,b=(ms[:2] if left else ms[-2:]);f=(t-a['t'])/(b['t']-a['t']) if b['t']!=a['t'] else 0
   return dict(t=t,**{v:a[v]+f*(b[v]-a[v]) for v in ['scale','x','y']},matches=0,error=None,extrapolated=True)
  if ms[0]['t']>st+.001:ms.insert(0,extend(st,True))
  if ms[-1]['t']<en-.001:ms.append(extend(en,False))
  r['refined_measurements']=ms
  g=groups[f'wall-art-{name}-row{r["row"]}'];g['keyframes']={k:[dict(t=m['t'],value=m[v],ease='linear') for m in ms] for k,v in [('x','x'),('y','y'),('scaleX','scale'),('scaleY','scale')]}
d['refinement']={'reason':'Loose visual-fingerprint threshold matched neighboring same-colored bubbles near transitions. Require MSE<.005, compare scale/translation across rows, preserve an exact base anchor, explicitly label inferred/extrapolated camera samples.','rejected':changes}
p.write_text(json.dumps(d,indent=2));(R/'scene-wall-v4.json').write_text(json.dumps(scene,indent=2));print('Refined wall camera fits; rejected cross-row outliers',len(changes))
