"""Freeze frame-inspected actions on the director's unmodified first export."""
import json
from pathlib import Path
import sys
from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parent
sys.path.insert(0,str(ROOT/'tools'))
from check_cues import PACKET_HASH_METHOD, packet_hash
import hashlib

picture=BASE/'v1-first-export.mp4'
events=[]


def cue(frame,kind,note,peak=None):
    event={'frame':frame,'kind':kind,'time':frame/30,'sample_offset_48000':frame*1600,
           'event_id':f'checkin:{kind}:{frame}','evidence':f'evidence/frame-{frame:03}.png','observation':note}
    if peak is not None:
        event['audio']={'target_peak_dbfs':peak}
    if kind in {'typing','delete'}:
        event['role']='human'; event['delta_count']=1
    events.append(event)


cue(13,'message_arrival','First faint Sam ask fade at13, blank12; clearly legible14. Impact uses visible fade onset.',-18)
cue(103,'panel_open','Plus tap at90 is offscreen. Composer/ring is camera-revealed97–99; actual menu begins rising103. Sound menu movement, not inferred tap.',-26)
cue(132,'tap','Check In row highlights and tap ring appears132; no highlight131.',-21)
cue(145,'control_appear','First draft-card edge at bottom145;140 is empty composer and old ring. Mere appearance stays silent.')
cue(186,'message_send','Visible send-button ring186, absent185; one combined send accent, not tap plus send or backspace.',-17)
cue(435,'control_appear','First card sliver camera-revealed435;432 shows phone edge only. Existing card is not a new receipt; silent.')
for f,text in [(445,'a'),(451,'ar'),(457,'are'),(469,'are y'),(474,'are yo'),(480,'are you'),(492,'are you h')]:
    cue(f,'typing',f'Visible glyph change to {text!r}; one observed glyph accent.',-24)
cue(505,'control_appear','Location marker is over home around504–505 and clock changes505; no UI confirmation yet. Avoid duplicate arrival accent.')
cue(510,'cart_update','Both cards turn green Arrived and moving marker disappears510; one shared confirmation tick, no duplicated phone hits.',-19)
for f,text in [(522,'are you'),(529,'are yo'),(532,'are y'),(535,'are'),(542,'ar'),(545,'a'),(548,'iMessage placeholder')]:
    cue(f,'delete',f'Visible composer deletion to {text!r}; not inferred physical-key timing.',-25)
cue(575,'message_send','Heart bubble first appears at right composer edge575 and send ring; one send accent.',-17)
cue(590,'message_arrival','Heart bubble first appears at first-phone composer edge590; absent589.',-18)
events.sort(key=lambda e:e['frame'])
excluded=[{'frames':[90],'reason':'Plus tap itself offscreen; menu movement103 is sounded instead.'},
          {'frames':[432],'reason':'Existing card arrives via camera, not a visible new incoming bubble.'},
          {'frames':[463,486],'reason':'Trailing spaces produce no visible glyph/caret change; do not infer keyboard sounds.'},
          {'frames':[525,538],'reason':'Deleting trailing spaces produces no visible glyph/caret change.'},
          {'range_inclusive':[210,419],'reason':'No UI event. Location/camera motion only; optional declared motion texture is separate from UI.'},
          {'frames':[145,435,505],'reason':'Silent visual states retained as control_appear receipts.'}]
schedule={'schema':'message-motion-ui-events/1','id':'checkin','frames':720,'fps_numerator':30,'fps_denominator':1,
          'sample_count':1152000,'duration':24.,'scheduling_picture':'director first export; zero-based native frames',
          'picture_file_sha256':hashlib.sha256(picture.read_bytes()).hexdigest(),
          'picture_file_hash_method':'SHA-256 of all original MP4 file bytes including container; not video packets or decoded frames',
          'picture_packet_sha256':packet_hash(picture),'picture_packet_hash_method':PACKET_HASH_METHOD,
          'events':events,'exclusions':excluded,'reference_audio_samples_used':False,
          'hardware_keypress_timing_claimed':False,'one_key_per_visible_batch':True,
          'verification_notes':'Native before/at/after crops visually inspected. Invisible spaces omitted; animation starts and camera reveals distinguished.'}
path=ROOT/'audio-recreation/ui-cues/canonical-checkin.json'
path.write_text(json.dumps(schedule,indent=2)+'\n')
(BASE/'canonical-cues.json').write_text(json.dumps(schedule,indent=2)+'\n')
frames=[12,13,14,90,98,103,131,132,140,145,155,186,210,270,330,390,432,435,445,492,505,510,522,548,575,590,610,719]
sheet=Image.new('RGB',(1920,7*294),'#222222');draw=ImageDraw.Draw(sheet)
for i,f in enumerate(frames):
    x,y=i%4*480,i//4*294
    sheet.paste(Image.open(BASE/'evidence'/f'frame-{f:03}.png').resize((480,270)),(x,y))
    draw.text((x+6,y+274),f'frame {f} / {f/30:.3f}s',fill='white')
sheet.save(BASE/'evidence/contact-sheet-verified.png')
print(json.dumps({'events':len(events),'audible':sum(e['kind']!='control_appear' for e in events),'silent':sum(e['kind']=='control_appear' for e in events),'picture_packet_sha256':schedule['picture_packet_sha256']},indent=2))
