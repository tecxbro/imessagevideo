from pathlib import Path
import importlib.util,json,copy,math
import numpy as np
from PIL import Image,ImageDraw
R=Path('/workspace/imessage-recreations');O=R/'outputs/alternative-methods/pillow-avatar-diagnosis/neutral';O.mkdir(exist_ok=True)
def module(name,file):
 sp=importlib.util.spec_from_file_location(name,R/file);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
old=module('old','engines/render_pillow.py');new=module('new','engines/render_pillow.conditioning-experiment.py')
im=Image.new('RGBA',(128,128));d=ImageDraw.Draw(im)
for color,box in [('#ff0000',(0,0,63,63)),('#00aa00',(64,0,127,63)),('#0000ff',(0,64,63,127)),('#ffcc00',(64,64,127,127))]:d.rectangle(box,fill=color)
im.save(O/'quadrants.png')
def scene(factor=1,rotation=0):
 c={'id':'unit-group','type':'group','x':32+10*(1-1/factor),'y':32+20*(1-1/factor),'scaleX':factor,'scaleY':factor,'rotation':rotation,'originX':10/factor,'originY':20/factor,'clip':{'x':0,'y':0,'width':256/factor,'height':256/factor,'radius':64/factor},'opacity':.75,'blur':.5/factor,'shadow':{'x':1.5/factor,'y':2.5/factor,'blur':3/factor,'color':'#00000066'},'children':[
 {'id':'field','type':'circle','x':38/factor,'y':38/factor,'width':180/factor,'height':180/factor,'fill':'#ee77aa','stroke':'#111111','strokeWidth':1/factor},
 {'id':'texture-wrapper','type':'group','x':0,'y':0,'scaleX':1/factor,'scaleY':1/factor,'children':[{'id':'photo','type':'image','src':str(O/'quadrants.png'),'x':64,'y':64,'width':128,'height':128}]},
 {'id':'glyph','type':'text','x':100/factor,'y':24/factor,'fontSize':16/factor,'fontFamily':'DejaVu Sans','text':'Aa','fill':'#111111'},
 {'id':'triangle','type':'path','d':f'M{100/factor},{220/factor}L{128/factor},{196/factor}L{156/factor},{220/factor}Z','fill':'#0099ff'}]}
 return {'width':340,'height':340,'fps':1,'duration':2,'background':'#ffffff','layers':[c]}
rows=[]
for rotation in [0,20]:
 reference=scene(1,rotation)
 # Compensate source x/y so origin10/factor,20/factor has the same world pivot42,52 as referenceorigin10,20.
 source=scene(10000,rotation)
 expected=old.render(reference,0,str(O),1);actual=new.render(source,0,str(O),1);bad=old.render(source,0,str(O),1)
 for name,im in [('reference',expected),('conditioned',actual),('old',bad)]:im.save(O/f'{rotation}-{name}.png')
 a=np.asarray(expected,dtype=np.int16);b=np.asarray(actual,dtype=np.int16);c=np.asarray(bad,dtype=np.int16)
 rows.append({'rotation':rotation,'oldMae':float(abs(a-c).mean()),'newMae':float(abs(a-b).mean()),'newMax':int(abs(a-b).max())})
 assert int(abs(a-b).max())<=2,rows[-1]
# Same world pose under two different unit systems, same-process cache reuse.
a=new.render(scene(10000),0,str(O),1);b=new.render(scene(20000),0,str(O),1)
x=np.asarray(a,dtype=np.int16);y=np.asarray(b,dtype=np.int16);assert int(abs(x-y).max())<=2
report={'physicalReferenceTests':rows,'cameraUnitChangeSameProcessMax':int(abs(x-y).max()),'components':'native circle/stroke, original neutral bitmap, native text/path, rounded clip, local Gaussian, shadow, group opacity, rotation and nonzero origins','productionUnchanged':True}
(O/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
