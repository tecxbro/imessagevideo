from pathlib import Path
import json,copy
p=Path(__file__).parent
samples=[(17.3,638),(17.6,594),(18,542),(18.5,462),(19,380),(19.5,302),(20,228),(20.3,188),(20.5,164)]
for original,out in [('final-v3.scene.json','candidate-geometry-v4.scene.json'),('candidate-v4.scene.json','candidate-geometry-art-v4.scene.json')]:
 scene=json.loads((p/original).read_text())
 camera=next(layer for layer in scene['layers'] if layer['id']=='p03-204')
 for prop in ['x','y','scaleX','scaleY']:
  prior=[key for key in camera['keyframes'][prop] if key['t'] <= 16.5]
  tail=[key for key in camera['keyframes'][prop] if key['t'] > 21.1]
  if prop=='y':
   middle=[{'t':time,'value':top-697*1.02,'ease':'linear'} for time,top in samples]
   middle.append({'t':21.1,'value':80,'ease':'easeInOut'})
  elif prop=='x':
   middle=[{'t':time,'value':552,'ease':'linear'} for time,top in samples]
   middle.append({'t':21.1,'value':610,'ease':'easeInOut'})
  else:
   middle=[{'t':time,'value':1.02,'ease':'linear'} for time,top in samples]
   middle.append({'t':21.1,'value':.875,'ease':'easeInOut'})
  camera['keyframes'][prop]=prior+middle+tail
 scene['source']['notes']+=' Measured lunch camera correction from blue-bubble native pixel anchors17.3–20.5s; changes only16.5<t<21.1. Source16.5andmenu21.5camera unaffected.'
 (p/out).write_text(json.dumps(scene,indent=2))
print('geometry candidates generated; frozenv3 untouched')
