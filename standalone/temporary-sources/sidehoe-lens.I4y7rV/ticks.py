from pathlib import Path
import json,numpy as np
from PIL import Image
p=Path(__file__).parent
s=json.loads((p/'project/scene.json').read_text())
for k in ('calendarGridRegistration','calendarCamera','calendarRight','calendarArrivalOpacity','calendarArrivalSmear'):
 print(k,[row for row in s['tracks'][k] if 396<=row[0]<=410])
for f in range(397,413):
 print(f,end=' ')
 for root in ('/tmp/sidehoe-hyperframes.wG3QA2/source-stage','/tmp/sidehoe-thread-audit.oxTJaL/frames'):
  a=np.asarray(Image.open(Path(root)/f'{f:06}.png').convert('L'),float)
  out=[]
  for lo,hi in [(115,142),(142,166),(166,188),(188,194)]:
   tile=np.clip(253-a[660:1000,lo:hi],0,255)
   out.append(f'{tile.mean():.2f}:{tile.max():.0f}')
  print('/'.join(out),end=' ')
 print()
