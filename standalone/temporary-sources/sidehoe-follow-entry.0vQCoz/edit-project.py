from pathlib import Path

project = Path(__file__).parent / 'project'
path = project / 'render.py'
code = path.read_text()

def edit(before, after):
    global code
    assert code.count(before) == 1, before
    code = code.replace(before, after)

edit('def status(d,w,y,label,island=False):', 'def status(d,w,y,label,island=False,*,island_bounds=None):')
edit('''    if island:
        d.rounded_rectangle((w/2-58,y-20,w/2+58,y+14),17,fill="#09090a")
        d.rounded_rectangle((w/2-52,y-13,w/2+8,y+7),10,fill="#141415")
        oval(d,w/2+41,y-3,8,8,"#14131b")
        oval(d,w/2+41,y-3,3.3,3.3,"#292b41")
''','''    if island:
        left,top,right,bottom = island_bounds or (w/2-58,y-20,w/2+58,y+14)
        mid=(top+bottom)/2
        d.rounded_rectangle((left,top,right,bottom),(bottom-top)/2,fill="#09090a")
        d.rounded_rectangle((left+6,mid-10,right-50,mid+10),10,fill="#141415")
        oval(d,right-17,mid,8,8,"#14131b")
        oval(d,right-17,mid,3.3,3.3,"#292b41")
''')
edit('''    def keyboard(self,im,y,*,home_indicator=True):
''','''    def keyboard(self,im,y,*,home_indicator=True,geometry=None):
''')
edit('''        d.rectangle((10,y,389,817),fill=tray)
        for row,start,letters in ((0,17,"QWERTYUIOP"),(1,35.5,"ASDFGHJKL"),(2,72.5,"ZXCVBNM")):
            top=y+9+row*51.3
            for column,label in enumerate(letters):
                x=start+column*37.1
                d.rounded_rectangle((x,top+2,x+32,top+43),5.5,fill="#babdc1")
                d.rounded_rectangle((x,top,x+32,top+40),5.5,fill=key)
                text(d,x+16,top+12,label,20,"#202020",500,"center")
        top=y+112
''','''        rows = [(17,y+9,37.1,32,40),(35.5,y+60.3,37.1,32,40),(72.5,y+111.6,37.1,32,40)]
        bottom, utility_height = y+162, 40
        baseline_home = (134,802,266,808)
        if geometry:
            y, rows, bottom, utility_height, baseline_home = geometry
        d.rectangle((10,y,389,817),fill=tray)
        for (start,top,pitch,width,height),letters in zip(rows,("QWERTYUIOP","ASDFGHJKL","ZXCVBNM")):
            for column,label in enumerate(letters):
                x=start+column*pitch
                d.rounded_rectangle((x,top+2,x+width,top+height+3),5.5,fill="#babdc1")
                d.rounded_rectangle((x,top,x+width,top+height),5.5,fill=key)
                text(d,x+width/2,top+12,label,20,"#202020",460 if geometry else 500,"center")
        top = rows[2][1] if geometry else y+112
''')
edit('''        top=y+162
        for a,b,n,col in [(17,106,"123",utility),(110,292,"space",key),(297,382,"Label",utility)]:
            d.rounded_rectangle((a,top+2,b,top+42),5,fill="#babdc1")
            d.rounded_rectangle((a,top,b,top+40),5,fill=col)
            text(d,(a+b)/2,top+12,n,15,INK,500,"center")
''','''        for a,b,n,col in [(17,106,"123",utility),(110,292,"space",key),(297,382,"Label",utility)]:
            d.rounded_rectangle((a,bottom+2,b,bottom+utility_height+2),5,fill="#babdc1")
            d.rounded_rectangle((a,bottom,b,bottom+utility_height),5,fill=col)
            text(d,(a+b)/2,bottom+12,n,15,INK,500,"center")
''')
edit('''        if home_indicator:
            d.rounded_rectangle((134,802,266,808),3,fill="#202020")
''','''        if home_indicator and baseline_home:
            d.rounded_rectangle(baseline_home,3,fill="#202020")
''')
edit('''    def thread_plate(self, which, f, keyboard_y, *, history_offset=0, heading_height=None,
                     measured=False, home_indicator=True):
''','''    def follow_history(self, im, registration):
        name, outgoing, *incoming = self.c["follow"][:4]
        l,t,r,b = registration["badge"]
        badge_width, badge_height = round(r-l),round(b-t)
        mark=badge(128).resize((badge_width,badge_height),Image.Resampling.LANCZOS)
        composite(im,mark,l,t)
        fit_ink(im,name,registration["name"],480,.94,.22,family=messages_font,ink=(44,44,45))

        (left,top,right,bottom),stops = registration["blue"]
        height=bottom-top
        swatch=layer(im.width,im.height)
        self.bubble(swatch,left,top,right-left-6,height,[],True,True,radius=height*.43)
        rows=np.linspace(top,bottom,len(stops)+2)[1:-1]
        pigments=np.stack([np.interp(np.arange(im.height),rows,c) for c in np.asarray(stops).T],axis=1)
        panel=Image.fromarray(np.uint8(np.rint(pigments))[:,None]).resize(im.size)
        panel.putalpha(swatch.getchannel("A"))
        im.alpha_composite(panel)
        words=[outgoing] if isinstance(outgoing,str) else outgoing
        for i,line in enumerate(words):
            width=min(right-left-34,max(12,len(line)*8))
            fit_ink(im,line,(left+14,top+height*.205+i*height*.31,width,height*.24),420,
                    .84,.38,family=messages_font,ink=(253,253,253))
        for index,(caption,(bounds,line_boxes)) in enumerate(zip(incoming,registration["bubbles"])):
            l,t,r,b=bounds
            height=b-t
            captions=[caption] if isinstance(caption,str) else caption
            has_ink_boxes=len(captions)==len(line_boxes)
            fill=(239,239,242) if index==0 else (232,232,235)
            self.bubble(im,l+height*.14,t,r-l-height*.14,height,
                        [] if has_ink_boxes else captions,paint=fill,radius=height*.35)
            if has_ink_boxes:
                ink=(86,86,88) if index==0 else (39,39,41)
                for line,box in zip(captions,line_boxes,strict=True):
                    fit_ink(im,line,box,420 if index==0 else 475,1,.36,
                            family=messages_font,ink=ink)
        fit_ink(im,self.c["today"],registration["today"],420,.94,.28,
                family=messages_font,ink=(111,111,112))

    def thread_plate(self, which, f, keyboard_y, *, history_offset=0, heading_height=None,
                     measured=False, home_indicator=True, follow_registration=None):
''')
edit('''        if heading_height is not None:
            header_bottom=heading_height
''','''        if heading_height is not None:
            header_bottom=heading_height
        if follow_registration:
            header_bottom=round(follow_registration["headerEnd"])
''')
edit('''        status(d,400,41,self.c["chatStatus"],True)
        d.line((43,82,33,92,43,102),fill="#498af3",width=3)
        d.rounded_rectangle((342,84,358,100),3,outline="#498af3",width=2)
        d.polygon([(359,92),(367,85),(367,99)],outline="#498af3")
''','''        if follow_registration:
            status(d,400,follow_registration["idY"],self.c["chatStatus"],True,
                   island_bounds=follow_registration["island"])
        else:
            status(d,400,41,self.c["chatStatus"],True)
        header_delta = (follow_registration["badge"][1]+follow_registration["badge"][3])/2-100 if follow_registration else 0
        d.line((43,82+header_delta,33,92+header_delta,43,102+header_delta),fill="#498af3",width=3)
        d.rounded_rectangle((342,84+header_delta,358,100+header_delta),3,outline="#498af3",width=2)
        d.polygon([(359,92+header_delta),(367,85+header_delta),(367,99+header_delta)],outline="#498af3")
''')
edit('''        else:
            c=self.c["follow"]
            stamp(im,badge(85),200,100,38)
''','''        elif follow_registration:
            self.follow_history(im,follow_registration)
        else:
            c=self.c["follow"]
            stamp(im,badge(85),200,100,38)
''')
edit('''        if not measured:
            self.composer(im,keyboard_y-41,settled=which=="sofia" and 340<=f<=355)
            self.keyboard(im,keyboard_y,home_indicator=home_indicator)
''','''        if not measured:
            if follow_registration:
                self.composer(im,follow_registration["composerY"],settled=True)
            else:
                self.composer(im,keyboard_y-41,settled=which=="sofia" and 340<=f<=355)
            geometry=follow_registration["layout"] if follow_registration else None
            self.keyboard(im,keyboard_y,home_indicator=home_indicator,geometry=geometry)
''')
edit('''        measured = self.s.get("threadRegistration",{}).get("follow",{}).get(str(f))
        plate=self.thread_plate("follow",f,keyboard_y,measured=bool(measured))
''','''        measured = self.s.get("threadRegistration",{}).get("follow",{}).get(str(f))
        follow_registration=self.s.get("followSettledRegistration",{}).get(str(f))
        plate=self.thread_plate("follow",f,keyboard_y,measured=bool(measured),
                               follow_registration=follow_registration)
''')
path.write_text(code)
