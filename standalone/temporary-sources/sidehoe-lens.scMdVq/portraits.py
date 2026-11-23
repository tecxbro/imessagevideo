from pathlib import Path
p=Path(__file__).parent/'project'
art=p/'artwork.py'
s=art.read_text()
pos=s.index('@lru_cache(maxsize=40)\ndef badge')
method='''@lru_cache(maxsize=2)
def compact_inbox_head(pose):
    """Draw the independently editable contacts used by the small inbox rows."""
    im = Image.new("RGBA",(256,256))
    d = ImageDraw.Draw(im)
    dark = pose == "glasses"
    hair = "#292b2c" if dark else "#686b6a"
    curve_polygon(d,(52,158),(
        ((61,143),(54,114),(58,93)), ((61,65),(85,42),(104,41)),
        ((125,47),(138,26),(157,39)), ((187,51),(185,72),(192,89)),
        ((199,105),(191,129),(195,148)), ((201,158),(201,169),(187,175)),
        ((145,183),(92,170),(70,178)), ((55,187),(46,178),(52,158)),
    ),hair)
    shadow = "#4c4641" if dark else "#8b8c85"
    d.arc((59,42,175,154),193,293,fill=shadow,width=9)
    oval(d,127,131,56,68,"#a57756")
    oval(d,128,127,50,63,"#d8aa83")
    oval(d,120,120,43,53,"#e0b591")
    shape = "#303233" if dark else "#797e7a"
    curve_polygon(d,(66,116),(
        ((62,87),(73,65),(95,55)), ((115,47),(146,55),(163,63)),
        ((184,59),(184,76),(188,91)), ((173,92),(140,89),(112,105)),
        ((89,110),(82,121),(79,148)), ((66,149),(59,142),(66,116)),
    ),shape)
    if dark:
        for x in (103,154):
            oval(d,x,129,26,23,"#332725")
            oval(d,x,128,20,17,"#e4c7ae")
            oval(d,x,129,13,9,"#f9ebdf")
            oval(d,x+1,131,5.2,6.4,"#3e3534")
        d.line((125,122,132,122),fill="#3a2b26",width=7)
    else:
        for x in (105,151):
            d.arc((x-15,108,x+15,135),193,346,fill="#70503f",width=6)
        oval(d,92,142,11,7,"#e8a79a")
        oval(d,164,143,11,7,"#e8a79a")
    oval(d,128,148,9,7,"#c59573")
    curve_polygon(d,(101,160),(
        ((114,167),(142,168),(155,158)),
        ((154,177),(141,184),(128,183)),
        ((116,183),(104,174),(101,160)),
    ),"#5d342b")
    d.arc((103,152,153,172),6,168,fill="#f7e4d3",width=6)
    if not dark:
        curve_polygon(d,(150,63),(
            ((154,62),(171,78),(181,96)), ((184,111),(191,125),(200,139)),
            ((184,140),(172,128),(163,116)), ((148,99),(142,80),(150,63)),
        ),"#a4a6a5")
        d.rounded_rectangle((166,164,203,220),19,fill="#c3946f")
        d.rounded_rectangle((175,135,189,194),7,fill="#d6a881")
        d.rounded_rectangle((190,149,203,192),7,fill="#e4b18b")
        oval(d,183,193,17,18,"#e2b392")
        d.arc((177,175,200,197),102,289,fill="#b18165",width=3)
    return im


'''
s=s[:pos]+method+s[pos:]
art.write_text(s)
r=p/'render.py'
s=r.read_text().replace('from artwork import rounded_gradient, sprite_portrait, stamp, text','from artwork import compact_inbox_head, rounded_gradient, sprite_portrait, stamp, text',1)
s=s.replace('''                self.avatar(surface,key,*avatar,opacity=opacity,bg=backdrop,lit=bool(backdrop))''','''                compact = self.s.get("inboxCompactPortraits",{}).get(str(index))
                if compact:
                    pose, color = compact
                    x,y,diam = avatar
                    oval(d,x,y,diam/2,diam/2,(*color,round(255*opacity)))
                    stamp(surface,compact_inbox_head(pose),x,y,diam,opacity)
                else:
                    self.avatar(surface,key,*avatar,opacity=opacity,bg=backdrop,lit=bool(backdrop))''',1)
r.write_text(s)
