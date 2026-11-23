from pathlib import Path
p=Path('sidehoe-skill-trial/repair/project/render.py')
s=p.read_text()
s=s.replace('''                composite(im,blur(tag,5*(1-p)),387,cy-157,p,.91)''','''                _, center_y, _, _ = self.track("inboxIntroPin1",f)
                composite(im,blur(tag,5*(1-p)),387,center_y-115,p,.91)''',1)
a=s.index('        onset=self.at("sofia.suggestion")',s.index('    def suggestion_group'))
b=s.index('        a=tween(f,self.at("sofia.no")',a)
s=s[:a]+s[b:]
a=s.index('        if f>=381:',s.index('    def sofia(self,im,f):'))
s=s[:a]+'''        if self.at("sofia.suggestion")<=f<360:
            c=self.c["sofia"]
            left,top,width,height=self.track("sofiaSuggestedBounds",f)
            incoming=layer()
            self.bubble(incoming,left,top,width-6,height,c[6],True,text_size=height*.33)
            label=height*.20
            d=ImageDraw.Draw(incoming)
            text(d,left+15,top-label*.99,c[5],label,MUTED,520)
            launch=1-tween(f,336,340)
            composite(im,blur(incoming,3*launch),0,0,.92+.08*(1-launch))
'''+s[a:]
a=s.index('        onset=[',s.index('    def end(self,im,f):'))
b=s.index('            face=font(size,weight)',a)
s=s[:a]+'''        caption_ids=(("the","most","personal"),("imessage","assistant","yet"))
        for j,row in enumerate(words):
            size=47 if j==0 else 48
            weight=515 if j==0 else 690
            onset=[self.at(f"ending.{word_id}") for word_id in caption_ids[j]]
            if f<766:
                for word,word_id,start in zip(row,caption_ids[j],onset):
                    if f<start:
                        continue
                    track=self.s["tracks"][f"closingInk-{word_id}"]
                    x,y,w,h,a=interpolate(track,f)
                    if f<track[0][0]:
                        a*=.65
                    fit_ink(im,word,(x,y,w,h),weight,a,2.3*(1-a))
                continue
'''+s[b:]
s=s.replace('onset[j][k]-1,onset[j][k]+6','onset[k]-1,onset[k]+6',1)
p.write_text(s)
