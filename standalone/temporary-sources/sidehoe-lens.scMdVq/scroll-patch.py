from pathlib import Path
p=Path(__file__).parent/'project'/'render.py'
s=p.read_text()
start='''    def inbox(self,im,f):
        held = self.s.get("inboxHeldRegistration",{}).get(str(f))
        i=layer(820,2500)'''
end='''    def inbox_scroll_rows(self, stage, frame, rows):
        surface = layer()
        d = ImageDraw.Draw(surface)
        for index, dot, avatar, name, quote, time, divider, opacity in rows:
            if opacity:
                person, preview, stamp_text, key = self.s["inboxRows"][index]
                x, y, width, height = dot
                d.ellipse((x, y, x+width, y+height), fill=(22,169,232,round(255*opacity)))
                backdrop = self.s.get("inboxRowColors",{}).get(person,"")
                self.avatar(surface,key,*avatar,opacity=opacity,bg=backdrop,lit=bool(backdrop))
                fit_ink(surface,person,name,630,opacity,.16,family=messages_font,
                        ink=(18,18,19),fractional=True)
                fit_ink(surface,preview,quote,395,opacity,.19,family=messages_font,
                        ink=(130,129,134),fractional=True)
                fit_ink(surface,stamp_text,time,405,opacity*.85,.21,family=messages_font,
                        ink=(153,149,157),fractional=True)
                left, top, width, height = time
                right = left+width+14
                d.line((right,top+4,right+7,top+11,right,top+18),
                       fill=(192,190,199,round(215*opacity)),width=2)
            d.line((283,divider,820,divider),fill=(235,234,239,186),width=1)
        blur_y, = self.track("inboxScrollSmear",frame)
        composite(stage,blur(surface,(.38,max(.12,blur_y*.26))),0,0)

    def inbox(self,im,f):
        scrolling = self.s.get("inboxScrollRegistration",{}).get(str(f))
        held = scrolling["chrome"] if scrolling else self.s.get("inboxHeldRegistration",{}).get(str(f))
        i=layer(820,2500)'''
assert start in s
s=s.replace(start,end,1)
start='''        status(d,815,214,None if clock else self.c["status"])
        if clock:'''
end='''        status_box = held.get("statusInk") if held else None
        if status_box:
            symbols = layer(815,310)
            status(ImageDraw.Draw(symbols),815,214,None)
            tight = symbols.crop(symbols.getbbox())
            left,top,width,height = status_box
            composite(chrome,tight.resize((round(width),round(height)),Image.Resampling.LANCZOS),
                      left,top)
        else:
            status(d,815,214,None if clock else self.c["status"])
        if clock:'''
assert start in s
s=s.replace(start,end,1)
start='''                text(d,x+dx,571+dy,label,26,"#353535",510,"center")'''
end='''                name = held.get("pinLabels",[None]*3)[j] if held else None
                if name:
                    fit_ink(i,label,name,495,1,.16,family=messages_font,ink=(47,47,49),
                            fractional=True)
                else:
                    text(d,x+dx,571+dy,label,26,"#353535",510,"center")'''
assert start in s
s=s.replace(start,end,1)
start='''        for j,(name,quote,time,key) in enumerate(self.s["inboxRows"]):'''
end='''        standard_rows = [] if scrolling else self.s["inboxRows"]
        for j,(name,quote,time,key) in enumerate(standard_rows):'''
assert start in s
s=s.replace(start,end,1)
start='''            composite(im,blur(row_layer,amount),500-410*row_scale,row_y,1,row_scale)
            if f<=59:'''
end='''            if scrolling:
                self.inbox_scroll_rows(im,f,scrolling["rows"])
            else:
                composite(im,blur(row_layer,amount),500-410*row_scale,row_y,1,row_scale)
            if f<=59:'''
assert start in s
s=s.replace(start,end,1)
p.write_text(s)
