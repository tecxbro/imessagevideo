#!/usr/bin/env python3
"""Native Pillow layer renderer with deterministic transforms and FFmpeg output.
Custom fonts are local sfnt/WOFF2 assets; SVG path geometry is drawn by CairoSVG.
"""
import argparse,base64,io,json,math,re,subprocess,hashlib,os
from pathlib import Path
from functools import lru_cache
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageColor,ImageChops
import numpy as np
FONT_REGISTRY={}
LEAF_CACHE={}
GROUP_CACHE={}
FAST_CACHE={}

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
 if isinstance(a,str) and isinstance(b,str) and len(a)==len(b)==7 and a[0]==b[0]=='#':return '#'+''.join(f'{round(int(a[i:i+2],16)+(int(b[i:i+2],16)-int(a[i:i+2],16))*p):02x}' for i in (1,3,5))
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

def rgba(value):
 if value in (None,'none','transparent'):return (0,0,0,0)
 m=re.fullmatch(r'rgba?\(([^)]+)\)',str(value))
 if m:
  a=[float(v.strip()) for v in m[1].split(',')];return tuple(round(v) for v in a[:3])+(round(a[3]*255) if len(a)>3 else 255,)
 return ImageColor.getcolor(value,'RGBA')

def register_fonts(scene,base):
 for f in scene.get('fonts',[]):
  src=f['src'];raw=base64.b64decode(src.split(',',1)[1]) if src.startswith('data:') else (Path(base)/src).read_bytes()
  if raw[:4] in (b'wOF2',b'wOFF'):
   from fontTools.ttLib import TTFont
   font=TTFont(io.BytesIO(raw));font.flavor=None;stream=io.BytesIO();font.save(stream);raw=stream.getvalue()
  if raw[:4] not in (b'OTTO',b'\x00\x01\x00\x00',b'ttcf'):raise ValueError('Font asset is not a valid sfnt: '+src[:100])
  FONT_REGISTRY[(f['family'].lower(),str(f.get('weight',400)))]=raw
 get_font.cache_clear()

@lru_cache(100)
def font_path(family,weight):
 first=family.split(',')[0].strip("'\"");style='Bold' if str(weight) in ('bold','700','800','900') else 'Semibold' if str(weight)=='600' else 'Medium' if str(weight)=='500' else 'Regular'
 return subprocess.check_output(['fc-match','-f','%{file}',first+':style='+style],text=True)

@lru_cache(200)
def get_font(family,size,weight):
 first=family.split(',')[0].strip("'\"").lower();requested=int({'normal':400,'bold':700}.get(str(weight),weight));weights=sorted(int(w) for f,w in FONT_REGISTRY if f==first)
 # CSS Fonts weight fallback: 400..500 searches toward 500 first; heavier
 # weights search upward before lighter ones. This matters for authored650.
 if 400<=requested<=500:order=[w for w in weights if requested<=w<=500]+[w for w in reversed(weights) if w<requested]+[w for w in weights if w>500]
 elif requested<400:order=[w for w in reversed(weights) if w<=requested]+[w for w in weights if w>requested]
 else:order=[w for w in weights if w>=requested]+[w for w in reversed(weights) if w<requested]
 registered=FONT_REGISTRY[(first,str(order[0]))] if order else None
 return ImageFont.truetype(io.BytesIO(registered) if registered else font_path(family,str(weight)),max(1,int(round(size))))

@lru_cache(100)
def load_image(src,base):
 if src.startswith('data:'):raw=base64.b64decode(src.split(',',1)[1])
 elif src.startswith(('http://','https://')):raise ValueError('Download image assets first; remote URLs are not reproducible')
 else:raw=(Path(base)/src).read_bytes()
 if raw.lstrip().startswith(b'<svg') or b'<svg' in raw[:300]:
  import cairosvg
  raw=cairosvg.svg2png(bytestring=raw)
 return Image.open(io.BytesIO(raw)).convert('RGBA')


@lru_cache(300)
def emoji_bitmap(text,size):
 path='/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
 font=ImageFont.truetype(path,109);advance=font.getlength(text);im=Image.new('RGBA',(max(1,math.ceil(advance)),128));ImageDraw.Draw(im).text((0,0),text,font=font,anchor='la',embedded_color=True);scale=size/109
 return im.resize((max(1,round(im.width*scale)),max(1,round(im.height*scale))),Image.Resampling.LANCZOS),advance*scale,size*.025

def emoji_clusters(text):
 clusters=[]
 for ch in text:
  code=ord(ch)
  if clusters and (code in (0xfe0f,0xfe0e,0x200d) or 0x1f3fb<=code<=0x1f3ff or clusters[-1].endswith('\u200d')):clusters[-1]+=ch
  else:clusters.append(ch)
 return clusters

def text_runs(text,font,size,tracking):
 clusters=emoji_clusters(text);runs=[]
 for i,cluster in enumerate(clusters):
  isemoji=any(ord(c)>=0x1f000 or ord(c) in (0x2705,0x274c,0x2764) for c in cluster) or '\ufe0f' in cluster
  if isemoji:
   bitmap,width,dy=emoji_bitmap(cluster,size);runs.append(dict(text=cluster,emoji=bitmap,width=width,dy=dy))
  elif runs and runs[-1].get('emoji') is None:runs[-1]['text']+=cluster
  else:runs.append(dict(text=cluster,emoji=None))
 for run in runs:
  if run['emoji'] is None:run['width']=font.getlength(run['text'])+max(0,len(run['text'])-1)*tracking
 for run in runs[:-1]:run['width']+=tracking
 return runs

def pc(value,size,default=0):return default if value is None else float(value[:-1])*size/100 if isinstance(value,str) and value.endswith('%') else float(value)

def paint(mask,fill,bounds,gradients):
 if not str(fill).startswith('url('):
  out=Image.new('RGBA',mask.size,rgba(fill));out.putalpha(ImageChops.multiply(mask,out.getchannel('A')));return out
 gid=re.fullmatch(r'url\(#([^)]*)\)',fill).group(1);g=next((v for v in gradients if v['id']==gid),None)
 if not g:raise ValueError('Unknown gradient '+gid)
 # Object-bounding-box coordinates; bounds are in mask pixels.
 x0,y0,x1,y1=bounds;w=max(1,x1-x0);h=max(1,y1-y0);yy,xx=np.mgrid[:mask.height,:mask.width];xx=xx-x0;yy=yy-y0
 if g.get('type')=='radial':p=np.hypot(xx-pc(g.get('cx'),w,w/2),yy-pc(g.get('cy'),h,h/2))/max(1e-8,pc(g.get('r'),math.hypot(w,h)/math.sqrt(2),math.hypot(w,h)/math.sqrt(2)/2))
 else:
  ax=pc(g.get('x1'),w);ay=pc(g.get('y1'),h);bx=pc(g.get('x2'),w);by=pc(g.get('y2'),h,h);dx=bx-ax;dy=by-ay;p=((xx-ax)*dx+(yy-ay)*dy)/max(1e-8,dx*dx+dy*dy)
 stops=sorted(g['stops'],key=lambda s:pc(s['offset'],1));offsets=[pc(s['offset'],1) for s in stops];colors=[rgba(s['color'])[:3]+(round(rgba(s['color'])[3]*s.get('opacity',1)),) for s in stops];arr=np.stack([np.interp(np.clip(p,0,1),offsets,[c[i] for c in colors]) for i in range(4)],axis=2).astype('uint8');arr[:,:,3]=(arr[:,:,3].astype(np.float32)*np.asarray(mask)/255).astype('uint8');return Image.fromarray(arr)

def transformed_bounds(im,x0,y0,M,aa):
 x1=x0+im.width/aa;y1=y0+im.height/aa;p=M@np.array([[x0,x1,x1,x0],[y0,y0,y1,y1],[1,1,1,1]])
 return (math.floor(p[0].min()*aa)/aa,math.floor(p[1].min()*aa)/aa,math.ceil(p[0].max()*aa)/aa,math.ceil(p[1].max()*aa)/aa)

def composite(target,target_x,target_y,im,x0,y0,M,aa):
 if abs(np.linalg.det(M))<1e-12:return
 tx=(M[0,2]+x0-target_x)*aa;ty=(M[1,2]+y0-target_y)*aa
 if M[0,0]==1 and M[0,1]==0 and M[1,0]==0 and M[1,1]==1 and abs(tx-round(tx))<1e-7 and abs(ty-round(ty))<1e-7:
  key=id(im)
  if key not in FAST_CACHE or FAST_CACHE[key][0] is not im:
   if len(FAST_CACHE)>=256:FAST_CACHE.pop(next(iter(FAST_CACHE)))
   FAST_CACHE[key]=(im,im.convert('RGBa').convert('RGBA'))
  target.alpha_composite(FAST_CACHE[key][1],(round(tx),round(ty)));return
 bx0,by0,bx1,by1=transformed_bounds(im,x0,y0,M,aa);left=max(0,round((bx0-target_x)*aa));top=max(0,round((by0-target_y)*aa));right=min(target.width,round((bx1-target_x)*aa));bottom=min(target.height,round((by1-target_y)*aa))
 if right<=left or bottom<=top:return
 # Destination crop pixels -> source image pixels.
 dest_to_units=np.array([[1/aa,0,target_x+left/aa],[0,1/aa,target_y+top/aa],[0,0,1.]])
 units_to_src=np.array([[aa,0,-x0*aa],[0,aa,-y0*aa],[0,0,1.]])
 inv=units_to_src@np.linalg.inv(M)@dest_to_units;piece=im.transform((right-left,bottom-top),Image.Transform.AFFINE,tuple(inv[:2].ravel()),resample=Image.Resampling.BICUBIC);target.alpha_composite(piece,(left,top))

def effects(im,x0,y0,s,aa):
 if s.get('clip'):
  c=s['clip'];mask=Image.new('L',im.size);d=ImageDraw.Draw(mask);x=(c.get('x',0)-x0)*aa;y=(c.get('y',0)-y0)*aa;d.rounded_rectangle((round(x),round(y),round(x+c['width']*aa),round(y+c['height']*aa)),radius=round(c.get('radius',0)*aa),fill=255);im.putalpha(ImageChops.multiply(im.getchannel('A'),mask))
 blur=s.get('blur',0);shadow=s.get('shadow');pad=math.ceil(blur*3*aa)
 if shadow:pad=max(pad,math.ceil((shadow.get('blur',0)*3+abs(shadow.get('x',0))+abs(shadow.get('y',0)))*aa))
 if pad:
  padded=Image.new('RGBA',(im.width+pad*2,im.height+pad*2));padded.alpha_composite(im,(pad,pad));im=padded;x0-=pad/aa;y0-=pad/aa
 if shadow:
  color=rgba(shadow.get('color','#000000'));alpha=im.getchannel('A').filter(ImageFilter.GaussianBlur(shadow.get('blur',0)*aa));alpha=alpha.point(lambda p:round(p*color[3]/255));shade=Image.new('RGBA',im.size,color);shade.putalpha(alpha);background=Image.new('RGBA',im.size);background.alpha_composite(shade,(round(shadow.get('x',0)*aa),round(shadow.get('y',0)*aa)));background.alpha_composite(im);im=background
 if blur:im=im.convert('RGBa').filter(ImageFilter.GaussianBlur(blur*aa)).convert('RGBA')
 alpha=max(0,min(1,s.get('opacity',1)))
 if alpha!=1:im.putalpha(im.getchannel('A').point(lambda p:round(p*alpha)))
 return im,x0,y0

def condition_group_units(layers,t,duration):
 """Rebase bounded, highly magnified clipped group coordinates before rasterizing.
 Opposing parent/child scales must not collapse an intermediate photo group to1px.
 The source tree stays untouched; unchanged branches retain their original objects.
 """
 def visit(layer,parent_gain=1.):
  if layer['type']!='group' and parent_gain==1:return layer
  v=state(layer,t)
  if t<v.get('start',0) or t>=v.get('end',duration) or v['opacity']<=0:return layer
  magnitude=max(abs(v['scaleX']*parent_gain),abs(v['scaleY']*parent_gain))
  gain=magnitude if v['type']=='group' and v.get('clip') and magnitude>=128 else 1.
  children=[visit(c,gain)for c in layer.get('children',[])]
  if parent_gain==1 and gain==1:
   if all(a is b for a,b in zip(children,layer.get('children',[]))):return layer
   result=dict(layer);result['children']=children;return result
  result=dict(v);result.pop('keyframes',None)
  # Uniform coordinate rebasing commutes with rotation, but not translation.
  # Absorb both original origins into the exact affine translation first.
  m=matrix(v)
  result.update(x=float(m[0,2]*parent_gain),y=float(m[1,2]*parent_gain),originX=0,originY=0,
                scaleX=v['scaleX']*parent_gain/gain,scaleY=v['scaleY']*parent_gain/gain)
  if 'children'in layer:result['children']=children
  if gain!=1:
   result['clip']={k:(value*gain if k in ('x','y','width','height','radius')else value)for k,value in v['clip'].items()}
   if v.get('blur'):result['blur']=v['blur']*gain
   if v.get('shadow'):result['shadow']={k:(value*gain if k in ('x','y','blur')else value)for k,value in v['shadow'].items()}
  return result
 return [visit(layer)for layer in layers]

def transform_only_group(s):
 return s['type']=='group' and s['opacity']==1 and not any(s.get(k)for k in ('clip','blur','shadow'))

def magnified_group_with_reduced_children(layer,t,duration):
 s=state(layer,t)
 if not transform_only_group(s) or max(abs(s['scaleX']),abs(s['scaleY']))<4:return False
 for child in layer.get('children',[]):
  c=state(child,t)
  if t<c.get('start',0)or t>=c.get('end',duration)or c['opacity']<=0:continue
  if min(abs(c['scaleX']),abs(c['scaleY']))<1:return True
 return False

def render(scene,t,base,aa=1):
 gradients=scene.get('gradients',[])
 def fragments(layer,M,force=False):
  v=state(layer,t)
  if t<v.get('start',0)or t>=v.get('end',scene['duration'])or v['opacity']<=0:return []
  if transform_only_group(v)and(force or magnified_group_with_reduced_children(layer,t,scene['duration'])):
   result=[]
   for child in layer.get('children',[]):result.extend(fragments(child,M@matrix(state(child,t)),True))
   return result
  r=raster(layer)
  return [(r,M)]if r is not None else []
 def resolved(layer,outer=False):
  s=state(layer,t)
  if t<s.get('start',0) or t>=s.get('end',scene['duration']) or s['opacity']<=0:return None
  excluded={'id','keyframes','start','end','children'}
  if outer:excluded.update(('x','y','rotation','scaleX','scaleY','originX','originY'))
  result={k:v for k,v in s.items() if k not in excluded}
  if s['type']=='group':result['children']=[v for child in s.get('children',[]) if (v:=resolved(child)) is not None]
  return result
 def raster(layer):
  s=state(layer,t)
  if t<s.get('start',0) or t>=s.get('end',scene['duration']) or s['opacity']<=0:return None
  typ=s['type']
  cachekey=None
  if typ!='group':
   cachekey=json.dumps([base,aa,gradients,{k:v for k,v in s.items() if k not in ('id','x','y','rotation','scaleX','scaleY','originX','originY','keyframes','start','end')}],sort_keys=True)
   if cachekey in LEAF_CACHE:return LEAF_CACHE[cachekey]
  if typ=='group':
   cachekey=json.dumps([base,aa,gradients,resolved(layer,True)],sort_keys=True)
   if cachekey in GROUP_CACHE:return GROUP_CACHE[cachekey]
   children=[]
   for c in s.get('children',[]):children.extend(fragments(c,matrix(state(c,t))))
   if not children:return None
   boxes=[transformed_bounds(*r,M,aa) for r,M in children];x0=min(b[0] for b in boxes);y0=min(b[1] for b in boxes);x1=max(b[2] for b in boxes);y1=max(b[3] for b in boxes)
   if s.get('clip'):
    c=s['clip'];x0=max(x0,c.get('x',0));y0=max(y0,c.get('y',0));x1=min(x1,c.get('x',0)+c['width']);y1=min(y1,c.get('y',0)+c['height'])
   if x1<=x0 or y1<=y0:return None
   im=Image.new('RGBA',(max(1,math.ceil((x1-x0)*aa)),max(1,math.ceil((y1-y0)*aa))))
   for (child,cx,cy),M in children:composite(im,x0,y0,child,cx,cy,M,aa)
  else:
   width=s.get('width',s.get('radius',0)*2);height=s.get('height',width);sw=s.get('strokeWidth',0);pad=max(2,math.ceil(sw*aa));x0=-pad/aa;y0=-pad/aa;x1=width+pad/aa;y1=height+pad/aa
   font=None;lines=[];colored=[];tracking=s.get('letterSpacing',0)*aa
   if typ=='text':
    font=get_font(s.get('fontFamily','Arial, sans-serif'),s.get('fontSize',32)*aa,str(s.get('fontWeight',400)));lh=s.get('lineHeight',s.get('fontSize',32)*1.2)*aa;scratch=ImageDraw.Draw(Image.new('L',(1,1)))
    for i,line in enumerate(str(s.get('text','')).split('\n')):
     runs=text_runs(line,font,s.get('fontSize',32)*aa,tracking);hasemoji=any(r['emoji'] is not None for r in runs);length=sum(r['width'] for r in runs) if hasemoji else scratch.textlength(line,font=font)+max(0,len(line)-1)*tracking;anchor=s.get('textAnchor','start');lx=-length/2 if anchor=='middle' else -length if anchor=='end' else 0;box=scratch.textbbox((lx,i*lh),line,font=font,anchor='la',stroke_width=round(sw*aa))
     if hasemoji:
      bounds=[];rx=lx
      for run in runs:
       if run['emoji'] is not None:
        eb=run['emoji'].getbbox() or (0,0,1,1);bounds.append((rx+eb[0],i*lh+run['dy']+eb[1],rx+eb[2],i*lh+run['dy']+eb[3]))
       else:bounds.append(scratch.textbbox((rx,i*lh),run['text'],font=font,anchor='la',stroke_width=round(sw*aa)))
       rx+=run['width']
      if bounds:box=(min(b[0] for b in bounds),min(b[1] for b in bounds),max(b[2] for b in bounds),max(b[3] for b in bounds))
     lines.append((line,lx,i*lh,length,box,runs if hasemoji else None))
    x0=(min(v[4][0] for v in lines)-pad)/aa;y0=(min(v[4][1] for v in lines)-pad)/aa;x1=(max(max(v[4][2],v[1]+v[3]) for v in lines)+pad)/aa;y1=(max(v[4][3] for v in lines)+pad)/aa
    if s.get('textDecoration')=='underline':y1=max(y1,(len(lines)-1)*lh/aa+s.get('fontSize',32)+max(1,s.get('fontSize',32)/20)+pad/aa)
   if typ=='path':
    from fontTools.pens.boundsPen import BoundsPen
    from fontTools.svgLib.path import parse_path
    pen=BoundsPen(None);parse_path(s['d'],pen);bounds=pen.bounds or (0,0,1,1);x0=bounds[0]-pad/aa;y0=bounds[1]-pad/aa;x1=bounds[2]+pad/aa;y1=bounds[3]+pad/aa
   im=Image.new('RGBA',(max(1,math.ceil((x1-x0)*aa)),max(1,math.ceil((y1-y0)*aa))));mask=Image.new('L',im.size);d=ImageDraw.Draw(mask);ox=-x0*aa;oy=-y0*aa;box=(round(ox),round(oy),round(ox+width*aa),round(oy+height*aa));fill=s.get('fill','#000000')
   if typ=='rect':d.rounded_rectangle(box,radius=round(s.get('radius',0)*aa),fill=255)
   elif typ=='circle':d.ellipse(box,fill=255)
   elif typ=='text':
    for line,lx,ly,length,b,runs in lines:
     if runs:
      cursor=0
      for run in runs:
       if run['emoji'] is not None:colored.append((run['emoji'],round(ox+lx+cursor),round(oy+ly+run['dy'])))
       elif tracking:
        cx=0
        for ch in run['text']:d.text((ox+lx+cursor+cx,oy+ly),ch,font=font,anchor='la',fill=255);cx+=d.textlength(ch,font=font)+tracking
       else:d.text((ox+lx+cursor,oy+ly),run['text'],font=font,anchor='la',fill=255)
       cursor+=run['width']
     elif tracking:
      cursor=0
      for j,ch in enumerate(line):d.text((ox+lx+cursor,oy+ly),ch,font=font,anchor='la',fill=255);cursor+=d.textlength(ch,font=font)+tracking
     else:d.text((ox+lx,oy+ly),line,font=font,anchor='la',fill=255)
     if s.get('textDecoration')=='underline':d.line((ox+lx,oy+ly+s.get('fontSize',32)*aa,ox+lx+length,oy+ly+s.get('fontSize',32)*aa),fill=255,width=max(1,round(s.get('fontSize',32)*aa/20)))
   elif typ=='image':im.alpha_composite(load_image(s['src'],base).resize((max(1,round(width*aa)),max(1,round(height*aa))),Image.Resampling.LANCZOS),(round(ox),round(oy)))
   elif typ=='path':
    import cairosvg
    from xml.sax.saxutils import escape
    defs=[]
    for g in gradients:
     tag='radialGradient' if g.get('type')=='radial' else 'linearGradient';attrs=' '.join(f'{k}="{escape(str(v))}"' for k,v in g.items() if k not in ('type','stops'));stops=''.join(f'<stop offset="{st["offset"]}" stop-color="{st["color"]}" stop-opacity="{st.get("opacity",1)}"/>' for st in g['stops']);defs.append(f'<{tag} {attrs}>{stops}</{tag}>')
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{im.width/aa}" height="{im.height/aa}" viewBox="{x0} {y0} {im.width/aa} {im.height/aa}"><defs>{"".join(defs)}</defs><path d="{escape(s["d"])}" fill="{fill}" stroke="{s.get("stroke","none")}" stroke-width="{sw}"/></svg>';im=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(),output_width=im.width,output_height=im.height))).convert('RGBA');bbox=im.getbbox()
    if bbox:im=im.crop(bbox);x0+=bbox[0]/aa;y0+=bbox[1]/aa
   else:raise ValueError('Unsupported layer type '+typ)
   if typ not in ('image','path'):
    bbox=mask.getbbox() or (0,0,1,1);im=paint(mask,fill,bbox,gradients)
    for bitmap,cx,cy in colored:im.alpha_composite(bitmap,(cx,cy))
    if sw and s.get('stroke'):
     sd=ImageDraw.Draw(im);stroke=rgba(s['stroke']);px=max(1,round(sw*aa))
     if typ=='rect':sd.rounded_rectangle(box,radius=round(s.get('radius',0)*aa),outline=stroke,width=px)
     elif typ=='circle':sd.ellipse(box,outline=stroke,width=px)
     elif typ=='text':
      for line,lx,ly,_,_,_ in lines:sd.text((ox+lx,oy+ly),line,font=font,anchor='la',fill=(0,0,0,0),stroke_fill=stroke,stroke_width=px)
  result=effects(im,x0,y0,s,aa)
  if cachekey is not None:
   cache=GROUP_CACHE if typ=='group' else LEAF_CACHE;limit=64 if typ=='group' else 256
   if len(cache)>=limit:cache.pop(next(iter(cache)))
   cache[cachekey]=result
  return result
 W,H=scene['width'],scene['height'];canvas=Image.new('RGBA',(W*aa,H*aa),rgba(scene.get('background','#ffffff')))
 for layer in condition_group_units(scene['layers'],t,scene['duration']):
  for r,M in fragments(layer,matrix(state(layer,t))):composite(canvas,0,0,*r,M,aa)
 return canvas.convert('RGB').resize((W,H),Image.Resampling.LANCZOS)

def frame_signature(scene,t):
 def walk(layer):
  s=state(layer,t)
  if t<s.get('start',0) or t>=s.get('end',scene['duration']) or s['opacity']<=0:return None
  result={k:v for k,v in s.items() if k not in ('id','keyframes','start','end','children')}
  if s['type']=='group':result['children']=[v for c in s.get('children',[]) if (v:=walk(c)) is not None]
  return result
 return json.dumps([v for l in scene['layers'] if (v:=walk(l)) is not None],sort_keys=True)

def atomic_png(image,path):
 temporary=path.with_name(path.name+f'.tmp-{os.getpid()}');image.save(temporary,format='PNG',compress_level=1);temporary.replace(path)

def parse_ranges(value,first,last,count):
 ranges=[list(map(int,r.split(':'))) for r in value.split(',')] if value else [[first,last]]
 if any(len(r)!=2 or r[0]<0 or r[1]<r[0] or r[1]>=count for r in ranges):raise ValueError('Invalid inclusive frame range')
 return ranges,sorted({f for first,last in ranges for f in range(first,last+1)})

def main():
 engine_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
 p=argparse.ArgumentParser();p.add_argument('--scene',required=True);p.add_argument('--out',required=True);p.add_argument('--frame',type=int);p.add_argument('--aa',type=int,default=1);p.add_argument('--frames-dir');p.add_argument('--ranges');p.add_argument('--start-frame',type=int,default=0);p.add_argument('--end-frame',type=int);p.add_argument('--encode-only',nargs='?',const='true',default='false');a=p.parse_args();f=Path(a.scene).resolve();scene=json.loads(f.read_text());out=Path(a.out).resolve();out.parent.mkdir(parents=True,exist_ok=True);register_fonts(scene,str(f.parent));count=round(scene['fps']*scene['duration']);ranges,frames=parse_ranges(a.ranges,a.start_frame,a.end_frame if a.end_frame is not None else count-1,count);directory=Path(a.frames_dir).resolve() if a.frames_dir else None;encode_only=str(a.encode_only).lower() in ('true','1');unique=0
 if a.aa<1:raise ValueError('Antialias scale must be positive')
 if a.frame is not None:
  if not 0<=a.frame<count:raise ValueError('Invalid frame index')
  atomic_png(render(scene,a.frame/scene['fps'],str(f.parent),a.aa),out);return
 if (len(frames)!=count or encode_only) and directory is None:raise ValueError('Partial/encode-only rendering requires --frames-dir containing retained native PNGs')
 if directory:directory.mkdir(parents=True,exist_ok=True)
 if directory and (len(frames)!=count or encode_only):
  metadata=directory/'native-cache.json'
  if metadata.exists():
   old=json.loads(metadata.read_text())
   if old['width']!=scene['width'] or old['height']!=scene['height'] or old['frames']!=count or abs(old['fps']-scene['fps'])>1e-8:raise ValueError('Native cache dimensions/cadence/frame count mismatch')
  selected=set(frames);missing=[frame for frame in range(count) if (encode_only or frame not in selected) and not (directory/f'{frame:06d}.png').exists()]
  if missing:raise ValueError(f'Missing unchanged cached frame {missing[0]}')
 encoding=out.with_name(out.stem+f'.encoding-{os.getpid()}.mp4');common=['-c:v','libx264','-threads','2','-filter_threads','1','-vf','scale=out_color_matrix=bt709','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-color_range','tv','-crf','16','-pix_fmt','yuv444p' if scene['width']%2 or scene['height']%2 else 'yuv420p','-movflags','+faststart',str(encoding)]
 try:
  if directory:
   previous_key=None;previous_path=None
   if not encode_only:
    for frame in frames:
     if frame%150==0:print(json.dumps(dict(method='pillow',frame=frame,total=count)),flush=True)
     key=frame_signature(scene,frame/scene['fps']);destination=directory/f'{frame:06d}.png'
     if key==previous_key and previous_path is not None:
      if destination!=previous_path:destination.unlink(missing_ok=True);os.link(previous_path,destination)
     else:atomic_png(render(scene,frame/scene['fps'],str(f.parent),a.aa),destination);unique+=1
     previous_key=key;previous_path=destination
   missing=[frame for frame in range(count) if not (directory/f'{frame:06d}.png').exists()]
   if missing:raise ValueError(f'Cannot encode incomplete native cache; first missingframe {missing[0]}')
   subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','1','-framerate',str(scene['fps']),'-i',str(directory/'%06d.png'),'-frames:v',str(count)]+common,check=True)
  else:
   proc=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{scene["width"]}x{scene["height"]}','-framerate',str(scene['fps']),'-threads','1','-i','-']+common,stdin=subprocess.PIPE);previous_key=None;previous_bytes=None
   try:
    for frame in frames:
     if frame%150==0:print(json.dumps(dict(method='pillow',frame=frame,total=count)),flush=True)
     key=frame_signature(scene,frame/scene['fps'])
     if key!=previous_key:previous_bytes=render(scene,frame/scene['fps'],str(f.parent),a.aa).tobytes();previous_key=key;unique+=1
     proc.stdin.write(previous_bytes)
   finally:proc.stdin.close()
   code=proc.wait()
   if code:raise RuntimeError(f'FFmpeg failed: {code}')
  encoding.replace(out)
 finally:encoding.unlink(missing_ok=True)
 previous_path=Path(str(out)+'.render.json');previous=json.loads(previous_path.read_text()) if previous_path.exists() else None;history=previous.get('captureHistory',[])+[dict(scene=previous.get('scene'),sceneSha256=previous.get('sceneSha256'),capturedFrameRanges=previous.get('capturedFrameRanges'))] if previous else []
 meta=dict(captureHistory=history,method='pillow',engineSha256=engine_sha256,scene=str(f),sceneSha256=hashlib.sha256(f.read_bytes()).hexdigest(),out=str(out),width=scene['width'],height=scene['height'],fps=scene['fps'],frames=count,duration=count/scene['fps'],source=scene.get('source'),antialias=a.aa,frameDirectory=str(directory) if directory else None,capturedFrameRanges=[] if encode_only else ranges,uniqueFramesCaptured=unique);metadata=json.dumps(meta,indent=2)+'\n';temporary=Path(str(out)+f'.render.json.tmp-{os.getpid()}');temporary.write_text(metadata);temporary.replace(Path(str(out)+'.render.json'))
 if directory:(directory/'native-cache.json').write_text(metadata)
 print(json.dumps(meta))
if __name__=='__main__':main()
