from pathlib import Path
from PIL import Image
import json
p=Path(__file__).parent;out=p/'assets/card-art';out.mkdir(exist_ok=True)
# Individual original mini-app artworks. They include bitmap internal UI copy.
# Frames, footers, labels and camera/translation tracks remain editable native layers.
specs=[('Love2night',31,(0,0,308,135),'bottom'),('Apartment in New York',31,(382,0,770,104),'bottom'),('DoorDash Order',31.8,(679,0,1020,178),'bottom'),('Starbucks Pickup',31,(1308,0,1688,60),'bottom'),('Mail',31,(1756,0,1920,29),'partial-right'),('Check-In',31.8,(25,500,345,678),'full'),('Marriott Stay',31,(329,249,714,455),'full'),('Zoom Meeting',31,(789,220,1184,429),'full'),('OpenTable Reservation',31,(1258,197,1642,405),'full'),('Wolf Inn Hotel',31.8,(1500,65,1825,244),'full'),('Weekend Plan',31.8,(96,777,420,951),'full'),('Jump Jump',31,(277,603,660,808),'full'),('Spectrum mini Apps',31,(735,578,1129,788),'full'),('Coding Agent',31,(1206,552,1594,761),'full'),('Your spending in August',31.8,(1575,343,1897,520),'full'),('Figma',31.8,(900,844,1238,1020),'full'),('Blue Bottle order',31.8,(1277,730,1610,911),'full')]
rows=[]
for i,(label,t,box,mode)in enumerate(specs):
 source=Image.open(p/'measured'/f'{t:g}.png').convert('RGBA');im=source.crop(box);canvas=Image.new('RGBA',(390,206))
 if mode=='full':canvas=im.resize((390,206),Image.Resampling.LANCZOS)
 elif mode=='bottom':
  h=round(im.height*390/im.width);im=im.resize((390,h),Image.Resampling.LANCZOS);canvas.paste(im,(0,206-h))
 else:
  # Only a narrow left portion of the off-stage Mail card is visible at this source time.
  im=im.resize((164,29),Image.Resampling.LANCZOS);canvas.paste(im,(0,177))
 name=f'{i:02d}.png';canvas.save(out/name);rows.append({'label':label,'file':'assets/card-art/'+name,'source_time':t,'source_box':list(box),'mode':mode,'limitation':'Static mini-app artwork contains bitmap UI copy; native container, footer and animation remain separate.'})
(p/'card-art-provenance.json').write_text(json.dumps(rows,indent=2));print('saved',len(rows),'separate mini-app artwork crops')
