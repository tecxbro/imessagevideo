#!/usr/bin/env python3
"""Measured geometry renderer. Pillow rasterizes geometry; FFmpeg encodes frames.
SVG paths are rasterized by optional CairoSVG. Text rasterization differs from Chromium.
"""
import argparse,base64,io,json,math,os,subprocess,tempfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageColor
import numpy as np
from functools import lru_cache

def easing(p,name='linear'):
 if name=='hold':return float(p>=1)
 if name=='easeIn':return p**3
 if name=='easeOut':return 1-(1-p)**3
 if name=='easeInOut':return 4*p**3 if p<.5 else 1-(-2*p+2)**3/2
 if name.startswith('cubic-bezier('):
  x1,y1,x2,y2=map(float,name[13:-1].split(','));lo=0;hi=1
  def cb(a,b,t):return 3*(1-t)**2*t*a+3*(1-t)*t*t*b+t**3
  for _ in range(24):
   m=(lo+hi)/2
   if cb(x1,x2,m)<p:lo=m
   else:hi=m
  return cb(y1,y2,(lo+hi)/2)
 return p

def mix(a,b,p):
 if isinstance(a,(int,float)) and isinstance(b,(int,float)):return a+(b-a)*p
 if isinstance(a,str) and isinstance(b,str) and len(a)==len(b)==7 and a[0]==b[0]=='#':
  return '#'+''.join(f'{round(int(a[i:i+2],16)+(int(b[i:i+2],16)-int(a[i:i+2],16))*p):02x}' for i in (1,3,5))
 return b if p>=1 else a

def track(keys,t):
 keys=sorted(keys,key=lambda k:k['t'])
 if t<=keys[0]['t']:return keys[0]['value']
 for a,b in zip(keys,keys[1:]):
  if t<=b['t']:return mix(a['value'],b['value'],easing((t-a['t'])/(b['t']-a['t']),b.get('ease','linear')))
 return keys[-1]['value']

def state(layer,t):
 s=dict(x=0,y=0,opacity=1,rotation=0,scaleX=1,scaleY=1,originX=0,originY=0);s.update(layer)
 for prop,keys in s.get('keyframes',{}).items():s[prop]=track(keys,t)
 return s

def matrix(s):
 a=math.radians(s['rotation']);c=math.cos(a);sn=math.sin(a);sx=s['scaleX'];sy=s['scaleY'];ox=s['originX'];oy=s['originY']
 return np.array([[c*sx,-sn*sy,s['x']+ox-c*sx*ox+sn*sy*oy],[sn*sx,c*sy,s['y']+oy-sn*sx*ox-c*sy*oy],[0,0,1.]])

@lru_cache(100)
def font_path(family,weight):
 first=family.split(',')[0].strip("'\""); pattern=first+(':style=Bold' if str(weight) in ('bold','700','800','900') else '')
 return subprocess.check_output(['fc-match','-f','%{file}',pattern],text=True)

@lru_cache(200)
def get_font(family,size,weight):return ImageFont.truetype(font_path(family,str(weight)),int(round(size)))

@lru_cache(100)
def load_image(src,base):
 if src.startswith('data:'):return Image.open(io.BytesIO(base64.b64decode(src.split(',',1)[1]))).convert('RGBA')
 if src.startswith(('http://','https://')):raise ValueError('Download image assets first; remote URLs are not reproducible')
 return Image.open(Path(base)/src).convert('RGBA')

def rgba(value):return ImageColor.getcolor(value,'RGBA') if value not in (None,'none','transparent') else (0,0,0,0)

def render(scene,t,base,aa=2):
 W,H=scene['width'],scene['height'];w,h=W*aa,H*aa;canvas=Image.new('RGBA',(w,h),rgba(scene.get('background','#ffffff')))
 def draw_layer(layer,parent=np.eye(3),parent_alpha=1):
  s=state(layer,t)
  if t<s.get('start',0) or t>=s.get('end',scene['duration']):return
  M=parent@matrix(s);alpha=parent_alpha*s['opacity'];typ=s['type']
  if typ=='group':
   for ch in s.get('children',[]):draw_layer(ch,M,alpha)
   return
  width=s.get('width',s.get('radius',0)*2);height=s.get('height',width)
  pad=math.ceil((s.get('blur',0)*3+s.get('strokeWidth',0)+3)*aa)
  x=lambda v:round(v*aa)
  fill=rgba(s.get('fill','#000000'));stroke=rgba(s.get('stroke'));sw=max(1,x(s.get('strokeWidth',0))) if stroke[3] else 0
  minx=miny=0;maxx=x(width);maxy=x(height)
  if typ=='text':
   f=get_font(s.get('fontFamily','Arial, sans-serif'),s.get('fontSize',32)*aa,s.get('fontWeight',400));lineheight=s.get('lineHeight',s.get('fontSize',32)*1.2);anchor={'start':'la','middle':'ma','end':'ra'}[s.get('textAnchor','start')]
   scratch=ImageDraw.Draw(Image.new('L',(1,1)));bounds=[scratch.textbbox((0,x(i*lineheight)),line,font=f,anchor=anchor,stroke_width=sw) for i,line in enumerate(str(s.get('text','')).split('\n'))]
   minx=min(v[0] for v in bounds);miny=min(v[1] for v in bounds);maxx=max(v[2] for v in bounds);maxy=max(v[3] for v in bounds)
  if typ=='path':minx,miny,maxx,maxy=-w,-h,w*2,h*2
  ox,oy=pad-minx,pad-miny
  local=Image.new('RGBA',(max(1,maxx-minx+2*pad+1),max(1,maxy-miny+2*pad+1)));d=ImageDraw.Draw(local)
  box=(ox,oy,ox+x(width),oy+x(height))
  if typ=='rect':d.rounded_rectangle(box,radius=x(s.get('radius',0)),fill=fill,outline=stroke,width=sw)
  elif typ=='circle':d.ellipse(box,fill=fill,outline=stroke,width=sw)
  elif typ=='text':
   f=get_font(s.get('fontFamily','Arial, sans-serif'),s.get('fontSize',32)*aa,s.get('fontWeight',400));lineheight=s.get('lineHeight',s.get('fontSize',32)*1.2);anchor={'start':'la','middle':'ma','end':'ra'}[s.get('textAnchor','start')]
   for i,line in enumerate(str(s.get('text','')).split('\n')):d.text((ox,oy+x(i*lineheight)),line,font=f,fill=fill,anchor=anchor,stroke_width=sw if sw else 0,stroke_fill=stroke)
  elif typ=='image':
   im=load_image(s['src'],base).resize((max(1,x(width)),max(1,x(height))),Image.Resampling.LANCZOS);local.alpha_composite(im,(ox,oy))
  elif typ=='path':
   try:import cairosvg
   except ImportError:raise RuntimeError('SVG path layers require engines/.venv/bin/python (CairoSVG installed there)')
   from xml.sax.saxutils import escape
   svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{local.width/aa}" height="{local.height/aa}" viewBox="{-ox/aa} {-oy/aa} {local.width/aa} {local.height/aa}"><path d="{escape(s["d"])}" fill="{s.get("fill","#000000")}" stroke="{s.get("stroke","none")}" stroke-width="{s.get("strokeWidth",0)}"/></svg>'
   local=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(),output_width=local.width,output_height=local.height))).convert('RGBA')
  else:raise ValueError(f'Unsupported layer type: {typ}')
  if s.get('clip'):
   clip=s['clip'];mask=Image.new('L',local.size);md=ImageDraw.Draw(mask);cx=ox+x(clip.get('x',0));cy=oy+x(clip.get('y',0));md.rounded_rectangle((cx,cy,cx+x(clip['width']),cy+x(clip['height'])),radius=x(clip.get('radius',0)),fill=255);local.putalpha(Image.fromarray((np.asarray(local.getchannel('A'),dtype=np.float32)*np.asarray(mask)/255).astype('uint8')))
  if s.get('blur'):local=local.filter(ImageFilter.GaussianBlur(s['blur']*aa))
  if alpha!=1:local.putalpha(local.getchannel('A').point(lambda p:round(p*max(0,min(1,alpha)))))
  # output pixels -> source padded local pixels (Pillow affine inverse).
  A=np.diag([aa,aa,1.])@M@np.diag([1/aa,1/aa,1.]);A=A@np.array([[1,0,-ox],[0,1,-oy],[0,0,1.]])
  if abs(np.linalg.det(A))<1e-12:return
  inv=np.linalg.inv(A);out=local.transform((w,h),Image.Transform.AFFINE,tuple(inv[:2].ravel()),resample=Image.Resampling.BICUBIC);canvas.alpha_composite(out)
 for layer in scene['layers']:draw_layer(layer)
 return canvas.convert('RGB').resize((W,H),Image.Resampling.LANCZOS)

def main():
 p=argparse.ArgumentParser();p.add_argument('--scene',required=True);p.add_argument('--out',required=True);p.add_argument('--frame',type=int);p.add_argument('--aa',type=int,default=1);a=p.parse_args();f=Path(a.scene).resolve();scene=json.loads(f.read_text());out=Path(a.out).resolve();out.parent.mkdir(parents=True,exist_ok=True)
 if scene.get('fonts'):raise ValueError('Pillow requires custom fonts registered with fontconfig; root fonts declarations are browser-only. Install the exact font before rendering.')
 def validate(layers):
  for layer in layers:
   if layer.get('shadow') or layer.get('textDecoration','none')!='none' or str(layer.get('fill','')).startswith('url('):raise ValueError('Pillow shadow/textDecoration/gradient adapter unsupported; use a browser engine')
   if layer.get('letterSpacing',0):raise ValueError('Pillow letterSpacing unsupported; use a browser engine or implement measured glyph placement')
   if layer['type']=='group' and (layer.get('clip') or layer.get('blur')):raise ValueError('Pillow group clip/blur unsupported; use a browser engine')
   validate(layer.get('children',[]))
 validate(scene['layers'])
 if a.frame is not None:render(scene,a.frame/scene['fps'],str(f.parent),a.aa).save(out);return
 proc=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{scene["width"]}x{scene["height"]}','-framerate',str(scene['fps']),'-i','-','-c:v','libx264','-vf','scale=out_color_matrix=bt709','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-color_range','tv','-crf','16','-pix_fmt','yuv444p' if scene['width']%2 or scene['height']%2 else 'yuv420p','-movflags','+faststart',str(out)],stdin=subprocess.PIPE)
 for frame in range(round(scene['fps']*scene['duration'])):proc.stdin.write(render(scene,frame/scene['fps'],str(f.parent),a.aa).tobytes())
 proc.stdin.close();code=proc.wait()
 if code:raise RuntimeError(f'FFmpeg failed: {code}')
 out.with_suffix(out.suffix+'.render.json').write_text(json.dumps(dict(method='pillow',scene=str(f),out=str(out),width=scene['width'],height=scene['height'],fps=scene['fps'],frames=round(scene['fps']*scene['duration']),duration=round(scene['fps']*scene['duration'])/scene['fps'],source=scene.get('source'),antialias=a.aa),indent=2)+'\n')
 print(json.dumps(dict(method='pillow',out=str(out),width=scene['width'],height=scene['height'],fps=scene['fps'],frames=round(scene['fps']*scene['duration']))))
if __name__=='__main__':main()
