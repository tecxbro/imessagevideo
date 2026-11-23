"""Build source / first / revised crops at significant inspection frames."""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from compare_visual import CODED, frames


BOARDS={
    "yes-contact":[(673,(440,650,1110,750)),(675,(440,650,1110,750)),
                   (676,(440,650,1110,750)),(684,(440,650,1110,750)),(688,(440,650,1110,750))],
    "largest-misses-a":[(62,(300,0,1400,1850)),(134,(90,300,1820,1700)),
                        (201,(300,530,1400,1100)),(255,(70,300,1840,1450)),
                        (308,(150,470,1700,1160))],
    "largest-misses-b":[(394,(645,430,1260,1080)),(420,(235,345,1560,1045)),(437,(235,690,1550,530))],
    "both-endings":[(765,(0,0,2000,2000)),(766,(0,0,2000,2000)),
                    (770,(0,0,2000,2000)),(776,(0,0,2000,2000)),(777,(0,0,2000,2000))]
}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("reference",type=Path)
    p.add_argument("first",type=Path)
    p.add_argument("revised",type=Path)
    p.add_argument("--font",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    args.out.mkdir(exist_ok=True,parents=True)
    need={f for items in BOARDS.values() for f,_ in items}
    sources=[{f:Image.fromarray(a) for f,a in enumerate(frames(path)) if f in need}
             for path in (args.reference,args.first,args.revised)]
    title=ImageFont.truetype(args.font,22)
    label=ImageFont.truetype(args.font,17)
    w=380
    pad=18
    for name,items in BOARDS.items():
        rows=[] 
        for f,box in items:
            tiles=[]
            for results in sources:
                img=results[f]
                x,y,bw,bh=box
                q=img.width/CODED
                crop=img.crop(tuple(round(v*q) for v in (x,y,x+bw,y+bh)))
                crop.thumbnail((w,325),Image.Resampling.LANCZOS)
                tiles.append(crop)
            rows.append((f,tiles))
        board=Image.new("RGB",(3*w+4*pad,62+sum(48+r[1][0].height for r in rows)),"#ebebf0")
        d=ImageDraw.Draw(board)
        for i,s in enumerate(("Source","First export","Revised export")):
            d.text((pad+i*(w+pad),20),s,font=title,fill="#171721")
        y=60
        for f,tiles in rows:
            d.text((pad,y),f"Frame {f}    PTS {f/25:.3f} s",font=label,fill="#35323d")
            for i,img in enumerate(tiles):
                board.paste(img,(pad+i*(w+pad)+(w-img.width)//2,y+24))
            y+=48+tiles[0].height
        board.save(args.out/f"{name}.jpg",quality=94,optimize=True)


if __name__=="__main__":
    main()
