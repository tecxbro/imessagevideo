from pathlib import Path
import json
p=Path('sidehoe-skill-trial/project')
s=json.loads((p/'scene.json').read_text())
t=s['tracks']
t['assistantY']=[[134,266],[135,309],[136,340],[137,365],[138,379],[140,401],[145,433],[154,466],[159,523],[161,574]]
t['assistantTitleY']=[[135,117],[138,178],[140,196],[145,211],[154,239],[159,294],[161,430]]
t['assistantWash']=[[134,0],[136,.08],[140,.15],[145,.45],[154,.95],[159,.98],[161,.93]]
t['followCamera'] += [[648,47,1.036],[650,47,1.05]]
t['followCamera']=[([653,51,1.08] if f==653 else [f,y,z]) for f,y,z in sorted(t['followCamera'])]
t['sofiaCamera']=[([f,y+22,z] if 338<=f<=349 else [f,y,z]) for f,y,z in t['sofiaCamera']]
(p/'scene.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
f=p/'render.py';v=f.read_text()
v=v.replace('d.rounded_rectangle((317,52,583,120),40,fill="#0c0d10")','d.rounded_rectangle((316,58,586,131),45,fill="#0c0d10")')
v=v.replace('oval(d,553,83,12,12,"#353444")','''        d.rounded_rectangle((329,68,466,120),23,fill="#151518")
        oval(d,548,94,16,16,"#161720")
        oval(d,548,94,7,7,"#252b42")'''.lstrip())
v=v.replace('text(d,103,87,self.c["status"],33,INK,630)','text(d,103,86,self.c["status"],34,INK,630)')
v=v.replace('for i, height in enumerate((6, 10, 14, 19)):\n            d.rounded_rectangle((755+8*i,107-height,760+8*i,107),2,fill=INK)\n        d.arc((789,88,822,111),206,332,fill=INK,width=4)\n        oval(d,806,105,2,2,INK)\n        d.rounded_rectangle((826,91,857,105),4,fill=INK)','''for i, height in enumerate((7, 12, 17, 21)):
            d.rounded_rectangle((604+11*i,116-height,612+11*i,116),3,fill=INK)
        d.arc((667,90,707,118),208,332,fill=INK,width=5)
        d.arc((674,99,700,118),208,332,fill=INK,width=4)
        oval(d,687,114,4,4,INK)
        d.rounded_rectangle((727,93,774,115),6,fill=INK)
        d.rectangle((776,100,781,108),fill=INK)''')
v=v.replace('d.rounded_rectangle((89,174,207,242),27,fill="#eeedf4")','''d.rounded_rectangle((85,181,198,252),35,fill="#f7f6f8")
        d.rounded_rectangle((720,181,790,251),33,fill="#f8f7f9")
        for half,y_line in ((19,208),(14,218),(8,228)):
            d.rounded_rectangle((755-half,y_line,755+half,y_line+4),2,fill="#535258")''')
v=v.replace('text(d,148,192,self.c["edit"],33,INK,615,"center")','text(d,143,208,self.c["edit"],33,INK,640,"center")')
v=v.replace('text(d,450,190,self.c["inbox"],35,INK,655,"center")','text(d,450,207,self.c["inbox"],36,INK,650,"center")')
v=v.replace('self.avatar(beneath,k,x,385,176,tween(f,134,138))','self.avatar(beneath,k,x,396,178,tween(f,134,138))').replace('text(d,x,491,n,29,INK,520,"center")','text(d,x,501,n,29,INK,520,"center")')
v=v.replace('stamp(beneath,badge(128),450,389,198)','stamp(beneath,badge(128),450,396,201)').replace('text(d,450,497,self.c["brand"]+"  ✓",29,INK,550,"center")','text(d,450,501,self.c["brand"]+"  ✓",29,INK,550,"center")')
v=v.replace('title_y+j*64,60,640','title_y+j*75,60,640')
f.write_text(v)
