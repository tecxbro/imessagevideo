import csv, subprocess
import numpy as np
W=500
cmd=['ffmpeg','-v','error','-i','/Users/darshan/Downloads/sidehoe.mp4','-vf',f'scale={W}:{W}','-pix_fmt','rgb24','-f','rawvideo','-']
p=subprocess.Popen(cmd,stdout=subprocess.PIPE)
out=csv.writer(open('sidehoe-recreation/evidence/camera-landmarks.csv','w'))
out.writerow(['frame','PTS seconds','layer','A x','A y','B x','B y','spacing','description'])
for f in range(778):
    a=np.frombuffer(p.stdout.read(W*W*3),np.uint8).reshape(W,W,3)
    def put(layer,x,y,xx,yy,note):
        out.writerow([f,f/25,layer,x,y,xx,yy,round(np.hypot(xx-x,yy-y),1),note])
    if f in (10,18,35,42,46,50,54):
        # Gold portrait, cobalt portrait. Median of hue mask.
        r,g,b=a[:250].astype('int16').transpose(2,0,1)
        def center(mask):
            yy,xx=np.where(mask)
            return np.median(xx)*4,np.median(yy)*4
        xx=np.arange(W)
        A=center((r-g>17)&(g-b>25)&(xx<190))
        B=center((b-r>65)&(g-r>35)&(xx>300))
        put('inbox',*A,*B,'color centers of pinned gold and blue contact disks')
    if f in (327,335,339,349,355,632,645,659,665,670,675,684,693):
        # Dark hull side landmarks sampled on the horizontal row through screen center.
        pix=a[W//2]
        mask=np.where(np.max(pix,axis=-1)<55)[0]
        if len(mask): put('phone body',mask[0]*4,1000,mask[-1]*4,1000,'dark extreme left and right on center row')
    if f in (410,420,427,431,435,442,452,457,460,470):
        r,g,b=a.astype('int16').transpose(2,0,1)
        y,x=np.where((r>170)&(r-g>110)&(r-b>80)&(np.arange(W)[:,None]<205))
        if len(x):
            A=(round(np.median(x)*4),round(np.median(y)*4))
            # White gutters outside bars contain thin grid lines. Read first horizontal gray line
            # following the date disk using a middle column above the appointments.
            v=a[:,225].mean(axis=1)
            yy=np.nonzero((v<237)&(v>150)&(np.arange(W)>y.max()+10)&(np.arange(W)<y.max()+50))[0]
            B=(900,int(yy[0])*4) if len(yy) else (900,-1)
            put('calendar grid',*A,*B,'red day center and first grid line at x 900, -1 denotes missing')
p.wait()
