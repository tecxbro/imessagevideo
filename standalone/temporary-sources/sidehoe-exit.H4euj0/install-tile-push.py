from pathlib import Path
import json
from sys import argv
root=Path(__file__).parent
original=root/'project/scene.json'
p=root/'tile-project/scene.json'
s=json.loads(original.read_text())
tile=json.loads((root/'tile-fit.json').read_text())
s['calendarTileProfiles']={}
for f,values in tile.items():
 detail,soft,dy,dh,smear=values
 row=next(row for row in s['tracks']['calendarTileTreatment'] if row[0]==int(f))
 row[1]+=dy
 row[-1]=round(row[-1]+dh,5)
 row[-2]=round(row[-2]*smear,4)
 s['calendarTileProfiles'][f]=[detail,soft]
data=json.loads((root/'next-focus-fit.json').read_text())
follow=s['threadRegistration']['follow']
for f,focus in data.items():
 if focus:
  follow[f]['focus']=focus
for i,(case_y,head_end,badge_y,status_y,utility,footer) in enumerate([
 (-26,141,93,41,(858,49),(962,(414,992,584,1000))),
 (-49,140,89,39,(876,51),(984,None)),
 (-74,138,83,37,(900,52),(1010,None)),
 (-111,149,82,35,(930,55),None),
 (-147,148,79,36,(959,59),None),
 (-188,147,77,36,(983,65),None),
]):
 f=660+i
 row=follow[str(f)]
 row['utilityRow']=utility
 if i<5:
  row['pushCamera']=[case_y,[head_end,status_y,badge_y]]
  if i<2:
   row['railSpan']=[[12,72,924,1000],[0,47,950,1000]][i]
 if footer:
  row['keyboardFooter']=footer
if len(argv)>1:
 for f in argv[1:]:
  follow[f] = json.loads(original.read_text())['threadRegistration']['follow'][f]
p.write_text(json.dumps(s,indent=2,ensure_ascii=False)+'\n')
