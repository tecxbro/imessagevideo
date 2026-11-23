from pathlib import Path
p=Path(__file__).parent/'project'/'render.py'
s=p.read_text()
old='''    def inbox_scroll_rows(self, stage, frame, rows, home):'''
new='''    def inbox_intro_chrome(self, stage, chrome, poses):
        parts = ((60,157,260,257),(538,158,805,263),(43,267,226,391),
                 (293,271,527,387),(624,266,779,393))
        for section, pose in zip(parts,poses,strict=True):
            if pose is None:
                continue
            x,y,w,h,opacity,soft_x,soft_y,angle = pose
            patch=chrome.crop(section)
            pixels=np.asarray(patch,dtype=np.int16)
            ink=(pixels[:,:,3]>=166)&(pixels[:,:,:3].mean(2)<161)
            iy,ix=np.where(ink)
            if not len(ix):
                continue
            l,t,r,b=ix.min(),iy.min(),ix.max()+1,iy.max()+1
            sx,sy=w/(r-l),h/(b-t)
            patch=patch.resize((max(1,round(patch.width*sx)),max(1,round(patch.height*sy))),
                               Image.Resampling.BICUBIC)
            left,top=x-l*sx,y-t*sy
            if angle:
                w0,h0=patch.size
                patch=patch.rotate(angle,Image.Resampling.BICUBIC,expand=True)
                left-=(patch.width-w0)/2
                top-=(patch.height-h0)/2
            composite(stage,blur(patch,(soft_x,soft_y)),left,top,opacity)

    def inbox_scroll_rows(self, stage, frame, rows, home, *, focus=None):'''
assert old in s
s=s.replace(old,new,1)
s=s.replace('''        blur_y, = self.track("inboxScrollSmear",frame)
        composite(stage,blur(surface,(.38,max(.12,blur_y*.26))),0,0)''','''        blur_y, = self.track("inboxScrollSmear",frame)
        composite(stage,blur(surface,focus or (.38,max(.12,blur_y*.26))),0,0)''',1)
s=s.replace('''        scrolling = self.s.get("inboxScrollRegistration",{}).get(str(f))''','''        intro = self.s.get("inboxIntroRegistration",{}).get(str(f))
        scrolling = self.s.get("inboxScrollRegistration",{}).get(str(f))''',1)
s=s.replace('''        if f<10:
            alpha,softness,rise=self.track("inboxIntroHeader",f)''','''        if intro:
            self.inbox_intro_chrome(im,chrome,intro["chrome"])
        elif f<10:
            alpha,softness,rise=self.track("inboxIntroHeader",f)''',1)
s=s.replace('''        standard_rows = [] if scrolling else self.s["inboxRows"]''','''        standard_rows = [] if scrolling or intro else self.s["inboxRows"]''',1)
s=s.replace('''        elif held:
            composite(im,blur(i,amount),500-410*scale,y,1,scale)''','''        elif intro:
            self.inbox_scroll_rows(im,f,intro["rows"],None,focus=intro["rowFocus"])
        elif held:
            composite(im,blur(i,amount),500-410*scale,y,1,scale)''',1)
s=s.replace('''            if tag is not None:
                _, center_y, _, _ = interpolate(self.s["tracks"]["inboxIntroPin1"],f)
                composite(im,blur(tag,5*(1-p)),387,center_y-115,p,.91)''','''            if tag is not None and intro:
                left,top,width,height,opacity,focus=intro["note"]
                note=tag.resize((round(width),round(height)),Image.Resampling.BICUBIC)
                composite(im,blur(note,focus),left,top,opacity)
            elif tag is not None:
                _, center_y, _, _ = interpolate(self.s["tracks"]["inboxIntroPin1"],f)
                composite(im,blur(tag,5*(1-p)),387,center_y-115,p,.91)''',1)
p.write_text(s)
