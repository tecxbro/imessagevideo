"""Create same-frame sheets, sample stage geometry, and inspect black endpoint."""
import argparse
import csv
import json
import math
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image, ImageDraw


SIDE=600
COUNT=778
CODED=2000


def frames(path):
    command=["ffmpeg","-v","error","-i",str(path),"-map","0:v:0","-vf",f"scale={SIDE}:{SIDE}",
             "-pix_fmt","rgb24","-f","rawvideo","-"]
    with subprocess.Popen(command,stdout=subprocess.PIPE) as process:
        for f in range(COUNT):
            data=process.stdout.read(SIDE*SIDE*3)
            if len(data)!=SIDE*SIDE*3:
                raise ValueError(f"{path}: missing decoded frame {f}")
            yield np.frombuffer(data,np.uint8).reshape(SIDE,SIDE,3)
        if process.stdout.read(1) or process.wait():
            raise ValueError(f"{path}: extra data or invalid EOF")


def cropped(a, rect):
    x,y,w,h=rect
    x0,y0,x1,y1=[round(p*SIDE/CODED) for p in (x,y,x+w,y+h)]
    return a[y0:y1,x0:x1],x0,y0


def bounding(mask, min_pixels):
    y,x=np.where(mask)
    if len(x)<min_pixels:
        return None
    return x,y


def locate(a, rect, kind):
    roi,x0,y0=cropped(a,rect)
    r,g,b=roi.astype(np.int16).transpose(2,0,1)
    if kind=="day":
        mask=(r>165)&(r-g>100)&(r-b>80)
    elif kind=="cyan":
        mask=(b-r>90)&(g-r>72)&(r<98)
    else:
        mask=(b-r>38)&(r-g>45)&(r<170)&(g<105)
    found=bounding(mask,8)
    if found is None:
        return None
    x,y=found
    scale=CODED/SIDE
    if kind=="day":
        return [round((np.median(x)+x0)*scale,1),round((np.median(y)+y0)*scale,1)]
    return round((y.min()+y0)*scale,1)


def geometry(ref, cand, f):
    day_area=(1260,250,500,425)
    # Left edges exclude the event labels and all pointer motion.
    cyan_area=(240,675,175,670)
    violet_area=(240,675,175,660)
    fields={"frame":f,"seconds":f/25}
    for label,area,kind,tolerance in [("red_day",day_area,"day",28),("lisa_top",cyan_area,"cyan",28),
                                      ("marie_top",violet_area,"purple",28)]:
        values=locate(ref,area,kind),locate(cand,area,kind)
        a,b=values
        delta=None if a is None or b is None else (math.dist(a,b) if isinstance(a,list) else abs(a-b))
        fields.update({f"{label}_source":a,f"{label}_render":b,
                       f"{label}_delta":None if delta is None else round(delta,1),
                       f"{label}_pass":delta is not None and delta<=tolerance})
    return fields


def pair_strip(out, name, a, b, rect, pairs):
    w,h=rect[2:]
    thumb_w=min(219,max(124,round(w/h*126)))
    thumb_h=max(44,min(161,round(thumb_w*h/w)))
    ncols=6
    cell_w=thumb_w+12
    cell_h=thumb_h*2+36
    sheet=Image.new("RGB",(ncols*cell_w,((b-a)//ncols+1)*cell_h),"#eae9ef")
    d=ImageDraw.Draw(sheet)
    for j,f in enumerate(range(a,b+1)):
        x,y=j%ncols*cell_w+6,j//ncols*cell_h
        d.text((x,y+3),f"{f:03} / {f/25:.2f}s",fill="#15151c")
        for k,label in enumerate(("Source","Render")):
            pic=Image.fromarray(cropped(pairs[f][k],rect)[0])
            pic.thumbnail((thumb_w,thumb_h))
            y0=y+22+k*(thumb_h+6)
            sheet.paste(pic,(x,y0))
            d.rectangle((x,y0,x+37,y0+13),fill="#fafafa")
            d.text((x+1,y0+1),label,fill="#222229")
    sheet.save(out/f"{name}.jpg",quality=91,optimize=True)


def overview(out, pairs):
    selected=sorted(f for f in pairs if f%16==0 or f==777)
    width=143
    step=width+20
    sheet=Image.new("RGB",(7*width,((len(selected)+6)//7)*(2*width+20)),"#eeeef3")
    d=ImageDraw.Draw(sheet)
    for i,f in enumerate(selected):
        x,y=(i%7)*width,(i//7)*(2*width+20)
        d.text((x+4,y+3),f"{f:03} / {f/25:.2f}s",fill="#11111a")
        for k in (0,1):
            sheet.paste(Image.fromarray(pairs[f][k]).resize((width,width),Image.Resampling.LANCZOS),
                        (x,y+20+width*k))
    sheet.save(out/"overview.jpg",quality=92,optimize=True)


def write_csv(path, rows):
    with path.open("w",newline="") as handle:
        writer=csv.DictWriter(handle,list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("reference",type=Path)
    p.add_argument("render",type=Path)
    p.add_argument("--windows",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    windows=json.loads(args.windows.read_text())
    needed={f for a,b,_ in windows.values() for f in range(a,b+1)}
    needed.update(range(0,COUNT,16))
    pairs={}
    geos=[]
    ending=[]
    for f,(ref,cand) in enumerate(zip(frames(args.reference),frames(args.render),strict=True)):
        if f in {420,427,435,442,452,457,460,470}:
            geos.append(geometry(ref,cand,f))
        if f>=765:
            m1,m2=ref.mean(),cand.mean()
            ending.append({"frame":f,"pts":f*2400,"seconds":f/25,"source_mean":round(m1,3),
                           "render_mean":round(m2,3),"error":round(abs(m1-m2),3),
                           "passes_luma":abs(m1-m2)<=12,"source_max":int(ref.max()),"render_max":int(cand.max())})
        if f in needed:
            # Drop precision for sheet storage only. Quantitative checks use RGB24 input.
            pairs[f]=ref[::2,::2].copy(),cand[::2,::2].copy()
    write_csv(args.out/"calendar-geometry.csv",geos)
    write_csv(args.out/"ending-luma.csv",ending)
    # Sheets use downsampled RGB, so adapt the crop function to the retained sampling.
    global SIDE
    SIDE//=2
    for name,(a,b,rect) in windows.items():
        pair_strip(args.out,name,a,b,rect,pairs)
    overview(args.out,pairs)
    print(f"Paired {COUNT} positions. Final black frame: {ending[-1]['render_max']==0}.")


if __name__=="__main__":
    main()
