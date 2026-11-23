from pathlib import Path
import json, sys
import numpy as np
from PIL import Image, ImageDraw

work=Path(__file__).parent
ref=Path('/tmp/imv-goal.9G9Un0')
tile=Path('/tmp/imv-sidehoe-tile.q9Ocuh')
output=work/sys.argv[1]
baseline=ref/'sidehoe-glyph-final-frames'
targets = {
 'tile': (tile/'source',range(612,624),[612,614,616,618,619,620,621], (742,1110,1245,2000), .29),
 'cursor': (ref/'follow-native/source',range(672,698),[672,675,683,690,692,694,695],(845,965,1110,1250),.56),
 'rail': (ref/'follow-native/source',range(672,698),[675,683,689,692,694,695], (130,755,570,900), .65),
}
result={}
for prop,(directory,frames,sampled,rect,scale) in targets.items():
 x0,y0,x1,y1=rect
 w,h=round((x1-x0)*scale),round((y1-y0)*scale)
 sheet=Image.new('RGB',(w*len(sampled),3*(h+16)),'#1b2031')
 draw=ImageDraw.Draw(sheet)
 report=[]
 for frame in frames:
    if not (directory/f'{frame:06d}.png').exists(): continue
    source=Image.open(directory/f'{frame:06d}.png').convert('RGB').crop(rect)
    a,b=[Image.open(path/f'{frame:06d}.png').convert('RGB').resize((2000,2000),Image.Resampling.LANCZOS).crop(rect)
         for path in (baseline,output)]
    u,v,z=(np.asarray(i,dtype=np.int16) for i in (source,a,b))
    metrics=[float(np.abs(u-y).mean()) for y in (v,z)]
    report.append([frame,*metrics])
    if frame in sampled:
      col=sampled.index(frame)*w
      for row,(label,photo) in enumerate(zip(('source','baseline','candidate'),(source,a,b))):
         draw.text((col+2,row*(h+16)+1),f'{label} {frame}',fill='white')
         sheet.paste(photo.resize((w,h),Image.Resampling.LANCZOS),(col,row*(h+16)+16))
 sheet.save(work/f'{prop}-{output.name}.jpg',quality=92)
 result[prop]=report
 print(prop, 'average',np.asarray(report)[:,1:].mean(axis=0).round(3), 'regresses',[(f,round(a,2),round(b,2)) for f,a,b in report if b>a+.10])
(work/f'{output.name}-results.json').write_text(json.dumps(result,indent=2)+'\n')
