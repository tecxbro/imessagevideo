from pathlib import Path
import importlib.util,json,gc
import numpy as np
from PIL import Image
R=Path('/workspace/imessage-recreations');rows=[]
for i,(ref,rev,f)in enumerate([('01-photonhq','final-v10',260),('02-danieltian','final-v13',441),('04-poke','final-v19',212),('05-linq','final-v13',259),('06-gallery','final-v23',614)]):
 sp=importlib.util.spec_from_file_location('conditioned'+str(i),R/'engines/render_pillow.conditioning-experiment.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 source=R/'outputs'/ref/rev/'scene.json';s=json.loads(source.read_text());m.register_fonts(s,str(source.parent));image=m.render(s,f/s['fps'],str(source.parent),1)
 old=np.asarray(Image.open(R/f'outputs/{ref}/cache/pillow/{f:06}.png').convert('RGB'),dtype=np.int16);new=np.asarray(image,dtype=np.int16);row={'reference':ref,'revision':rev,'frame':f,'mae':float(abs(old-new).mean()),'max':int(abs(old-new).max())};rows.append(row);print(json.dumps(row),flush=True);assert row['max']==0
 del m,s,image,old,new;gc.collect()
(R/'outputs/alternative-methods/pillow-avatar-diagnosis/unaffected-controls.json').write_text(json.dumps(rows,indent=2)+'\n')
