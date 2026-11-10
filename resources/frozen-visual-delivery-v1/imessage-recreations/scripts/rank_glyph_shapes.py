"""Rank real SF Pro glyph shapes at an explicitly measured native ink box."""
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageFont,ImageDraw

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--image',required=True,type=Path)
parser.add_argument('--text',required=True)
parser.add_argument('--box',required=True,help='Exclusive ink bounds x1,y1,x2,y2')
parser.add_argument('--background',required=True,type=float,help='Mean RGB of flat surrounding background')
parser.add_argument('--foreground',required=True,type=float,help='Mean RGB of solid glyph interiors')
parser.add_argument('--fonts-dir',type=Path,default=Path(__file__).parents[2]/'shared/fonts')
parser.add_argument('--out',required=True,type=Path)
args=parser.parse_args()
if args.out.exists():parser.error('Refusing to overwrite a measured report; choose a new revision name')
box=[int(x)for x in args.box.split(',')]
if len(box)!=4 or box[2]<=box[0] or box[3]<=box[1]:parser.error('Invalid exclusive ink box')
if args.background==args.foreground:parser.error('Background and foreground must differ')
ref=np.array(Image.open(args.image).convert('RGB').crop(box)).mean(2)
alpha=np.clip((ref-args.background)/(args.foreground-args.background),0,1)
rows=[]
for family in ['Text','Display']:
 for weight in ['Regular','Medium','Semibold','Bold']:
  file=args.fonts_dir/f'SF-Pro-{family}-{weight}.otf';font=ImageFont.truetype(str(file),176)
  im=Image.new('L',(max(4000,int(font.getlength(args.text))+32),400));ImageDraw.Draw(im).text((0,0),args.text,font=font,fill=255)
  im=im.crop(im.getbbox()).resize((ref.shape[1],ref.shape[0]),Image.Resampling.LANCZOS);candidate=np.array(im)/255
  rows.append({'family':family,'weight':weight,'mse_alpha':float(((alpha-candidate)**2).mean()),'mae_alpha':float(np.abs(alpha-candidate).mean()),'dark_pixels_at_175':int((candidate>175/255).sum())})
rows.sort(key=lambda x:x['mse_alpha']);report={'settings':{**vars(args),'image':str(args.image),'fonts_dir':str(args.fonts_dir),'out':str(args.out),'box':box},'method':'Render actual fonts at176px, crop to native glyph ink, normalize to reference ink width/height, compare alpha masks spatially. A diagnostic ranking only; validate selected family in actual browser renderer. Density alone is insufficient.','ranking':rows};args.out.write_text(json.dumps(report,indent=2));print(json.dumps(rows[:3],indent=2))
