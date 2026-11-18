import subprocess
def pixels(png):
    out=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','csv=p=0',png],capture_output=True,text=True).stdout.strip().split(',')
    w,h=int(out[0]),int(out[1])
    raw=subprocess.run(['ffmpeg','-v','error','-i',png,'-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
    return w,h,raw
def px(raw,w,x,y):
    o=(y*w+x)*3;return raw[o],raw[o+1],raw[o+2]
def blue(r,g,b): return b>200 and r<120 and g<170
w,h,raw=pixels('frames/linq-f750.png')
print("== blue bubble column scan (main bubble rows)")
for y in range(48,200,8):
    row=[x for x in range(300,960) if blue(*px(raw,w,x,y))]
    if row: print(f'  y={y} x {min(row)}..{max(row)}')
print("== tail region rows 160-200")
for y in range(150,210,4):
    row=[x for x in range(600,960) if blue(*px(raw,w,x,y))]
    if row: print(f'  y={y} x {min(row)}..{max(row)}')
print("== tapback badge rows 280-375")
for y in range(280,380,6):
    row=[x for x in range(400,700) if blue(*px(raw,w,x,y))]
    if row: print(f'  y={y} x {min(row)}..{max(row)}')
print("== gray bubble (Sure it'll be) rows 200-300")
def gray(r,g,b): return abs(r-g)<10 and abs(g-b)<10 and 200<r<245
for y in range(195,300,6):
    row=[x for x in range(0,700) if gray(*px(raw,w,x,y))]
    if row: print(f'  y={y} x {min(row)}..{max(row)}')
print("== cash card black rows 330-700")
def blk(r,g,b): return r<60 and g<60 and b<60
for y in range(320,700,10):
    row=[x for x in range(0,700) if blk(*px(raw,w,x,y))]
    if row: print(f'  y={y} x {min(row)}..{max(row)}')
