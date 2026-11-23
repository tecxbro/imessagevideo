#!/usr/bin/env python3
"""Independent scene builder for the 03-photon-mini recreation.

Authored from direct source.mp4 measurement only (frame-exact mask/bbox reads
at key frames). No source pixels are used as assets: all artwork is native
geometry/text (Apple Color Emoji supplies food/memoji/icon glyphs via the
system fallback). Screen-local space is 750x1560; one phone group carries the
camera dance.
"""
import json, math

W, H, FPS, DUR = 1920, 1080, 30.0, 42.0
L = []
_id = [0]
def nid(p):
    _id[0] += 1
    return f'{p}{_id[0]:03d}'

def node(t, **kw):
    d = {'type': t}; d.update(kw); d.setdefault('id', nid(t)); return d

def rect(x, y, w, h, fill, r=0, **kw):
    return node('rect', x=x, y=y, width=w, height=h, fill=fill, radius=r, **kw)

def circle(x, y, d, fill, **kw):
    return node('circle', x=x, y=y, width=d, height=d, fill=fill, **kw)

def text(x, y, s, fs, fill='#000000', family='SF Pro Text', weight=400, **kw):
    return node('text', x=x, y=y, text=s, fontSize=fs, fill=fill,
                fontFamily=family, fontWeight=weight, **kw)

def grp(children, x=0, y=0, **kw):
    return node('group', children=children, x=x, y=y, **kw)

def k(pts):   # [(t,val,ease?)]
    return [{'t': p[0], 'value': p[1], 'ease': p[2] if len(p) > 2 else 'linear'}
            for p in pts]

def anim(l, **props):
    l.setdefault('keyframes', {})
    for p, pts in props.items():
        l['keyframes'][p] = k(pts)
    return l

def put(l, start=None, end=None):
    if start is not None: l['start'] = start
    if end is not None: l['end'] = end
    L.append(l); return l

# ---------- shared bits ----------
BLUE, GRAYBG, TXT2 = '#0b93f6', '#e9e9eb', '#8a8a8e'
scrW, scrH = 750, 1560

def chevron(x, y, s=26, color='#555555', sw=5, flip=False):
    d = f'M {x} {y} L {x + s * .55} {y + s / 2} L {x} {y + s}' if not flip else \
        f'M {x + s * .55} {y} L {x} {y + s / 2} L {x + s * .55} {y + s}'
    return node('path', d=d, fill='none', stroke=color, strokeWidth=sw,
                strokeLinecap='round')

def tail_bubble(x, y, w, h, fill, right=False):
    """Bubble body + little tail nub."""
    c = [rect(x, y, w, h, fill, min(38, h / 2 - 1))]
    if right:
        c.append(node('path', d=f'M {x + w - 24} {y + h - 14} Q {x + w + 12} {y + h + 4} '
                                f'{x + w + 2} {y + h - 26} Q {x + w - 8} {y + h - 8} {x + w - 24} {y + h - 14} Z', fill=fill))
    else:
        c.append(node('path', d=f'M {x + 24} {y + h - 14} Q {x - 12} {y + h + 4} '
                                f'{x - 2} {y + h - 26} Q {x + 8} {y + h - 8} {x + 24} {y + h - 14} Z', fill=fill))
    return c

def bubble(text_s, x, y, w, fs=40, right=False, fill=None, lines=None,
           color=None):
    """Returns group: bubble + wrapped text. lines = explicit line list."""
    color = color or ('#ffffff' if right else '#000000')
    lines = lines or [text_s]
    pad = 26
    h = pad * 2 + len(lines) * fs * 1.28 - fs * .28
    fill = fill or (BLUE if right else GRAYBG)
    ch = tail_bubble(x, y, w, h, fill, right)
    for i, ln in enumerate(lines):
        ch.append(text(x + pad, y + pad - 6 + i * fs * 1.28, ln, fs, color,
                       family='SF Pro Text', weight=400))
    g = grp(ch, 0, 0)
    g['_h'] = h
    return g

def pop(g, t0, dur=12, y0=None, scale0=.55):
    """iMessage-style arrival: rise + scale up + fade."""
    ky = y0 if y0 is not None else 80
    anim(g, y=[(t0 / FPS, g['y'] + ky), ((t0 + dur) / FPS, g['y'], 'easeOut')],
            opacity=[(t0 / FPS, 0), ((t0 + 4) / FPS, 1)],
            scaleX=[(t0 / FPS, scale0), ((t0 + dur) / FPS, 1, 'easeOut')],
            scaleY=[(t0 / FPS, scale0), ((t0 + dur) / FPS, 1, 'easeOut')])
    g['originX'] = .5; g['originY'] = 1
    return g

# ---------- PHONE ----------
bezel = rect(-14, -14, scrW + 28, scrH + 28, '#151517', 118)
screen = rect(0, 0, scrW, scrH, '#fcfcfc', 104)
island = rect(scrW / 2 - 105, 24, 210, 62, '#000000', 31)

def header(name, avatar_children, t0=0):
    ch = [grp([circle(28, 58, 64, '#f2f2f6'), chevron(46, 72, 28, '#4a4a4c', 6, flip=True),
               circle(66, 63, 44, '#8e8e93'), text(79, 70, '2', 30, '#ffffff', weight=600)]),
          grp([circle(658, 58, 64, '#f2f2f6'),
               node('path', d='M 678 78 L 704 78 Q 710 78 710 84 L 710 96 Q 710 102 704 102 '
                              'L 678 102 Q 672 102 672 96 L 672 84 Q 672 78 678 78 Z '
                              'M 710 85 L 724 76 L 724 104 L 710 95 Z', fill='#4a4a4c')]),
          grp([circle(0, 0, 96, '#f2f2f6')] + avatar_children, scrW / 2 - 48, 40)]
    name_t = text(0, 152, name, 40, weight=700)
    name_t['x'] = scrW / 2 - (len(name) * 21) / 2
    ch.append(name_t)
    ch.append(chevron(scrW / 2 + len(name) * 23 / 2 + 16, 158, 24, '#8e8e93', 6))
    ch.append(text(scrW / 2 - 95, 205, 'Today 9:41 AM', 27, TXT2))
    return grp(ch)

def composer():
    return grp([circle(24, 1460, 52, '#f2f2f6'), text(30, 1466, '+', 40, '#555555'),
                rect(92, 1452, 560, 66, '#fcfcfc', 33),
                rect(92, 1452, 560, 66, 'none', 33, stroke='#d4d4d8', strokeWidth=2),
                text(120, 1468, 'iMessage', 30, '#c7c7cc'),
                node('path', d='M 622 1478 a10 10 0 1 1 0.01 0 M 619 1486 l 6 -10 6 10 z',
                     fill='#c7c7cc')])

comp_a = composer()
comp = composer()

agent_hdr = header('Agent', [text(10, 16, '\U0001f916', 58)])
# Team Lunch: 4-memoji cluster avatar
team_hdr = header('Team Lunch', [
    text(-6, 2, '\U0001f9d1\U0001f3fe', 34), text(46, 2, '👱‍♀️', 34),
    text(-6, 48, '👩🏾‍🦱', 34), text(46, 48, '\U0001f916', 34)])

# ---------- AGENT transcript (screen-local) ----------
ag = [agent_hdr]
b1 = bubble('', 190, 320, 530, fs=34, right=True,
            lines=['Draft an email to Alice about', 'our dinner.'])
b1 = pop(b1, 98, 14, 140); ag.append(b1)
b2 = bubble('', 47, 480, 268, fs=34, lines=['Working on it.'])
b2 = pop(b2, 142, 12, 100); ag.append(b2)

# mail rich card
card = [rect(0, 0, 508, 268, '#ffffff', 44, shadow={'x': 0, 'y': 2, 'blur': 10, 'color': '#00000022'})]
card += [rect(0, 0, 508, 96, '#1189f2', 44),
         rect(0, 44, 508, 52, '#1189f2', 0),
         circle(24, 20, 54, '#ffffff'),
         node('path', d='M 36 52 L 66 34 L 66 70 Z', fill='#1189f2'),
         rect(22, 118, 462, 128, '#f2f2f7', 20),
         text(42, 130, 'To: Alice', 30, '#333333'),
         text(42, 168, 'Subject: ', 30, '#333333'),
         text(172, 168, 'Dinner this week', 30, '#333333'),
         text(42, 206, 'Hi Alice,', 26, '#666666'),
         text(260, 226, 'Mail', 30, '#000000', weight=600)]
card = grp(card, 47, 660)
card = pop(card, 176, 16, 160, .3); ag.append(card)

# sent + reply bubbles (after sheet closes); card morphs into "Sent."
card['end'] = 356 / FPS
b3 = bubble('', 47, 700, 130, fs=34, lines=['Sent.'])
b3 = pop(b3, 357, 10, 60); ag.append(b3)
b4 = bubble('', 47, 780, 500, fs=34, lines=["I'll let you know when she replies."])
b4 = pop(b4, 373, 12, 80); ag.append(b4)
ag.append(comp_a)

agent_chat = grp(ag)
anim(agent_chat, opacity=[(468 / FPS, 1), (488 / FPS, 0)])
agent_chat['end'] = 488 / FPS
put(agent_chat, 0, None)

# ---------- LUNCH transcript ----------
lu = [team_hdr, comp]
alabel = text(150, 300, 'Alice', 26, TXT2); lu.append(alabel)
b5 = bubble('', 100, 330, 560, fs=32, lines=['Can someone order lunch for us?'])
b5 = pop(b5, 478, 12, 90); lu.append(b5)
memA = grp([circle(0, 0, 72, '#f6e3d4'), text(12, 14, '👩🏾‍🦱', 44)], 20, 336)
memA = pop(memA, 478, 12, 90); lu.append(memA)
blabel = text(150, 452, 'Bob', 26, TXT2); lu.append(blabel)
b6 = bubble('', 100, 482, 330, fs=32, lines=['Vegetarian for me.'])
b6 = pop(b6, 493, 12, 80); lu.append(b6)
memB = grp([circle(0, 0, 72, '#d9e6f7'), text(12, 14, '\U0001f9d1\U0001f3fe', 44)], 20, 488)
memB = pop(memB, 493, 12, 80); lu.append(memB)
b7 = bubble('', 300, 605, 420, fs=32, right=True, lines=['Something light.'])
b7 = pop(b7, 509, 12, 90); lu.append(b7)
aglabel = text(150, 720, 'Agent', 26, TXT2); lu.append(aglabel)
b8 = bubble('', 100, 750, 560, fs=32,
            lines=["Taking everyone's preferences", 'into account, I found a few good', 'options.'])
b8 = pop(b8, 535, 12, 90); lu.append(b8)
memG = grp([circle(0, 0, 72, '#e6f4ea'), text(12, 14, '\U0001f916', 44)], 20, 810)
memG = pop(memG, 535, 12, 90); lu.append(memG)

# Uber Eats rich card
uc = [rect(0, 0, 508, 360, '#ffffff', 44, shadow={'x': 0, 'y': 2, 'blur': 10, 'color': '#00000022'})]
uc += [rect(0, 0, 508, 150, '#f6e8d8', 44), rect(0, 100, 508, 50, '#f6e8d8', 0),
       text(150, 30, '🍕  🍜  🥗', 60),
       text(24, 165, 'Lanespan Pizza & Pub', 34, weight=700),
       text(24, 205, '(Emeryville)', 34, weight=700),
       text(24, 250, '★ 4.8 (200+ ratings) • Pizza • $$', 24, '#333333'),
       text(24, 285, 'Open until 3:00 AM', 22, TXT2),
       text(24, 315, 'Tap for hours info and more', 22, TXT2),
       chevron(478, 240, 26, '#8e8e93', 6)]
uc += [rect(0, 360, 508, 74, '#f2f2f7', 0),
       node('path', d='M 30 400 Q 44 380 58 400 Q 44 420 30 400 Z', fill='#1189f2'),
       text(78, 385, 'Uber Eats', 32, weight=700),
       text(78, 420, 'Lanespan Pizza & Pub (Emeryville)', 22, TXT2)]
ucard = grp(uc, 100, 950)
ucard = pop(ucard, 546, 18, 200, .2); lu.append(ucard)

lunch_chat = grp(lu)
anim(lunch_chat, opacity=[(468 / FPS, 0), (488 / FPS, 1)])
lunch_chat['opacity'] = 0
put(lunch_chat, 0, None)

# typing indicator (Alice, before her message)
tip = grp([circle(0, 0, 72, '#f6e3d4'), text(12, 14, '👩🏾‍🦱', 44)], 20, 330)
tipb = grp(tail_bubble(100, 336, 150, 60, GRAYBG) +
           [circle(120, 358, 16, '#b9b9be'), circle(152, 358, 16, '#b9b9be'), circle(184, 358, 16, '#b9b9be')])
typing = grp([tip, tipb])
typing = pop(typing, 460, 8, 60, .7)
typing['start'] = 460 / FPS; typing['end'] = 478 / FPS

# ---------- MAIL EDITOR SHEET ----------
sh = [rect(0, 0, 710, 1500, '#ffffff', 46, shadow={'x': 0, 'y': -4, 'blur': 24, 'color': '#00000033'})]
sh += [rect(300, 12, 110, 12, '#d4d4d8', 6),
       grp([circle(0, 0, 68, '#f2f2f6'),
            node('path', d='M 22 22 L 46 46 M 46 22 L 22 46', stroke='#555555', strokeWidth=6,
                 fill='none', strokeLinecap='round')], 34, 60),
       grp([circle(0, 0, 68, BLUE),
            node('path', d='M 34 16 L 34 52 M 20 32 L 34 16 L 48 32', stroke='#ffffff',
                 strokeWidth=7, fill='none', strokeLinecap='round', strokeLinejoin='round')], 606, 60)]
sh += [text(34, 170, 'Dinner This Week', 52, weight=700, family='SF Pro Display')]
sh += [text(34, 260, 'To:', 30, TXT2), text(90, 260, 'Alice', 30, '#1a86e8'),
       rect(34, 300, 642, 2, '#ececf0'),
       text(34, 318, 'Cc/Bcc, ', 28, '#b9b9be'), text(196, 318, 'From: ryan@photon.codes', 28, '#b9b9be'),
       rect(34, 358, 642, 2, '#ececf0'),
       text(34, 374, 'Subject: ', 28, '#b9b9be'), text(166, 374, 'Dinner This Week', 28, '#000000'),
       rect(34, 412, 642, 2, '#ececf0')]
body = [text(34, 440, 'Hi Alice,', 30),
        text(34, 500, "Just wanted to check if we're still on", 30),
        text(34, 540, "for dinner this week. I'm free", 30),
        text(34, 580, "know what works best for you.", 30),
        text(34, 660, 'Looking forward to catching up.', 30),
        text(34, 740, 'Best,', 30),
        text(34, 820, 'Ryan', 30)]
sh += body
mail_sheet = grp(sh, 20, 60)
anim(mail_sheet, y=[(214 / FPS, 1300), (226 / FPS, 60, 'easeOut')])
mail_sheet['start'] = 214 / FPS; mail_sheet['end'] = 355 / FPS

# selection highlight + replacement text (typing)
sel = rect(196, 588, 320, 44, '#0b93f655', 6)
put(sel, 242 / FPS, 268 / FPS)
newphrase = text(196, 580, 'next weekend works', 30)
reveal = rect(196, 584, 330, 40, '#ffffff')
anim(reveal, x=[(270 / FPS, 196), (302 / FPS, 526)],
             width=[(270 / FPS, 330), (302 / FPS, 0)])
put(newphrase, 270 / FPS, 354 / FPS)
put(reveal, 270 / FPS, 303 / FPS)
oldline = body[2]
oldline['end'] = 268 / FPS  # selected phrase deleted

# ---------- FOOD SHEET ----------
fh = [rect(0, 0, 710, 1500, '#ffffff', 46, shadow={'x': 0, 'y': -4, 'blur': 24, 'color': '#00000033'})]
fh += [rect(300, 12, 110, 12, '#d4d4d8', 6),
       text(280, 30, 'Uber Eats', 36, weight=700),
       text(170, 74, 'Lanespan Pizza & Pub (Emeryville)', 24, TXT2),
       grp([circle(0, 0, 62, BLUE),
            node('path', d='M 18 32 L 28 44 L 46 20', stroke='#ffffff', strokeWidth=7,
                 fill='none', strokeLinecap='round', strokeLinejoin='round')], 616, 40),
       rect(30, 112, 650, 2, '#ececf0')]
rows_ = [('Grilled Chicken Rice Bowl', '$15.4', 'Chicken, rice, broccoli,', 'sesame sauce', '🍗', '👩🏾‍🦱'),
         ('Roasted Veggie Grain Bowl', '$13.2', 'Quinoa, roasted vegetables,', 'chickpeas', '🥗', '\U0001f9d1\U0001f3fe'),
         ('Chicken Caesar Salad', '$17.9', 'Chicken, romaine, parmesan,', 'Caesar dressing', '🥗', '👱‍♀️'),
         ('Turkey Avocado Wrap', '$19.3', 'Turkey, avocado, lettuce,', 'tomato', '🌯', '\U0001f9d1\U0001f3fe'),
         ('Falafel Pita Pocket', '$16.1', 'Falafel, hummus, cucumber,', 'tzatziki', '🥙', '👩🏾‍🦱'),
         ('Simple Shrimp & Side Salad', '$17.2', 'Shrimp, greens, lemon,', 'olive oil', '🍤', '👱‍♀️')]
for i, (nm, pr, d1, d2, em, mem) in enumerate(rows_):
    yy = 140 + i * 205
    fh += [text(34, yy, nm, 34, weight=700),
           text(34, yy + 40, pr, 30),
           text(34, yy + 84, d1, 26, '#9a9a9e'),
           text(34, yy + 114, d2, 26, '#9a9a9e'),
           grp([rect(0, 0, 128, 128, '#efe6dc', 26), text(28, 32, em, 64)], 548, yy),
           grp([circle(0, 0, 52, '#ffe9ee'), text(8, 10, mem, 34),
                circle(38, 38, 26, '#ffffff'), text(44, 38, '+', 30, '#555555')], 486, yy + 60),
           rect(30, yy + 168, 650, 2, '#ececf0')]
food_sheet = grp(fh, 20, 60)
anim(food_sheet, y=[(618 / FPS, 1300), (632 / FPS, 60, 'easeOut')])
food_sheet['start'] = 618 / FPS; food_sheet['end'] = 744 / FPS
# floating cart + badge (screen-local, floats right of sheet)
cart = grp([circle(0, 0, 80, '#f2f2f6', shadow={'x': 0, 'y': 2, 'blur': 8, 'color': '#00000033'}),
            text(18, 18, '\U0001f6d2', 44)], 640, 640)
cart['start'] = 668 / FPS; cart['end'] = 735 / FPS
badges = []
for f_, n_ in [(674, '1'), (682, '2'), (711, '3')]:
    b = grp([circle(0, 0, 34, '#e23b3b'), text(11, 6, n_, 22, '#ffffff', weight=700)], 686, 626)
    b['start'] = f_ / FPS; b['end'] = (f_ + 60) / FPS
    badges.append(b)

# ---------- WORLD RELEASE ----------
wr = []
foods = [('\U0001f355', -0.5), ('\U0001f355', -0.3), ('🍜', -0.1), ('\U0001f355', 0.15),
         ('🥗', 0.4), ('\U0001f355', 0.6), ('🍜', 0.8), ('\U0001f355', 1.0),
         ('🍜', 1.2), ('\U0001f355', 1.35)]
# canvas-space flying food: from phone center out to ring positions
ring = [(140, 60), (620, 90), (1560, 40), (1790, 200), (240, 330), (1500, 420),
        (90, 700), (700, 760), (1620, 740), (1850, 950)]
for i, (em, frac) in enumerate(foods):
    tx, ty = ring[i % len(ring)]
    f_ = text(tx, ty, em, 90)
    f_['rotation'] = (i * 47) % 60 - 30
    anim(f_, x=[(730 / FPS, 960), (750 / FPS, tx, 'easeOut')],
             y=[(730 / FPS, 640), (755 / FPS, ty, 'easeOut')],
             opacity=[(728 / FPS, 0), (734 / FPS, 1), (820 / FPS, 1), (838 / FPS, 0)])
    put(f_, 728 / FPS, 840 / FPS)
orders = [(300, 950), (450, 505), (1600, 300), (1700, 620), (1560, 0), (120, 90)]
for i, (ox, oy) in enumerate(orders):
    ob = bubble('', ox, oy, 150, 30, lines=['Order!'], fill='#f2f2f6', color='#000000')
    anim(ob, scaleX=[((742 + i * 8) / FPS, 0), ((752 + i * 8) / FPS, 1, 'easeOut')],
             scaleY=[((742 + i * 8) / FPS, 0), ((752 + i * 8) / FPS, 1, 'easeOut')],
             opacity=[((742 + i * 8) / FPS, 0), ((746 + i * 8) / FPS, 1),
                      (815 / FPS, 1), (830 / FPS, 0)])
    ob['originX'] = .5; ob['originY'] = 1
    put(ob, (742 + i * 8) / FPS, 832 / FPS)

# ---------- PHONE SCREENS: jump jump / health / dark card ----------
jj = grp([rect(0, 0, scrW, scrH, '#e8e8ef'),
          text(300, 110, 'Jump Jump', 34, weight=600),
          text(360, 170, '4', 60, weight=700),
          rect(180, 700, 200, 90, '#9a9aa2', 12), rect(60, 850, 220, 90, '#3a3a3e', 12),
          rect(430, 880, 220, 90, '#3a3a3e', 12), rect(560, 560, 200, 90, '#7ed321', 12),
          circle(315, 640, 40, '#6b4fa1'), rect(300, 660, 70, 46, '#6b4fa1', 10),
          circle(560, 800, 16, '#8e8e93')])
jj['start'] = 800 / FPS; jj['end'] = 852 / FPS
health = grp([rect(0, 0, scrW, scrH, '#fcfcfc'),
              text(80, 120, "Today's Health", 40, weight=700),
              circle(120, 200, 300, 'none', stroke='#f3d2d8', strokeWidth=30),
              node('path', d='M 270 200 A 150 150 0 0 1 380 300', fill='none', stroke='#f25e7a', strokeWidth=30),
              text(215, 280, '92', 72, weight=700),
              rect(80, 560, 590, 120, '#f2f2f6', 24), text(110, 590, '7,410 steps', 34),
              rect(80, 700, 590, 120, '#f2f2f6', 24), text(110, 730, 'Mindful 10m', 34)])
health['start'] = 852 / FPS; health['end'] = 872 / FPS
darkcard = grp([rect(0, 0, scrW, scrH, '#121216'),
                rect(60, 140, 630, 400, '#1e1e24', 30), text(90, 160, '🗺️', 120),
                text(90, 580, '$12.29', 44, '#ffffff', weight=700),
                text(90, 640, 'Your ride is arriving', 26, '#9a9aa0')])
darkcard['start'] = 872 / FPS; darkcard['end'] = 892 / FPS
for g_ in (jj, health, darkcard):
    g_['x'] = 0; g_['y'] = 0

# ---------- PHONE GROUP + camera ----------
phone = grp([bezel, screen, island,
             grp([agent_chat, lunch_chat, typing, jj, health, darkcard,
                  mail_sheet, food_sheet, cart] + badges,
                 clip={'x': 0, 'y': 0, 'width': scrW, 'height': scrH})])
phone['keyframes'] = {
 'scaleX': k([(0, .99), (78 / FPS, .99), (176 / FPS, 1.62), (205 / FPS, 1.62),
              (228 / FPS, 1.0), (357 / FPS, 1.0), (430 / FPS, 1.28), (560 / FPS, 1.28),
              (632 / FPS, .92), (730 / FPS, .92), (800 / FPS, .58), (895 / FPS, .58)]),
 'scaleY': k([(0, .99), (78 / FPS, .99), (176 / FPS, 1.62), (205 / FPS, 1.62),
              (228 / FPS, 1.0), (357 / FPS, 1.0), (430 / FPS, 1.28), (560 / FPS, 1.28),
              (632 / FPS, .92), (730 / FPS, .92), (800 / FPS, .58), (895 / FPS, .58)]),
 'x': k([(0, 196), (176 / FPS, 96), (228 / FPS, 178), (430 / FPS, 0), (632 / FPS, 255),
         (800 / FPS, 460), (895 / FPS, 460)]),
 'y': k([(0, 40), (59 / FPS, 40), (78 / FPS, 62), (176 / FPS, -40), (228 / FPS, 30),
         (430 / FPS, 10), (632 / FPS, 40), (800 / FPS, 62), (880 / FPS, 62),
         (900 / FPS, 400, 'easeIn'), (910 / FPS, 1300)]),
}
phone['originX'] = .5; phone['originY'] = 0
put(phone)

# ---------- canvas-space title / big title / mosaic / taglines / end ----------
# Title card
title = grp([text(560, 420, 'Introducing API for', 72, weight=700, family='SF Pro Display'),
             grp([rect(0, 8, 84, 84, '#4a90e2', 20), text(18, 22, '⬚', 48, '#ffffff')], 470, 540),
             text(575, 548, 'Mini Apps in', 72, weight=700, family='SF Pro Display'),
             grp([rect(0, 8, 84, 84, '#5fc653', 20), text(16, 20, '💬', 44)], 1180, 540),
             text(1285, 548, 'iMessage', 72, weight=700, family='SF Pro Display')])
anim(title, opacity=[(0, 0), (8 / FPS, 1), (52 / FPS, 1), (60 / FPS, 0)])
put(title, 0, 60 / FPS)

# Team Lunch big title (canvas space)
bt = grp([grp([text(-6, 2, '\U0001f9d1\U0001f3fe', 60), text(60, 2, '👱‍♀️', 60),
               text(-6, 60, '👩🏾‍🦱', 60), text(60, 60, '\U0001f916', 60),
               circle(0, 0, 130, '#f2f2f6')], 850, 330),
          text(760, 480, 'Team Lunch', 76, weight=700, family='SF Pro Display'),
          chevron(1230, 500, 40, '#8e8e93', 8)])
# cluster circle behind emoji
bt['children'][0]['children'].insert(0, circle(-15, -15, 160, '#f2f2f6'))
anim(bt, opacity=[(400 / FPS, 0), (415 / FPS, 1), (462 / FPS, 1), (475 / FPS, 0)],
         scaleX=[(400 / FPS, .7), (420 / FPS, 1, 'easeOut')],
         scaleY=[(400 / FPS, .7), (420 / FPS, 1, 'easeOut')])
bt['originX'] = .5; bt['originY'] = .5
put(bt, 400 / FPS, 475 / FPS)

# Zoom meeting notification card
zm = grp([rect(0, 0, 640, 190, '#ffffff', 40, shadow={'x': 0, 'y': 6, 'blur': 30, 'color': '#0000002e'}),
          text(56, 30, 'Zoom Meeting', 62, weight=700, family='SF Pro Display'),
          text(56, 108, 'Join in 5 minutes', 48, '#8a8a8e')])
anim(zm, x=[(880 / FPS, 1960), (896 / FPS, 1240, 'easeOut')],
         opacity=[(945 / FPS, 1), (958 / FPS, 0)])
put(zm, 880 / FPS, 960 / FPS)

# mosaic of mini-app cards
apps = [('📦', 'Amazon Package', 'Arriving today'), ('☕', 'Blue Bottle', 'Order ready'),
        ('🍬', 'Candy Saga', 'Level 12'), ('✈️', 'Delta Airlines', 'Boarding 8:40'),
        ('🛒', 'Walmart Cart', '$16.59 · 6 items'), ('💻', 'Coding Agent', 'Task complete'),
        ('🌮', 'Taco Truck', 'Pickup 12:30'), ('🚗', 'Uber Ride', 'Driver 3 min'),
        ('📈', 'Stock Alert', 'AAPL +2.4%'), ('🎵', 'Setlist', 'Show tonight'),
        ('🏨', 'Hotel Check-in', 'Room 804'), ('🗳️', 'Poll', '4 votes'),
        ('📊', 'Dashboard', 'Weekly KPIs'), ('🍷', 'Wine Club', 'New shipment'),
        ('🧾', 'Receipt', '$42.10'), ('🎮', 'Puzzle Duel', 'Your turn'),
        ('🏦', 'Bank', 'Deposit $500'), ('📅', 'Calendar', 'Dinner Fri'),
        ('🧘', 'Mindfulness', 'Day 30'), ('📰', 'News Brief', '5 stories')]
mos = []
for i, (ic, t1, t2) in enumerate(apps):
    col = i % 5; row = i // 5
    cx = 130 + col * 345; cy = 210 + row * 195
    card_ = grp([rect(0, 0, 315, 165, '#ffffff', 26,
                      shadow={'x': 0, 'y': 4, 'blur': 16, 'color': '#00000024'}),
                 grp([rect(0, 0, 74, 74, '#f2f2f6', 18), text(12, 12, ic, 48)], 24, 20),
                 text(24, 108, t1, 28, weight=600),
                 text(180, 108, '', 1),
                 text(24, 140, t2, 22, TXT2)], cx, cy)
    d0 = 905 + (i * 37) % 50
    anim(card_, y=[(d0 / FPS, cy + 260), ((d0 + 22) / FPS, cy, 'easeOut')],
                opacity=[(d0 / FPS, 0), ((d0 + 10) / FPS, 1), (960 / FPS, 1), (980 / FPS, 0)],
                scaleX=[(d0 / FPS, .7), ((d0 + 22) / FPS, 1, 'easeOut')],
                scaleY=[(d0 / FPS, .7), ((d0 + 22) / FPS, 1, 'easeOut')])
    put(card_, d0 / FPS, 985 / FPS)

# taglines: "Now your agent can send" + cycling icon+label
tags = [('agentic apps', '#f2627b', '⬒'), ('generative UIs', '#f2b23f', '⬒'),
        ('games', '#64b5f6', '🎮'), ('sign-in requests', '#7ed321', '🔑'),
        ('live screen sharing', '#63cdda', '📺'), ('live delivery tracking', '#f2a03f', '📦'),
        ('menus', '#f2627b', '🍽️'), ('dashboards', '#8e8e93', '📊'),
        ('mini apps', '#f2b23f', '📱')]
tl = text(560, 470, 'Now your agent can send', 62, weight=700, family='SF Pro Display')
put(tl, 985 / FPS, 1150 / FPS)
tl0 = tl
for i, (lab, colr, ic) in enumerate(tags):
    t0, t1 = (985 + i * 17) / FPS, (985 + (i + 1) * 17) / FPS
    g_ = grp([rect(0, 0, 74, 74, colr, 20), text(12, 12, ic, 46)], 1290, 462)
    lbl = text(1380, 472, lab, 62, weight=700, family='SF Pro Display')
    gg = grp([g_, lbl])
    anim(gg, opacity=[(t0, 0), (t0 + 5 / FPS, 1), (t1 - 4 / FPS, 1), (t1, 0)])
    put(gg, t0, t1)
anim(tl0, x=[(985 / FPS, 560), (1000 / FPS, 300), (1140 / FPS, 300), (1150 / FPS, 80)])

# end cards
end1 = grp([text(560, 490, 'Available today at ', 58, weight=700, family='SF Pro Display'),
            text(1058, 490, 'tryphoton.ai', 58, '#7aa8c7', weight=700, family='SF Pro Display')])
anim(end1, opacity=[(1130 / FPS, 0), (1140 / FPS, 1), (1180 / FPS, 1), (1188 / FPS, 0)])
put(end1, 1130 / FPS, 1190 / FPS)
end2 = grp([node('path', d='M 830 480 L 880 480 L 850 545 L 900 545 L 800 660 L 830 565 L 785 565 Z',
                 fill='#000000'),
            text(930, 480, 'Photon', 84, weight=700, family='SF Pro Display')])
anim(end2, opacity=[(1190 / FPS, 0), (1200 / FPS, 1), (1245 / FPS, 1), (1258 / FPS, 0)])
put(end2, 1190 / FPS, 1259 / FPS)

scene = {
 'title': '03-photon-mini independent recreation',
 'width': W, 'height': H, 'fps': FPS, 'duration': DUR,
 'background': '#fcfcfc',
 'source': {'path': 'source.mp4', 'sourceStart': 0, 'sourceEnd': DUR,
            'notes': 'Recreated from source.mp4 measurement only; no source pixels used. '
                     'Artwork = native geometry + Apple Color Emoji glyphs.'},
 'fonts': [{'family': f, 'src': f'assets/{f.replace(" ", "-")}-{w}.woff', 'weight': w}
           for f in ('SF Pro Text', 'SF Pro Display') for w in (400, 500, 600, 700)],
 'layers': L}
json.dump(scene, open('scene/scene.json', 'w'))
print('layers:', len(L), '->', 'scene/scene.json')
