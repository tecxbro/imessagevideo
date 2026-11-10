from PIL import Image,ImageDraw
from pathlib import Path
import json,shutil
p=Path(__file__).parent;a=p/'assets';a.mkdir(exist_ok=True)
records=[]
def crop(t,box,name,mask=None):
 im=Image.open(p/'native'/f'{t:04.1f}.png').convert('RGBA').crop(box)
 if mask:
  m=Image.new('L',im.size,0);d=ImageDraw.Draw(m)
  if mask=='circle':d.ellipse((0,0,im.width-1,im.height-1),fill=255)
  else:d.rounded_rectangle((0,0,im.width-1,im.height-1),radius=mask,fill=255)
  im.putalpha(m)
 im.save(a/f'{name}.png');records.append({'asset':f'assets/{name}.png','referenceTime':t,'referenceCrop':box,'purpose':'Static authentic raster artwork; surrounding native text/layout excluded','mask':mask})
crop(0,(460,220,982,744),'poke-square',135)
crop(.5,(597,251,844,700),'poke-circle-original') # replace precise crop below
crop(.5,(597,251,844,700),'unused')
# circular textured icon crop has 247 px diameter; native screenshot exact y251..700? actual icon y251..700 observed image was 1440x1080; measure automated bounds below
crop(.5,(597,251,844,700),'unused2')
crop(.5,(192,398,466,672),'braden','circle')
crop(.5,(976,430,1250,704),'sydney','circle')
crop(2,(483,166,959,643),'poke-circle','circle')
crop(18,(604,274,1158,834),'location-map',40)
crop(25,(460,430,850,725),'zareen-map',30)
crop(20,(294,483,462,651),'ettan-photo',12)
crop(20,(294,738,462,905),'khazana-photo',12)
crop(21,(295,425,461,592),'zareen-photo',12)
crop(21,(295,680,461,847),'darbar-photo',12)
crop(23,(628,795,769,938),'zareen-card-photo',28)
for name,box in [('taco',(276,164,334,215)),('sushi',(275,269,334,319)),('pasta',(277,374,333,426)),('indian',(276,483,334,533)),('noodles',(276,588,336,640)),('dice',(277,697,335,749))]:crop(12,box,name)
crop(14,(882,346,936,399),'thumb')
# Feature tiles at native 31/33/35; retained brand artwork without feature text
crop(31,(1028,376,1180,528),'feature-mail',32)
crop(31,(1015,628,1160,774),'feature-calendar',32)
crop(31,(980,889,1110,1017),'feature-clock',28)
crop(35,(1005,216,1146,356),'feature-auto',32)
crop(35,(1037,456,1193,612),'feature-image',30)
crop(35,(1003,715,1142,854),'feature-search',30)
# exact standalone brand wordmark, distinct from application UI text
crop(41,(499,492,927,576),'poke-wordmark')
# Original app icon grid: each branded tile is a separate image asset, never a complete source frame.
xs=[-78,201,472,744,1015,1287];ys=[22,293,565,837];names=[['sonos','github','banana','asana','hex','strava'],['spiral','webflow','canva','todoist','oura','sonos'],['outlook','cursor','vercel','notion','gmail','spiral'],['netlify','linear','calendar','sonos','github','outlook']]
for row,y in enumerate(ys):
 for col,x in enumerate(xs):
  if x<0 or x+225>1440:continue
  name=names[row][col]
  if not (a/f'brand-{name}.png').exists():crop(39,(x,y,x+225,y+225),f'brand-{name}',54)
# gmail/notion/todoist source connection tile, service logos only
for name,box in [('gmail',(605,196,703,294)),('notion',(608,410,704,505)),('todoist',(605,625,703,723))]:crop(37,box,f'connect-{name}',24)
for f in ['SFProDisplay-Regular.woff2','SFProDisplay-Medium.woff2']:
 src=p.parent/'01-photonhq'/'assets'/f
 if src.exists() and src.read_bytes()[:4] == b'wOF2':shutil.copy2(src,a/f)
# remove temporary investigative wrong crops, only final assets referenced by scene
for name in ['unused','unused2','poke-circle-original']:
 (a/f'{name}.png').unlink(missing_ok=True)
records=[r for r in records if not any(x in r['asset'] for x in ['unused','original'])]
(a/'provenance.json').write_text(json.dumps(records,indent=2))
