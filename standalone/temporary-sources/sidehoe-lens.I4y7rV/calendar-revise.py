from pathlib import Path
import json
root=Path(__file__).parent
p=root/'project/render.py'
s=p.read_text()
s=s.replace('''        for j in range(8):
            y=grid_y+grid_step*j
            d.line((left,y,right,y),fill="#d5d2dc",width=2)
            text(d,left-8,y-8,f"{j or 12}AM",h*.195,tick_ink,535,"right")''','''        tick_controls = self.s.get("calendarHandoff",{}).get(str(f))
        ticks = layer() if tick_controls else cal
        tick_draw = ImageDraw.Draw(ticks)
        for j in range(8):
            y=grid_y+grid_step*j
            if tick_controls:
                tick_right, tick_shift, tick_focus, tick_trail, strength, _, _, _ = tick_controls
            else:
                tick_right, tick_shift = left-8, 0
            d.line((left,y,right,y),fill="#d5d2dc",width=2)
            text(tick_draw,tick_right,y-8+tick_shift,f"{j or 12}AM",h*.195,tick_ink,535,"right")''')
s=s.replace('''        typed=ImageDraw.Draw(calendar_labels)
        for index''','''        typed=ImageDraw.Draw(calendar_labels)
        bar_left,bar_right,bar_shift = tick_controls[-3:] if tick_controls else (left,right,0)
        for index''')
s=s.replace('''                top,height,opacity=exposure[index*3:index*3+3]
                bottom=top+height''','''                top,height,opacity=exposure[index*3:index*3+3]
                top += bar_shift
                bottom=top+height''')
s=s.replace('bar=layer(round(right-left),max(1,round(bottom-top)))',
            'bar=layer(round(bar_right-bar_left),max(1,round(bottom-top)))')
s=s.replace('composite(calendar_blocks,bar,left,top)','composite(calendar_blocks,bar,bar_left,top)')
s=s.replace('text(typed,left+13,top+', 'text(typed,bar_left+13,top+')
s=s.replace('''        if exposure:
            label_blur=exposure[-1]''','''        if tick_controls:
            ticks = vertical_blur(ticks,tick_trail).convert("RGBa")
            ticks = ticks.filter(ImageFilter.GaussianBlur((tick_focus,1.4))).convert("RGBA")
            composite(im,ticks,0,0,strength)
        if exposure:
            label_blur=exposure[-1]''')
p.write_text(s)
p=root/'project/scene.json'
j=json.loads(p.read_text())
j['calendarHandoff'] = {
    str(f):[right,shift,focus,trail,strength,edge,874,dy]
    for f,right,shift,focus,trail,strength,edge,dy in [
    (397,184,-3,3.1,83,.88,194,2.0),
    (398,184,-3,3.0,75,.87,194,2.0),
    (399,182,0,2.7,69,.93,194,2.5),
    (400,184,3,2.3,92,.97,194,4.5),
    (401,186,0,1.15,92,1,195,4),
    (402,186,4,1.00,68,1,195,3),
    (403,186,5,.85,48,1,195,2.5),
    (404,186,3,.8,30,1,195,2),
    (405,186,0,.65,23,1,195,1),
    (406,186,0,.6,21,1,195,1),
    (407,186,0,.55,17,1,195,.5),
    (408,186,0,.5,14,1,195,0),
    (409,187,0,.5,10,1,195,0),
    (410,188,0,.5,8,1,195,0),
    (411,188,0,.5,5,1,195,0),
    (412,189,0,.5,3,1,195,0),
    ]
}
for k, vals in {
    'sendReplyBox':{397:[505,222,930,322],398:[505,206,931,305],399:[505,184,931,284],
                    400:[505,153,931,256],401:[505,111,931,218],402:[506,72,932,174]},
    'sendSuggestionBox':{397:[344,380,933,537],398:[343,362,934,522],399:[343,340,934,502],
                         400:[342,309,935,473],401:[342,268,935,435],402:[343,228,935,391]},
    'sendExitExposure':{397:[1.45,3.7],398:[1.9,4.15],399:[2.4,4.9],
                        400:[2.8,6.2],401:[3.4,7.0],402:[3.1,7.3]}
}.items():
    t=j['tracks'][k]
    for i,row in enumerate(t):
        if row[0] in vals:
            t[i] = [row[0],*vals[row[0]]]
p.write_text(json.dumps(j,indent=2)+'\n')
