from pathlib import Path
import json
import numpy as np
from phones import load,runs
p=Path('sidehoe-skill-trial/repair/project')
s=json.loads((p/'scene.json').read_text())
t=s['tracks']
t['personalLine1']=[[162,284,412,442,51],[163,284,426,444,49],[164,284,437,440,49],
    [165,282,442,443,50],[166,282,448,442,50],[168,282,456,442,62],[170,282,460,442,58],
    [172,282,462,445,55],[178,267,463,472,56],[184,264,461,478,51],[187,264,442,478,52],
    [192,264,429,479,52],[196,264,418,480,51],[201,264,400,480,40],[205,265,353,480,52],
    [208,266,310,482,46],[210,271,254,483,49],[211,270,211,478,53],[212,264,129,476,57]]
t['personalLine2']=[[178,240,538,518,51],[182,240,531,516,60],[184,240,526,518,66],
    [188,240,501,520,69],[192,238,490,523,72],[196,238,476,522,74],[201,238,447,527,75],
    [205,240,407,530,74],[208,244,362,522,72],[210,250,305,523,70],
    [211,248,259,525,67],[212,244,191,518,71]]
t['lisaProfileBounds']=[]
for f in range(282,313):
    a=load('source',f)
    r,g,b=a.transpose(2,0,1)
    good=(g-r>19)&(g-b>12)&(r>106)&(g>138)
    good[:,346:]=False
    blocks=runs(good.sum(1)>11)
    if not len(blocks):continue
    lo,hi=max(blocks,key=lambda v:v[1]-v[0])
    ys,xs=np.where(good[lo:hi])
    x0,x1=xs.min(),xs.max()+1
    t['lisaProfileBounds'].append([f,int(x0+x1),int(lo+hi),int(max(x1-x0,hi-lo)*2)])
t['ellaProfileX']=[[282,446],[286,466],[288,668],[289,769],[290,808],
               [291,822],[293,841],[298,860],[300,867],[304,876],[308,879],[311,895],[312,905]]
t['ellaRevealVeil']=[[282,0],[286,0],[288,.44],[290,.75],[295,.92],[300,.96],[305,.97],[312,.97]]
t['lisaOutline']=[[288,0],[289,.24],[290,.96],[291,.91],[293,.73],[296,.47],
                  [299,.23],[300,.15],[302,.07],[305,0],[312,0]]
t['suggestionLaunch']=[[336,.82],[337,.95],[338,1],[340,1]]
t['calendarArrivalSmear']=[[397,81],[398,68],[399,59],[400,39],[401,34],[402,24],[403,15],[404,9],[405,6],[408,0]]
t['calendarCamera'][3]=[400,190,707,82]
t['calendarCamera'][4]=[401,190,655,82]
t['calendarCamera'][5]=[402,190,598,82]
t['calendarCamera'][6]=[403,188,533,82]
t['calendarCursor']=[[398,989,947,-92],[399,977,896,-95],[400,965,829,-98],
    [401,934,790,-95],[402,901,717,-91],[403,875,676,-95],[404,864,641,-96],[405,897,596,-94]]+[x for x in t['calendarCursor'] if x[0]>405]
d=s['clusterWipe']
d.extend([[257,0,0,180,1000],[257,835,0,165,1000],
          [258,0,0,900,409],[258,80,440,900,185],[258,110,650,890,220],[258,316,0,640,1000]])
d.sort()
(p/'scene.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
f=p/'render.py';v=f.read_text()
v=v.replace('''        if f<168:
            gentle_characters(title,self.c["personal"][0],500,y,65,660,f,start-1,.30)
        else:
            fit_ink(title,self.c["personal"][0],self.track("personalLine1",f),660,
                    mix(.72,1,tween(f,168,174)))''','''        line1=self.c["personal"][0]
        x,top,w,h=self.track("personalLine1",f)
        if f<167:
            sizes=(3,7,10,14,17)
            visible=min(len(line1),sizes[f-start])
            scale=font(80,660).getlength(line1[:visible])/font(80,660).getlength(line1)
            fit_ink(title,line1[:visible],(x,top,w*scale,h),660,
                    mix(.48,.86,tween(f,162,168)),2*(1-tween(f,162,168)))
        else:
            fit_ink(title,line1,(x,top,w,h),660,mix(.82,1,tween(f,167,173)))''')
v=v.replace('''            left=500-face.getlength(line)/2
            hints=(179,178,178,182,183,177,181,183,180,182,181,177)
            for j,char in enumerate(line):
                ink=(72,35,76,round(255*tween(f,hints[min(j,len(hints)-1)],188)))
                text(ImageDraw.Draw(title),left+face.getlength(line[:j]),y+56,char,89,ink,765)''','''            left,top,_,_=self.track("personalLine2",f)
            hints=(179,178,178,182,183,177,181,183,180,182,181,177,177)
            for j,char in enumerate(line):
                phase=tween(f,hints[min(j,len(hints)-1)],188)
                ink=(95,42,102,round(255*phase))
                text(ImageDraw.Draw(title),left+face.getlength(line[:j]),top+3,char,89,ink,765)''')
v=v.replace('''            if j==0 and local>=0 and local<15:
                for shift in (0,2):
                    d.arc((39+shift,308+shift,261-shift,358-shift), -140+local*12,
                          min(224,170+local*12),fill="#68d982" if shift==0 else "#c4f6cc",width=2)''','''            if j==0 and f>=288:
                pulse,=self.track("lisaOutline",f)
                if pulse:
                    color=(97,233,112,round(255*pulse))
                    d.rounded_rectangle((39,308,261,358),24,outline=color,width=2)''')
v=v.replace('''            y=414+yoff-90*(1-p)
            composite(im,blur(tile,9*(1-p)+6*max(0,1-abs(f-287)/3)+5*tween(f,308,312)),
                      x-150*zoom,y-124*zoom,opacity,zoom)''','''            y=414+yoff-90*(1-p)
            if f>=282 and j in (0,1):
                measured_x,y,diam=self.track("lisaProfileBounds",f)
                zoom=diam/204
                x=measured_x if j==0 else self.track("ellaProfileX",f)[0]
            composite(im,blur(tile,9*(1-p)+6*max(0,1-abs(f-287)/3)+5*tween(f,308,312)),
                      x-150*zoom,y-124*zoom,opacity,zoom)''')
v=v.replace('''        p=tween(f,onset-3,340) if f>=onset else 0
        if p>0:''','''        p=self.track("suggestionLaunch",f)[0] if f>=onset else 0
        if p>0:''')
v=v.replace('landing_y = mix(375,420,tween(f,onset,340))','landing_y=interpolate([[336,378],[337,391],[338,406],[340,420]],f)[0]')
v=v.replace('''        if smear:
            cal = vertical_blur(cal,smear)''','''        if smear:
            # The incoming calendar moves independently from the outgoing text.
            cal = vertical_blur(cal,smear)''')
f.write_text(v)
