import subprocess,sys
def pixels(png):
    # get size
    out=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','csv=p=0',png],capture_output=True,text=True).stdout.strip().split(',')
    w,h=int(out[0]),int(out[1])
    raw=subprocess.run(['ffmpeg','-v','error','-i',png,'-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
    return w,h,raw
def px(raw,w,x,y):
    o=(y*w+x)*3;return raw[o],raw[o+1],raw[o+2]
def scan(png,cond,label):
    w,h,raw=pixels(png)
    xs=[];ys=[]
    for y in range(0,h,2):
        for x in range(0,w,2):
            r,g,b=px(raw,w,x,y)
            if cond(r,g,b): xs.append(x);ys.append(y)
    if not xs: print(label,'none'); return
    print(f'{label}: x {min(xs)}..{max(xs)}  y {min(ys)}..{max(ys)}  w {max(xs)-min(xs)} h {max(ys)-min(ys)}')
    return w,h,raw,xs,ys
# blue bubble in linq f750
def blue(r,g,b): return b>200 and r<120 and g<170
r=scan('frames/linq-f750.png',blue,'linq-f750 blue')
if r:
    w,h,raw,xs,ys=r
    # tail: lowest blue rows - find bottom extent columns
    ymax=max(ys)
    for y in range(ymax-3,ymax+1):
        row=[x for x in range(w) if blue(*px(raw,w,x,min(y,h-1)))]
        if row: print('  row',y,'x',min(row),max(row))
    # sample colors
    print('  color@',xs[len(xs)//2],ys[len(ys)//2],px(raw,w,xs[len(xs)//2],ys[len(ys)//2]))
    # corner radius: scan left edge of top rows vs middle
    for y in [55,60,70,80,100]:
        row=[x for x in range(w) if blue(*px(raw,w,x,y))]
        if row: print('  edge y',y,'left',min(row),'right',max(row))
# gray bubble
def gray(r,g,b): return abs(r-g)<8 and abs(g-b)<8 and 215<r<245
scan('frames/linq-f750.png',gray,'linq-f750 gray')
