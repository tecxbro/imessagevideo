"""Apply measured staggered entry while preserving the verified held-grid render."""
from pathlib import Path
import copy,json
def apply(scene,directory):
 p=Path(directory);fit=json.loads((p/'measurements-v8/grid-pose-fit.json').read_text());assets=json.loads((p/'assets/grid-native-v8-provenance.json').read_text());grid=[g for g in scene['layers']if g.get('start')==37.8 and g.get('end')==40.6];fps=30000/1001;join=1169/fps;cut=fit['cut_time'];entry=[]
 if len(grid)!=24:raise ValueError('Expected24editable service-icon groups')
 rows=[r for r in fit['measurements']if r['frame']<1169]
 for i,held in enumerate(grid):
  group={'id':'v8-entry-'+held['id'],'type':'group','start':rows[0]['time'],'end':join,'children':[{'id':'v8-entry-art-'+str(i),'type':'image','src':assets[i]['asset'],'x':0,'y':0,'width':225,'height':225}],'keyframes':{}}
  for prop in ['x','y','scaleX','scaleY','opacity']:group['keyframes'][prop]=[{'t':r['time'],'value':r['tiles'][i][prop],'ease':'linear'}for r in rows]
  entry.append(group);held['start']=join;held['end']=cut
 scene['layers'][scene['layers'].index(grid[0]):scene['layers'].index(grid[0])]=entry
 outro=next(l for l in scene['layers']if l.get('src','').endswith('poke-wordmark.png'));outro['start']=cut
 scene['source']['notes']+=' V8 measured grid entrance:24independent native sprite x/y/scale/opacity tracks at each source frame; alternating row stagger was missing in v7. The verified39/40held native scene is preserved after1169. Source hardcut to authentic wordmark is frame1215(40.5405s).'
 return {'grid_entry_frames':[rows[0]['frame'],1168],'grid_cut_frame':fit['cut_frame'],'preserved_held_interval':[1169,fit['cut_frame']-1]}

if __name__=='__main__':
 p=Path(__file__).parent;s=json.loads((p/'scene-v7-fonts.json').read_text());report=apply(s,p);(p/'scene-v8-grid-candidate.json').write_text(json.dumps(s,indent=2));print(report)
