#!/usr/bin/env python3
"""Build visual-state-derived UI cue events, never from audio or title letter motion."""
from pathlib import Path
import hashlib,json,math
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent

def sha(path):
 digest=hashlib.sha256()
 with path.open('rb') as stream:
  for block in iter(lambda:stream.read(1024*1024),b''):
   digest.update(block)
 return digest.hexdigest()

def event(frame,kind,group,confidence,evidence,**extra):
 return {'frame':frame,'time':round(frame/30,9),'kind':kind,'group':group,'confidence':confidence,'evidence_layer_or_source':evidence,**extra}

def evidence(ids,source_frames,helper=None):
 value={'canonical_layer_ids':ids,'source':'references/02-danieltian/source.mp4','native_source_frames':source_frames}
 if helper:value['source_owner_helper']=helper
 return value

inventory01=json.loads((OUT/'01-scene-ui-inventory.json').read_text())
press=json.loads((ROOT/'references/01-photonhq/intro-review-elements.json').read_text())['measurements']['pill-press-weights']
first_press=next(item['frame']for item in press if item['weight']>.5)
assert first_press==70
one={
 'id':'01-photonhq','fps':30,'frames':655,'duration':655/30,'frame_numbering':'Zero-based native frames; time=frame/30.',
 'canonical_scene':inventory01['canonical_scene'],'canonical_scene_sha256':inventory01['canonical_scene_sha256'],
 'events':[event(70,'tap','blue-pill',.99,{'canonical_layer_ids':['group-6-source-pill','intro-pill-pressed','group-8-source-cursor'],'source':'references/01-photonhq/source.mp4','native_source_frames':[69,70,71,72,73],'source_owner_helper':'references/01-photonhq/refine-intro-cursor-press.py','measurement_file':'references/01-photonhq/intro-review-elements.json','measurement_key':'measurements.pill-press-weights'},observed_or_inferred='observed_cursor_press_state',description='Cursor rests on the blue pill; pressed-state blend jumps 0 at 69 to 0.954 at 70, with deepest press at 73. One click cue at first pressed frame; no second click on release.',gesture_visible=True)],
 'typing_events':0,'delete_events':0,
 'excluded_visuals':['Intro Photon2.0 title letter reveal is promotional title animation, not human typing.','With just one click words are promotional title animation.','SMS/email/call/iMessage/WhatsApp/Telegram wall motion is background promotional montage, not individual user sends or arrivals.','Final URL/logo presentation has no observed pointer tap or human typing.'],
 'evidence_files':[{'path':'audio-recreation/ui-cues/01-source-ui-contact.jpg','sha256':sha(OUT/'01-source-ui-contact.jpg')},{'path':'references/01-photonhq/intro-review-elements.json','sha256':sha(ROOT/'references/01-photonhq/intro-review-elements.json')}],
 'policy':'Only direct UI action evidence is cued. No original audio or music-transient timing is used.'
}
(OUT/'01-events.json').write_text(json.dumps(one,indent=2)+'\n')

# Each entry is a manually checked native visible prefix, cross-checked with OCR.
# Layout line wrapping is normalized to a space, never asserted as a Return key.
prefixes=[
 (105,'m'),(107,'mu'),(108,'mus'),(109,'muse'),(110,'muse,'),
 (112,'muse, m'),(113,'muse, my'),(114,'muse, my bo'),(115,'muse, my boss'),
 (116,'muse, my boss w'),(117,'muse, my boss wants'),(118,'muse, my boss wants a t'),
 (119,'muse, my boss wants a team'),(120,'muse, my boss wants a team offs'),
 (121,'muse, my boss wants a team offsit'),(122,'muse, my boss wants a team offsite'),
 (123,'muse, my boss wants a team offsite t'),(124,'muse, my boss wants a team offsite tm'),
 (125,'muse, my boss wants a team offsite tmr'),(127,'muse, my boss wants a team offsite tmr.'),
 (143,'muse, my boss wants a team offsite tmr. '),
 (145,'muse, my boss wants a team offsite tmr. c'),
 (146,'muse, my boss wants a team offsite tmr. ca'),
 (148,'muse, my boss wants a team offsite tmr. can'),
 (149,'muse, my boss wants a team offsite tmr. can '),
 (150,'muse, my boss wants a team offsite tmr. can u'),
 (152,'muse, my boss wants a team offsite tmr. can u '),
 (153,'muse, my boss wants a team offsite tmr. can u h'),
 (154,'muse, my boss wants a team offsite tmr. can u he'),
 (156,'muse, my boss wants a team offsite tmr. can u hel'),
 (157,'muse, my boss wants a team offsite tmr. can u help'),
 (159,'muse, my boss wants a team offsite tmr. can u help?'),
]
ocr={row['frame']:row for row in json.loads((OUT/'02-composer-ocr.json').read_text())['records']}
typing=[];previous='';previous_frame=104
for frame,text in prefixes:
 assert text.startswith(previous)
 delta=text[len(previous):]
 kind='typing' if len(delta)==1 else 'typing_burst'
 inferred_space=delta.count(' ')
 observation='observed_single_character_display_change' if kind=='typing' else 'observed_multi_character_display_change; internal_keystroke_times_not_visible'
 note='Visible glyph change, checked on the native composer contact and OCR.'
 confidence=.98
 if frame in [143,149,152]:
  observation='observed_caret_advance; space_character_identity_inferred_from_draft_context'
  note={143:'Caret x 440–446 at 142 advances to 453–458 at 143 while glyph copy is unchanged.',149:'Caret x 563–568 at 148 advances to 579–584 at 149 while glyph copy is unchanged.',152:'Caret x 617–622 at 151 advances to 633–638 at 152 while glyph copy is unchanged.'}[frame]
  confidence=.95
 elif inferred_space:
  note+=' Interword whitespace is inferred from the readable prefix; a separate space-key timestamp is not claimed.'
 if frame==123:note+=' The visual line wrap is layout, not an asserted Return key.'
 typing.append(event(frame,kind,'human-composer',confidence,evidence([f'root-copy-pose-{frame}',f'root-copy-black-{frame}-contour0'],[previous_frame,frame],'references/02-danieltian/refine-copy-root.py'),character_or_delta=delta,delta_count=len(delta),text_before=previous,text_after=text,observed_or_inferred=observation,individual_character_display_frame_observed=(kind=='typing' and frame not in [143,149,152]),individual_hardware_keystroke_times_observed=False,inferred_space_count=inferred_space,display_change_frame=frame,previous_display_change_frame=previous_frame,evidence_note=note,ocr_raw=ocr[frame]['ocr_raw']))
 previous=text;previous_frame=frame
assert len(typing)==32 and sum(item['delta_count']for item in typing)==51

arrivals=[
 (640,'kickoff','hey team, @Justina needs a Photon team offsite. Tomorrow.'),
 (667,'airbnb-command','@Airbnb find a place in Tahoe for 9'),
 (677,'lyft-command','@Lyft 2 XL rides from 880 Harrison St, 9am tomorrow'),
 (702,'resy-command','@Resy find a sushi spot. The team loves sushi'),
 (734,'budget','Budget?'),
 (866,'how-about','How about this one?'),
 (952,'airbnb-booked','Booked✅'),
 (972,'lyft-booked','2 XLs booked. Photon HQ→Airbnb in Tahoe, 9am✅'),
 (999,'resy-booked','Sushi for 9, booked🍣'),
]
messages=[]
for frame,name,copy in arrivals:
 messages.append(event(frame,'message_arrival',name,.95,evidence([f'middle-message-{name}',f'middle-glyphs-{name}'],[frame-1,frame],'references/02-danieltian/refine-v11-middle-checkpoint.py'),observed_or_inferred='observed_incoming_bubble_birth_in_canonical; source_presentation_cross_checked',text=copy,description='First canonical visible message frame; the spring growth/scroll continuation is one arrival, not repeated cues.'))
messages.append(event(840,'message_arrival','airbnb-rich-link',.98,evidence(['v11-card-local-pose-840','post-v14-soft-card-840'],[839,840,841],'references/02-danieltian/final-midstate-fix/elements-final.json'),observed_or_inferred='observed_rich_message_artwork_birth',description='First blurred/growing cabin rich-link panel replaces Airbnb typing indicator; one arrival at first visual birth, not at its settled frame 855.'))
sends=[
 event(175,'message_send','initial-offsite-request',.99,evidence(['root-send-flight-pose-175','root-send-flight-glyphs-175','root-send-flight-control-175'],[174,175,176],'references/02-danieltian/apply-root-send-flight.py'),observed_or_inferred='observed_composer_to_outgoing_bubble_transition; tap_gesture_inferred',text=previous,description='Filled composer becomes a blue outgoing message and begins its flight. Do not treat composer clearing as backspace/delete.'),
 event(770,'message_send','budget-reply',.99,evidence(['middle-message-budget-reply','post-v14-interior-copy-budget-reply'],[769,770,771],'references/02-danieltian/final-midstate-fix/elements-final.json'),observed_or_inferred='observed_outgoing_payload_reveal; send_action_inferred',text='~$100 per person',description='Literal reply hard-reveals at 770 after a blue three-dot presentation. No human composer or individual keys are shown for this reply.',typing_indicator_birth_frame=754),
 event(920,'message_send','love-it',.99,evidence(['middle-message-love-it','post-v14-interior-copy-love-it'],[919,920,921],'references/02-danieltian/final-midstate-fix/elements-final.json'),observed_or_inferred='observed_outgoing_payload_reveal; send_action_inferred',text='Love it',description='Literal reply hard-reveals at 920 after a blue three-dot presentation. No human composer or individual keys are shown for this reply.',typing_indicator_birth_frame=901),
]
optional=[]
for frame,name,bounds in [(509,'airbnb-agent-selection',[1192,550,1206,564]),(517,'lyft-agent-selection',[1156,460,1170,474]),(519,'resy-agent-selection',[1192,768,1206,782])]:
 optional.append(event(frame,'tap',name,.9,evidence(['pb-capsule-'+name.split('-')[0]],[frame-1,frame],'references/02-danieltian/phonebook-v14/elements-candidate.json'),observed_or_inferred='observed_green_check_birth; human_tap_inferred_and_not_visible',gesture_visible=False,visual_state_confidence=.96,user_gesture_confidence=.3,description='Optional soft selection/confirmation cue for a visible green-check birth. This may be an automated selection, so it is not evidence of an actual finger/pointer tap.',native_green_seed_bounds=bounds,optional=True))
inventory02=json.loads((OUT/'02-scene-ui-inventory.json').read_text())
ordered=sorted(typing+sends+messages,key=lambda item:(item['frame'],item['kind']))
two={
 'id':'02-danieltian','fps':30,'frames':1360,'duration':1360/30,'frame_numbering':'Zero-based native frames; time=frame/30.',
 'canonical_scene':inventory02['canonical_scene'],'canonical_scene_sha256':inventory02['canonical_scene_sha256'],
 'events':ordered,'optional_events':optional,
 'typing_summary':{'first_frame':105,'last_frame':159,'display_change_events':32,'single_change_events':sum(e['kind']=='typing'for e in typing),'multi_character_burst_events':sum(e['kind']=='typing_burst'for e in typing),'normalized_character_count':51,'final_text':previous,'text_pause_native_frames':[128,142],'text_pause_note':'No character change 128–142. Caret disappears/reappears during the hold and is not a delete or typing action.','trailing_space_caret_advances':[143,149,152],'normalization':'Automatic visual line wrap is represented as interword whitespace; no Return key is asserted. Some spaces bundled with visible letters cannot be assigned a separate precise hardware key time.','method':'All 85 native 90–174 source frames were observed with thresholded OCR plus manual native-contact verification. Older interpolated composer-v5 schedule was not used as ground truth.'},
 'delete_events':0,
 'excluded_visuals':['Intro/CTA/title letter reveals are presentation text, not typing.','AI reasoning text and Searching the Agent Phone Book query are automated output, not human composer/search input.','Gray and blue three-dot typing indicators are status animations, not observed per-character typing.','The initial sent bubble carried into the phone view is the same send, not a second message.','Message spring/scroll/settle frames do not create additional message arrivals.','Composer clearing on send 175 is not backspacing.','Reaction/emoji decorations without a demonstrated input gesture are not asserted as taps.'],
 'evidence_files':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)}for p in [OUT/'02-composer-ocr.json',OUT/'02-composer-native-0.jpg',OUT/'02-composer-native-1.jpg',OUT/'02-source-ui-contact.jpg',OUT/'02-phonebook-check-observations.json',ROOT/'references/02-danieltian/final-midstate-fix/elements-final.json',ROOT/'references/02-danieltian/refine-copy-root.py']],
 'policy':'Human composer display changes only; no source audio/music transients used. Frame timestamps describe visible motion-graphic state, not physical keyboard hardware telemetry. Optional check cues explicitly retain the inferred-gesture qualification.'
}
(OUT/'02-events.json').write_text(json.dumps(two,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'01_events':len(one['events']),'02_events':len(ordered),'02_typing':len(typing),'02_send':len(sends),'02_arrival':len(messages),'02_optional_check_confirmations':len(optional)},indent=2))
