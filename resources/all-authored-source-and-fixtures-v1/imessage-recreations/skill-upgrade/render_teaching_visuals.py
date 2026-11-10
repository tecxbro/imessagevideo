from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import cairosvg,io
root=Path(__file__).resolve().parents[1];d=root/'skill/imessage-motion-recreation/director';folders=sorted((root/'skill-upgrade/starter-frames').iterdir())
canvas=Image.new('RGB',(1440,len(folders)*186),'#f6f5f1');draw=ImageDraw.Draw(canvas);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
for row,folder in enumerate(folders):
 for col,frame in enumerate([0,24,48,72,96,119]):
  png=cairosvg.svg2png(url=str(folder/(str(frame)+'.svg')),output_width=240,output_height=135)
  canvas.paste(Image.open(io.BytesIO(png)).convert('RGB'),(col*240,row*186+22));draw.text((col*240+7,row*186+160),'f'+str(frame),font=font,fill='#64717d')
 draw.text((7,row*186+3),folder.name+' / NEW STARTER',font=font,fill='#1c252c')
canvas.save(d/'visuals/starter-overview.jpg',quality=90,subsampling=0,optimize=True)
cairosvg.svg2png(url=str(d/'visuals/component-anatomy.svg'),write_to=str(d/'visuals/component-anatomy.png'))
print('Analytical SVG raster previews rendered (not browser screenshots).')
