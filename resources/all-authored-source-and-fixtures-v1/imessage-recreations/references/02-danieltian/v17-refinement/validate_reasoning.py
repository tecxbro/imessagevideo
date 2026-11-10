from pathlib import Path
from PIL import Image,ImageDraw
import json,numpy as np,argparse
R=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--directory',default='reasoning-native');parser.add_argument('--frames',default='271,272,275,280,293,300,320,350,360,361,363,364,367,370,374,375');parser.add_argument('--name',default='reasoning-native');args=parser.parse_args()
frames=list(map(int,args.frames.split(',')));D=R/args.directory
rows=[];contacts=[]
for i,f in enumerate(frames):
 source=Image.open(R/'reasoning-source'/f'source-{f:04d}.png').convert('RGB');before=Image.open(R/'reasoning-baseline'/f'{f:06d}.png').convert('RGB');after=Image.open(D/f'{f/30:.3f}.png').convert('RGB')
 a,b,c=[np.asarray(x).astype('int16')for x in[source,before,after]]
 rows.append({'frame':f,'before':float(abs(a-b).mean()),'after':float(abs(a-c).mean()),'oldVsNewMax':int(abs(b-c).max())})
 if f in[271,272,275,280,293,300,320,350,360,361,363,364,367,370,374,375]:
  panel=Image.new('RGB',(1440,290),'white');draw=ImageDraw.Draw(panel)
  for col,im in enumerate([source,before,after]):
   im=im.resize((480,270));panel.paste(im,(480*col,20));draw.text((480*col,0),str(f)+' '+['source','before16','after+house'][col],fill='black')
  contacts.append(panel)
for k in range(0,len(contacts),4):
 page=Image.new('RGB',(1440,290*len(contacts[k:k+4])),'white')
 for j,im in enumerate(contacts[k:k+4]):page.paste(im,(0,290*j))
 page.save(R/(args.name+f'-contact-{k//4+1}.jpg'))
changed=[q for q in rows if 272<=q['frame']<=374]
report={'rows':rows,'meanBefore':float(np.mean([q['before']for q in changed])),'meanAfter':float(np.mean([q['after']for q in changed])),'regressions':[q for q in changed if q['after']>q['before']],'controlsExact':all(q['oldVsNewMax']==0 for q in rows if q['frame']in[271,375])}
(R/(args.name+'-metrics.json')).write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
