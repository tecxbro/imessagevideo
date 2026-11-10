"""Measure the exposed native gray backsheet, independently of the foreground camera."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image
from measure_lunch_refinement_v16 import find
P=Path(__file__).resolve().parent
scene=json.loads((P/'final-v16.scene.json').read_text())
phone=next(n for n in scene['layers']if n['id']=='p03-86')

def crossing(rgb):
 profile=rgb[:150,950:970].mean((1,2))
 candidates=np.where((profile>30)&(profile<190))[0]
 if not len(candidates):
  raise ValueError('No observed center gray surface')
 first=int(candidates[0])
 plateau=float(np.median(profile[first+1:first+7]))
 threshold=plateau/2
 index=next(i for i in range(max(1,first-2),first+6)if profile[i]>=threshold and profile[i-1]<threshold)
 value=index-1+(threshold-profile[index-1])/(profile[index]-profile[index-1])
 return dict(crossing=float(value),plateau=plateau,threshold=threshold,profile=profile[max(0,index-3):index+6].tolist())
calibration_image=np.array(Image.open(P.parent.parent/'outputs/03-photon-mini/frames-gsap/000275.png').convert('RGB'))
calibration=crossing(calibration_image)
_,calibration_parent=find(phone,'p03-77',275)
calibration_geometry_top=calibration_parent[1,2]+164*calibration_parent[1,1]
calibration_offset=calibration['crossing']-calibration_geometry_top
rows=[]
for frame in range(230,310):
 source=np.array(Image.open(P/f'mail-edit-v17-source/{frame:04}.png').convert('RGB'))
 native=np.array(Image.open(P.parent.parent/f'outputs/03-photon-mini/frames-gsap/{frame:06}.png').convert('RGB'))
 actual=crossing(source)
 _,parent=find(phone,'p03-77',frame)
 geometry_top=float(parent[1,2]+164*parent[1,1])
 try:
  old=crossing(native)
 except StopIteration:
  old=dict(top_censored=True,geometry_top=geometry_top)
 y=(actual['crossing']-calibration_offset-parent[1,2])/parent[1,1]
 rows.append(dict(frame=frame,source=actual,candidate=old,native_parent_scaleY=float(parent[1,1]),corrected_logical_y=float(y),corrected_fill='#'+f'{int(round(actual["plateau"])):02x}'*3,calibrated_native_crossing_offset=float(calibration_offset)))
print([(r['frame'],round(r['source']['crossing'],3),round(r['candidate'].get('crossing',r['candidate'].get('geometry_top',0)),3),round(r['corrected_logical_y'],3))for r in rows if r['frame']in [230,240,258,275,293,309]])
(P/'mail-backsheet-v17-measurements.json').write_text(json.dumps(dict(scope=[230,309],frames=rows,notice='Exposed gray backsheet center top is directly observed, using its own halfplateau crossing to separate differing source/native fill. Frontpaper top alreadymatches; only backsheetY moves within230–309. Existing physical/UI/papercamera and310+special closeup remain untouched.'),indent=2))
