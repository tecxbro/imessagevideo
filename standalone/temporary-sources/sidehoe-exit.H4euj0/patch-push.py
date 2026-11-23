from pathlib import Path
import json
root=Path(__file__).parent/'tile-project'
p=root/'render.py'
s=p.read_text()
start='''                     measured=False, home_indicator=True, follow_registration=None):'''
end='''                     measured=False, home_indicator=True, follow_registration=None,
                     push_header=None):'''
assert start in s
s=s.replace(start,end,1)
s=s.replace('''        d.rounded_rectangle((10,9,389,header_bottom),56,fill="#f0f0f3")''','''        if push_header:
            header_bottom = push_header[0]
        d.rounded_rectangle((10,9,389,header_bottom),56,fill="#f0f0f3")''',1)
s=s.replace('''        else:
            status(d,400,41,self.c["chatStatus"],True)
        header_delta''','''        else:
            status_y = push_header[1] if push_header else 41
            status(d,400,status_y,self.c["chatStatus"],True)
        header_delta''',1)
s=s.replace('''        d.line((43,82+header_delta''','''        if push_header:
            header_delta = push_header[2]-100
        d.line((43,82+header_delta''',1)
s=s.replace('''            stamp(im,badge(85),200,100,38)
            text(d,200,126,c[0]+"  ›",11,INK,560,"center")''','''            avatar_y = push_header[2] if push_header else 100
            stamp(im,badge(85),200,avatar_y,45 if push_header else 38)
            text(d,200,avatar_y+26,c[0]+"  ›",11,INK,560,"center")''',1)
s=s.replace('''def staged_thread(self, im, which, registration, frame):''','''def staged_thread(self, im, which, registration, frame, *, handset_mask=None):''',1)
s=s.replace('''            ramp = registration.get("railBlend")
            if ramp:''','''            ramp = registration.get("railBlend")
            span = registration.get("railSpan")
            if span:
                fade = np.interp(np.arange(upper_limit,SIZE),span,(0,255,255,0)).astype(np.uint8)
                mask = Image.fromarray(np.broadcast_to(fade[:,None],(rail.height,rail.width)))
                im.paste(rail,(start,upper_limit),mask)
            elif ramp:''',1)
s=s.replace('''        bottom=top+161*zoom
        if bottom<SIZE:''','''        bottom,utility_height=registration.get("utilityRow",(top+161*zoom,40*zoom))
        if bottom<SIZE:''',1)
s=s.replace('''(x1,bottom,x2,bottom+40*zoom),5.2*zoom,fill=background''','''(x1,bottom,x2,bottom+utility_height),5.2*zoom,fill=background''',1)
s=s.replace('''        if follow:
            softness=.78''','''        footer = registration.get("keyboardFooter")
        if footer:
            icon_y,home_indicator = footer
            glyph = layer(40,40)
            keyboard_glyph(ImageDraw.Draw(glyph),"emoji",20,20)
            composite(surface,glyph,l+48*zoom-20*zoom,icon_y-20*zoom,1,zoom*.74)
            microphone(d,r-39*zoom,icon_y,21*zoom,"#667076")
            if home_indicator:
                d.rounded_rectangle(home_indicator,4,fill="#252526")
        if follow:
            softness=.78''',1)
s=s.replace('''        composite(im,blur(surface,(softness*.85,softness)),0,0)
''','''        exposure = blur(surface,(softness*.85,softness))
        if handset_mask is not None:
            exposure.putalpha(ImageChops.multiply(exposure.getchannel("A"),handset_mask))
        composite(im,exposure,0,0)
''',1)
assert 'from PIL import ' in s
first=next(line for line in s.splitlines() if line.startswith('from PIL import '))
if 'ImageChops' not in first:
    s=s.replace(first,first+', ImageChops',1)
s=s.replace('''        plate=self.thread_plate("follow",f,keyboard_y,measured=bool(measured),
                               follow_registration=follow_registration)''','''        push_camera = measured.get("pushCamera") if measured else None
        case_offset = 0
        if push_camera:
            camera_y,push_header = push_camera
            case_offset = camera_y-y
            y = camera_y
        else:
            push_header = None
        plate=self.thread_plate("follow",f,keyboard_y,measured=bool(measured),
                               follow_registration=follow_registration,push_header=push_header)
        handset_mask = None
        if push_camera:
            handset_mask=Image.new("L",(SIZE,SIZE))
            width,height=round(plate.width*s),round(plate.height*s*aspect)
            handset_mask.paste(plate.getchannel("A").resize((width,height),Image.Resampling.BICUBIC),
                               (round(x),round(y)))''',1)
s=s.replace('''        chip_shift,=self.track("followChipOffset",f)
        def face''','''        chip_shift,=self.track("followChipOffset",f)
        chip_shift -= case_offset/s
        def face''',1)
s=s.replace('''            self.staged_thread(im,"follow",measured,f)''','''            self.staged_thread(im,"follow",measured,f,handset_mask=handset_mask)''',1)
p.write_text(s)
