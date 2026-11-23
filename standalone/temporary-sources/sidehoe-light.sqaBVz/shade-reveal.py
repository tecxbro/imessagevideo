from pathlib import Path
p=Path(__file__).parent/'project'/'render.py'
s=p.read_text()
start='''        title_y,=self.track("assistantTitleY", f)
        for j,line in enumerate(self.c["assistant"]):
            lettering'''
end='''        finish = screen.get("islandShade")
        if finish:
            left,top,right,bottom,pigment,softness = finish
            margin = math.ceil(softness*3)+2
            box = (left-margin,top-margin,right+margin,bottom+margin)
            area = im.crop(box)
            mask = Image.new("L",area.size)
            ImageDraw.Draw(mask).rounded_rectangle(
                (margin,margin,margin+right-left,margin+bottom-top),
                radius=(bottom-top)/2,fill=255,
            )
            coverage = np.asarray(mask.filter(ImageFilter.GaussianBlur(softness)),dtype=float)/255
            rgba = np.array(area)
            adjusted = rgba[:,:,:3]-coverage[...,None]*np.asarray(pigment)
            rgba[:,:,:3] = np.uint8(np.clip(np.rint(adjusted),0,255))
            im.paste(Image.fromarray(rgba),box[:2])
        title_y,=self.track("assistantTitleY", f)
        captions = self.s.get("assistantCaptionOptics",{}).get(str(f))
        for j,line in enumerate(self.c["assistant"]):
            if captions:
                left,top,width,height,weight,opacity,sx,sy = captions[j]
                fit_ink(im,line,(left,top,width,height),weight,opacity,(sx,sy),
                        family=messages_font,ink=(8,8,8),fractional=True)
                continue
            lettering'''
assert start in s
p.write_text(s.replace(start,end,1))
