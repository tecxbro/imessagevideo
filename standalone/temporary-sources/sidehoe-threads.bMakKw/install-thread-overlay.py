from pathlib import Path
import json,textwrap
d=Path(__file__).parent;p=d/'project/render.py'
s=p.read_text()
start=s.index('            settle = self.s["tracks"].get("sofiaHistorySettle")',s.index('    def thread_plate('))
end=s.index('        else:\n            c=self.c["follow"]',start)
s=s[:start]+'            if not measured:\n'+textwrap.indent(s[start:end],'    ')+s[end:]
start=s.index('            upper_shift,=self.track("followMessageLift",f)',s.index('    def thread_plate('))
end=s.index('        self.composer(im,keyboard_y-41',start)
s=s[:start]+'            if not measured:\n'+textwrap.indent(s[start:end],'    ')+s[end:]
start=s.index('        self.composer(im,keyboard_y-41',s.index('    def thread_plate('))
end=s.index('        # The white screen',start)
s=s[:start]+'        if not measured:\n'+textwrap.indent(s[start:end],'    ')+s[end:]
s=s.replace('def thread_plate(self, which, f, keyboard_y, *, history_offset=0, heading_height=None):',
'''def thread_plate(self, which, f, keyboard_y, *, history_offset=0, heading_height=None,
                     measured=False):''')
insertion='''    def staged_thread(self, im, which, registration, frame):
        """Paint bodies and keyboard on the measured screen plane."""
        surface = layer()
        copy = self.c[which]
        follow = which=="follow"
        if registration["blue"] and follow:
            x0,y0,x1,y1 = registration["blue"]
            h = y1-y0
            upper = layer()
            self.bubble(upper,x0,y0,x1-x0-5,h,[],True,True,text_size=h*.30,paint="#ccf3fc")
            ink = layer()
            for i,line in enumerate(copy[1]):
                fit_ink(ink,line,(x0+18,y0+h*(.20+.37*i),min(x1-x0-44, len(line)*h*.25),h*.24),
                        420,.86,.6,family=messages_font,ink=(254,254,254))
            composite(upper,ink,0,0)
            # The incoming light rolls off the pale outgoing message vertically.
            alpha=np.asarray(upper.getchannel("A"),dtype=float)
            lighting=np.interp(np.arange(SIZE),(y0,y0+h*.40,y1),(.08,.29,.89))
            upper.putalpha(Image.fromarray(np.uint8(np.rint(alpha*lighting[:,None]))))
            composite(surface,upper,0,0)
        for i,(bounds,lines) in enumerate(registration["items"]):
            left,top,right,bottom = bounds
            height = bottom-top
            tail = height*.13
            background = "#eeeef0" if follow and i==0 else "#e8e8eb"
            self.bubble(surface,left+tail,top,right-left-tail-1,height-1,[],
                        text_size=height*.43,paint=background)
            words=copy[i+2]
            if isinstance(words,str):
                words=[words]
            for word,ink in zip(words,lines):
                color = (113,113,115) if follow and i==0 else (34,34,35)
                weight = 440 if follow and i else 410
                fit_ink(surface,word,ink,weight,1,.25,family=messages_font,ink=color)
        if registration["today"]:
            fit_ink(surface,self.c["today"],registration["today"],400,1,.2,
                    family=messages_font,ink=(126,126,126))

        l,r = registration["rails"]
        top,tray,rows = registration["keys"]
        zoom=(r-l)/376
        d=ImageDraw.Draw(surface)
        d.rectangle((l,top,r-1,SIZE),fill=tuple(tray))
        composer_y=top-41*zoom
        prompt=layer(400,45)
        self.composer(prompt,3,settled=True)
        composite(surface,prompt,l-10*zoom,composer_y-3*zoom,1,zoom)
        d=ImageDraw.Draw(surface)
        for (x,y,pitch,w,h,_), letters in zip(rows,("QWERTYUIOP","ASDFGHJKL","ZXCVBNM")):
            for j,letter in enumerate(letters):
                key_x = x+j*pitch
                d.rounded_rectangle((key_x,y+1,key_x+w,y+h+2),w*.114,fill="#b9bcc3")
                d.rounded_rectangle((key_x,y,key_x+w,y+h-1),w*.112,fill="#fdfdfd")
                d.text((key_x+w/2,y+h*.29),letter,font=messages_font(h*.57,420),
                       fill="#1f1f1f",anchor="mt")
            if letters=="ZXCVBNM":
                for key_x,key_w,name,tone in ((l+4,1.20*w,"shift","#fafafa"),
                                               (r-1.22*w-6,1.22*w,"delete","#c4cbd1")):
                    d.rounded_rectangle((key_x,y,key_x+key_w,y+h-1),w*.105,fill=tone)
                    glyph=layer(36,36)
                    keyboard_glyph(ImageDraw.Draw(glyph),name,18,18)
                    composite(surface,glyph,key_x+key_w/2-18*zoom,y+h/2-18*zoom,1,zoom)
        exit_focus=1.50*tween(frame,691,695) if follow else 0
        softness=.52+exit_focus if follow else .49
        composite(im,blur(surface,(softness*.85,softness)),0,0)

'''
a=s.index('    def expose_phone(')
s=s[:a]+insertion+s[a:]
a='''        if a>0:
            plate=self.thread_plate("sofia",f,keyboard_y,history_offset=history,heading_height=heading)'''
b='''        measured = self.s.get("threadRegistration",{}).get("sofia",{}).get(str(f))
        if a>0:
            plate=self.thread_plate("sofia",f,keyboard_y,history_offset=history,
                                    heading_height=heading,measured=bool(measured))'''
assert a in s;s=s.replace(a,b)
a='''            if f>=352 and rail:
                self.expose_phone(im,rim_only(400,827,65),x,y,s,0,.72,rail)
        if f<onset:'''
b='''            if f>=352 and rail:
                self.expose_phone(im,rim_only(400,827,65),x,y,s,0,.72,rail)
            if measured:
                self.staged_thread(im,"sofia",measured,f)
        if f<onset:'''
assert a in s;s=s.replace(a,b)
a='''        plate=self.thread_plate("follow",f,keyboard_y)
        no_frame'''
b='''        measured = self.s.get("threadRegistration",{}).get("follow",{}).get(str(f))
        plate=self.thread_plate("follow",f,keyboard_y,measured=bool(measured))
        no_frame'''
assert a in s;s=s.replace(a,b)
a='''        self.chip(plate,45,433+chip_shift,72,29,self.c["follow"][4],False,.58+.42*a,a,
                  glyph=face,follow_style=True)'''
b='''        no_x,no_y,no_w,no_h = 45,433+chip_shift,72,29
        if measured and measured["no"]:
            lx,ty,rx,by=measured["no"]
            no_x,no_y=(lx-x)/s,(ty-y)/s
            no_w,no_h=min(75,round((rx-lx)/s)),round((by-ty)/s)
        self.chip(plate,no_x,no_y,no_w,no_h,self.c["follow"][4],False,.58+.42*a,a,
                  glyph=face,follow_style=True)'''
assert a in s;s=s.replace(a,b)
a='''                          softness,vertical_scale=aspect)

        # The measured cursor'''
b='''                          softness,vertical_scale=aspect)
        if measured:
            self.staged_thread(im,"follow",measured,f)

        # The measured cursor'''
assert a in s;s=s.replace(a,b)
p.write_text(s)
p=d/'project/scene.json'
a=json.loads(p.read_text())
a['threadRegistration']=json.loads((d/'inside-staging.json').read_text())
p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
