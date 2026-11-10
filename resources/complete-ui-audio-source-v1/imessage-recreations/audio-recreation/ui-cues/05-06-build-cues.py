"""Derive visual UI cues only for accepted Linq05/Rene06. Never inspect audio.

Writes only the owned05-/06- cue files. Canonical scenes and media stay read-only.
"""
from pathlib import Path
import json,hashlib,csv,math

R=Path(__file__).resolve().parents[2]
D=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
P05=R/'outputs/05-linq/final-v20/scene.json'
P06=R/'outputs/06-gallery/final-v23/scene.json'
before={str(p):sha(p)for p in [P05,P06]}
S05=json.loads(P05.read_text());S06=json.loads(P06.read_text())

def inventory(scene):
 out={}
 def walk(n,parents,pointer):
  assert n['id']not in out,n['id']
  out[n['id']]={'node':n,'parents':parents,'pointer':pointer}
  for i,c in enumerate(n.get('children',[])):walk(c,parents+[n],pointer+f'/children/{i}')
 for i,n in enumerate(scene['layers']):walk(n,[],f'/layers/{i}')
 return out
I05=inventory(S05);I06=inventory(S06)
def interp(n,key,t):
 values=n.get('keyframes',{}).get(key,[])
 if not values:return n.get(key,1 if key=='opacity'else 0)
 if t<=values[0]['t']+1e-10:return values[0]['value']
 for a,b in zip(values,values[1:]):
  if t<=b['t']+1e-10:
   if b.get('ease')=='hold':return a['value']if t<b['t']-1e-10 else b['value']
   u=(t-a['t'])/max(1e-10,b['t']-a['t']);return a['value']+(b['value']-a['value'])*u
 return values[-1]['value']
def onset(I,name,scene,min_opacity=.03):
 row=I[name];chain=row['parents']+[row['node']];fps=scene['fps']
 start=max(n.get('start',0)for n in chain);end=min(n.get('end',scene['duration'])for n in chain)
 for frame in range(math.ceil(start*fps-1e-7),math.ceil(end*fps-1e-7)):
  opacity=math.prod(float(interp(n,'opacity',frame/fps))for n in chain)
  if opacity>=min_opacity:return frame
 raise ValueError('No visible opacity onset: '+name)
def evidence(I,name,property=None,note=None):
 v={'node_id':name,'json_pointer':I[name]['pointer']}
 if property:v['property']=property
 if note:v['note']=note
 return v
def base(identity,scene,path):
 return {'schema_version':1,'reference':identity,'scene':{'path':str(path.relative_to(R)),'sha256':sha(path)},'fps':scene['fps'],'framecount':round(scene['duration']*scene['fps']),'duration':scene['duration'],'timebase':'zero-based OUTPUT native frame; time=frame/fps; start of frame','sound_is_originally_observed':False,'basis':'Visible accepted graphics state and measured semantic builder timings only. No music, source-audio transient, generated audio or library asset is used as timing evidence.','policy':{'typing':'Only human composer/search input. A typing event here is a visible glyph/draft delta, not proof of a physically observed key-down.','not_typing':['AI message bodies','marketing title/type animation','caret blinks','placeholder iMessage text','rolling Cash amount digits','already-present text carried into view by a camera'],'delete':'No backspace is asserted without a visible human draft deletion. Composer retirement/send is not backspace.','tap':'Tap cues are aligned to visible UI response; absent finger/pointer contact is declared. Low-confidence camera/navigation interpretations are kept separately and not recommended by default.','no_transient_ground_truth':True},'events':[],'optional_inferred_events':[],'typing_spans':[],'unresolved_input_operations':[],'exclusions':[]}
O05=base('05-linq',S05,P05);O06=base('06-gallery',S06,P06)
O05['source_frame_mapping']={'kind':'identity','intervals':[{'output_start':0,'output_end_inclusive':1457,'source_offset':0}]}
O06['source_frame_mapping']={'kind':'graphics-only edit','removed_source_frames_inclusive':[1049,1229],'intervals':[{'output_start':0,'output_end_inclusive':1048,'source_offset':0},{'output_start':1049,'output_end_inclusive':1482,'source_offset':181}],'notice':'Output1049 maps to source1230, not source1049. The live-action interval is not available for UI cue placement.'}
def event(doc,frame,kind,group,confidence,observed,ev,action,delta=None,**extra):
 f=int(frame);assert f==frame and 0<=f<doc['framecount']
 out={'frame':f,'time':f/doc['fps'],'kind':kind,'group':group,'confidence':confidence,'observed_vs_inferred':observed,'evidence_layer_or_source':ev,'action_evidence':action,'source_frame':f+(181 if doc is O06 and f>=1049 else 0),'sample_offset_48000':round(f/doc['fps']*48000)}
 if delta is not None:out['character_or_delta']=delta
 out.update(extra);return out

# 05: actual source-measured independent original glyphs; no guessed cadence.
full=I05['v19-composer-typed-glyphs']['node']['semanticText']
glyphs=sorted([v['node']for k,v in I05.items()if k.startswith('v19-type-glyph-')],key=lambda n:int(n['id'].rsplit('-',1)[1]))
assert ''.join(n['semanticText']for n in glyphs)==full.replace(' ','')
cursor=0;prior_draft='';last_visible_frame=None
for n in glyphs:
 ch=n['semanticText'];whitespace=''
 while full[cursor]==' ':whitespace+=full[cursor];cursor+=1
 assert full[cursor]==ch;cursor+=1;draft=full[:cursor];frame=onset(I05,n['id'],S05)
 if whitespace:
  O05['unresolved_input_operations'].append({'kind':'whitespace','text':whitespace,'between_visible_frames_inclusive':[last_visible_frame,frame],'assigned_exact_frame':None,'sound_events_created':0,'reason':'Whitespace separates visible glyphs but has no independently visible ink/onset. Do not invent another exact space key-down.'})
 O05['events'].append(event(O05,frame,'typing','05.initial_human_composer',.99,'observed_visible_glyph_reveal',[evidence(I05,n['id'],'start/semanticText'),evidence(I05,'v19-composer-typed-glyphs','semanticText')],'First rendered native frame of this independently measured human draft glyph.',ch,visible_character=ch,draft_before=prior_draft,draft_after=draft,intervening_whitespace_without_exact_timing=whitespace,one_sound_at_this_frame=True,physical_key_down_observed=False,timing_precision_frames=1))
 prior_draft=draft;last_visible_frame=frame
assert prior_draft==full
O05['typing_spans']=[{'group':'05.initial_human_composer','start_frame':O05['events'][0]['frame'],'end_frame_inclusive':O05['events'][-1]['frame'],'draft':full,'observed_visible_glyph_events':len(glyphs),'unlocated_whitespace_operations':len(O05['unresolved_input_operations']),'guidance':'Use the23 individual visible-glyph events, not an additional burst track. Physical key-downs and exact whitespace key timings are not visible.'}]

def add05(frame,kind,group,node,action,delta=None,confidence=.94,**extra):
 O05['events'].append(event(O05,frame,kind,group,confidence,'observed_visible_ui_response',[evidence(I05,node)],action,delta,physical_touch_observed=False,**extra))
# One outgoing message bundle, not a doubled sound for its attachment + copy.
add05(149,'message_send','05.chess_outgoing_bundle','v16-preview-directional-shutter','Outgoing chess app/message bundle first enters. Question copy begins151; treat attachment+copy as one send cue, not two simultaneous sends.',full,.90,timing_window_frames=[149,151],control_press_frame_unknown=True)
for frame,kind,group,node,copy in [
 (257,'message_send','05.flight_question','g-357','hey can you find me a one way flight from Atlanta to San Francisco in July? looking for something cheap'),
 (314,'message_arrival','05.flight_reply','v10-flight-reply','On it! Found a few options, here’s the cheapest one way:'),
 (477,'message_arrival','05.flight_booked','g-567','Your flight is booked!'),
 (511,'message_send','05.necklace_question','g-572','i wanna check out some necklaces'),
 (538,'message_arrival','05.jewelry_reply','v11-hot-reply','Here’s what’s hot right now'),
 (651,'message_arrival','05.order_confirmed','g-595','Order confirmed, I’ll ping you when tracking’s ready'),
 (686,'message_send','05.groceries_question','broad-v5-group-25','can you order my weekly groceries?'),
 (699,'message_arrival','05.groceries_quote','v10-cash-reply','Sure, it’ll be $166.89'),
 (711,'message_arrival','05.cash_request_card','v10-cash-request','$166.89 Cash request'),
 (830,'message_arrival','05.groceries_ordering','g-631','Got it, ordering now'),
 (1150,'message_arrival','05.flight_checkin','g-925','Check-in just opened; tap to get your boarding pass')]:
  assert onset(I05,node,S05,min_opacity=.03)==frame,(node,onset(I05,node,S05))
  add05(frame,kind,group,node,'First native rendered entry of the complete outgoing/incoming message or card. This is a bubble/card cue, not typing body text.',copy)
# Local human selection/commit responses. Opponent moves are not extra taps.
add05(216,'tap','05.chess_select_f2','v10-selection-art','Selection opacity jumps from~.017 at215 to~.980 at216. Audible click aligned to visible cell-selection response; no finger/pointer is shown.','select f2',.94,timing_precision_frames=1)
add05(228,'tap','05.chess_move_f2_f3','root-white-pawn-post-move-selection-v19','Selected-cell/undo UI switches and the independently measured white pawn begins moving228; not the earlier discarded226 trajectory.','move f2 to f3',.91,timing_window_frames=[227,228])
disc=I05['root-cash-control-disc-v19']['node'];fill={round(k['t']*30):k['value']for k in disc['keyframes']['fill']};rail=I05['v10-cash-units-rail']['node'];offset={round(k['t']*30):k['value']for k in rail['keyframes']['y']}
for i,(press,amount_frame)in enumerate([(786,787),(791,792),(796,797),(802,803)]):
 assert int(fill[press][1:3],16)>int(fill[press-1][1:3],16)
 assert offset[amount_frame-1]-offset[amount_frame]>90
 add05(press,'tap','05.cash_plus_'+str(i+1),'root-cash-control-disc-v19','Distinct brighter plus-control response, followed by the next measured native amount-rail increment. Click alignment is observed UI response, not an observed physical contact.',f'${162+i}.89 → ${163+i}.89',.96,timing_window_frames=[press,amount_frame],amount_change_frame=amount_frame,amount_rail_evidence=evidence(I05,'v10-cash-units-rail','keyframes.y'),control_fill_before=fill[press-1],control_fill_at_event=fill[press])
for f,g,node,reason,window in [
 (101,'05.plus_drawer_open','g-119','The app drawer begins entering after the plus/composer. No pressed-plus or finger frame is independently visible; the action timing is inferred from the opening response.',[99,101]),
 (355,'05.flight_app_open','flight-review-entrance-355','First measured flight-app entrance after the chat preview; an activating tap is plausible but no control contact is shown.',[353,355]),
 (1184,'05.boarding_pass_open','g-942','Boarding pass begins rising after the explicit tap-to-open check-in message. No finger/button depression is visible.',[1182,1184])]:
 O05['optional_inferred_events'].append(event(O05,f,'tap',g,.60,'inferred_action_from_visible_navigation',[evidence(I05,node)],reason,timing_window_frames=window,recommended_by_default=False,physical_touch_observed=False))
O05['exclusions']=[{'span_frames':[0,22],'reason':'Placeholder iMessage/mic/send readiness is not typed human text.'},{'span_frames':[84,149],'reason':'Completed draft is held, moved away and sent. No backspace/deletion sound is justified.'},{'span_frames':[99,109],'reason':'Composer repeats the already completed same draft under camera motion; no duplicate typing.'},{'span_frames':[257,1150],'reason':'Whole outgoing paragraphs and AI responses/cards appear as message bodies; no human composer character sequence is visible. Their body reveal must not become keyboard sounds.'},{'span_frames':[773,810],'reason':'Cash numeric rail is changed by four plus responses, not typing. Caret blink and rolling digits are excluded from keyboard cues.'},{'span_frames':[1268,1457],'reason':'Closing title/CTA/brand glyph animations are marketing copy, not human input.'}]

# 06: static empty composer/keyboard. Message display births are still usable.
O06['typing_observation']={'exact_keypress_events':0,'reason':'The visible human composer is a static empty iMessage bitmap; keyboard presence alone is not a typing event. Book/Yes/Wait/Order/LETS GOOOO appear as outgoing message bodies without an observed draft sequence. No honest individual keypress or typing-burst span can be recovered from these accepted input states.'}
def add06(frame,kind,group,node,copy,confidence=.96,**extra):
 O06['events'].append(event(O06,frame,kind,group,confidence,'observed_visible_message_entry',[evidence(I06,node)],'Native visible message/component entry; body copy is not a typing schedule.',copy,physical_touch_observed=False,control_press_frame_unknown=(kind=='message_send'),**extra))
for node,frame,copy,group in [
 ('rene-intro-priya-precut-hires',30,'Someone just pick a weekend, I’m not the mom of this group','06.cabin_priya_first'),
 ('rene-intro-dan',56,'Not me, I organized the last one','06.cabin_dan'),
 ('rene-intro-rene',83,'Oct17 is the first weekend all of you are free','06.cabin_oct17'),
 ('source-message-art-Want',108,'Want me to book the lakeside cabin Dan sent? Before someone gets busy again','06.cabin_want'),
 ('rene-final11-group-24',148,'Ok we gotta commit','06.cabin_priya_commit'),
 ('rene-final11-group-29',179,'Let’s go! Book it','06.cabin_book'),
 ('rene-final11-group-37',208,'Done. Cabin booked','06.cabin_done')]:
  assert onset(I06,node,S06)==frame,(node,onset(I06,node,S06))
  add06(frame,'message_send'if 'book'==group.rsplit('_',1)[-1]else'message_arrival',group,node,copy,.96,timing_precision_frames=1)
for node,frame,kind,copy,group in [
 ('root-rene-gray-1-body-485',485,'message_arrival','3 similar units in your building are listed lower. Want me to write a pushback?','06.rent_comparables'),
 ('root-rene-yes-body-499',499,'message_send','Yes plz','06.rent_yes'),
 ('root-rene-gray-2-body-512',512,'message_arrival',"It's in your drafts. Friendly but firm. You've got this",'06.rent_draft_ready'),
 ('phone-v17-message-Fuji',714,'message_arrival','She’s been wanting to try film photography – found a Fuji half frame, $189, arrives Friday','06.birthday_fuji'),
 ('phone-v17-message-Wait',734,'message_send','Wait, you remember that?','06.birthday_wait'),
 ('phone-v17-message-Order',745,'message_send','Order it. She’s gonna cry','06.birthday_order'),
 ('phone-v17-message-Done',770,'message_arrival','Done. Gift wrap on 🎉','06.birthday_done'),
 ('phone-v17-message-Remember',781,'message_arrival','I remember everything 😌','06.birthday_remember'),
 ('v19-soccer-first-message',929,'message_arrival','It’s official: United signed their striker. Announced2min ago','06.soccer_news'),
 ('v19-soccer-blue-message',991,'message_send','LETS GOOOO','06.soccer_reaction'),
 ('v19-soccer-second-message',1013,'message_arrival','€85M, five years. You called this back in June, btw','06.soccer_terms')]:
  assert onset(I06,node,S06)==frame,(node,onset(I06,node,S06))
  add06(frame,kind,group,node,copy,.98,timing_precision_frames=1)
# Already-present notification carried by a moving phone is an optional cue,
# not a newly proved notification birth; never double it at its thread reframe.
O06['optional_inferred_events']=[event(O06,1,'message_arrival','06.opening_marcus',.55,'inferred_cue_from_opening_reveal',[evidence(I06,'rene-intro-marcus-precut-hires')],'Opening already-present enlarged Marcus message fades in. Physical arrival is not proved, so no default notification.',"We’ve been talking about this trip since January",recommended_by_default=False),event(O06,425,'message_arrival','06.rent_notification_reveal',.65,'inferred_cue_from_camera_reveal',[evidence(I06,'rene-final11-group-65','keyframes.y'),evidence(I06,'rene-final11-image-64')],'Existing static lockscreen notification first crosses the viewport during phone entrance. At424 its notification ROI is above the view; at425 part appears. This is not an independently animated notification birth. Same content reappears at461 in Messages: do not double-ping.',"Heads up: Your landlord emailed about the renewal. Rent's going up8%",recommended_by_default=False,timing_window_frames=[425,426],duplicate_thread_reveal_frame=461)]
O06['exclusions']=[{'span_frames':[108,239],'reason':'The visible static composer contains the iMessage placeholder and microphone; keyboard image presence does not establish human typing. No invented Book-it keystrokes.'},{'span_frames':[425,484],'reason':'Existing rent notification carried by the lockscreen and same first gray message at461 are one content item. Optional reveal cue425 only; no duplicate default arrival at461.'},{'span_frames':[680,713],'reason':'Emma birthday message is already inside the phone while its camera enters; its physical message arrival is not independently shown. No default additional ping or typing.'},{'span_frames':[240,460],'reason':'Introducing/contact/phone/inbox title glyph animation is marketing, not composer typing.'},{'span_frames':[556,689],'reason':'Remembers your people title, email/photo/card movement is not human typed input.'},{'span_frames':[813,928],'reason':'Tracks what you love and football word/icon animations are marketing, not input.'},{'span_frames':[1049,1482],'reason':'Post-live-action-cut marketing text, provider icons and closing CTA/word builds are not interactive input; no keyboard or tap cues.'}]

for doc,prefix in [(O05,'05-linq'),(O06,'06-gallery')]:
 doc['events'].sort(key=lambda e:(e['frame'],e['kind'],e['group']))
 for i,e in enumerate(doc['events']):e['id']=prefix+f'-ui-{i+1:03}'
 doc['summary']={'recommended_events':len(doc['events']),'by_kind':{k:sum(e['kind']==k for e in doc['events'])for k in ['typing','delete','tap','message_send','message_arrival','typing_burst']},'optional_inferred_events':len(doc['optional_inferred_events'])}
 assert all(0<=e['frame']<doc['framecount']and abs(e['time']-e['frame']/doc['fps'])<1e-10 for e in doc['events']+doc['optional_inferred_events'])
 (D/(prefix+'-ui-cues.json')).write_text(json.dumps(doc,indent=2,ensure_ascii=False)+'\n')
 with (D/(prefix+'-keypress-schedule.csv')).open('w',newline='')as file:
  writer=csv.DictWriter(file,fieldnames=['frame','time','kind','character_or_delta','draft_after','group','confidence','source_frame','sample_offset_48000']);writer.writeheader()
  for e in doc['events']:
   if e['kind']in ['typing','delete']:writer.writerow({k:e.get(k,'')for k in writer.fieldnames})
 print(prefix,doc['summary'])
assert all(sha(p)==h for p,h in before.items()),'Canonical inputs must remain unchanged'
assert 1048+0==1048 and 1049+181==1230 and 1482+181==1663
evidence_sources=[P05,P06,R/'references/05-linq/refine_composers_v19.py',R/'references/05-linq/composer-v19-frozen-elements.json',R/'references/05-linq/build_transition_v10.py',R/'outputs/06-gallery/final-v23/build-birthday-birth-v23.py']
(D/'05-06-evidence-and-validation.json').write_text(json.dumps({'canonical_inputs_unchanged':True,'only_visual_states_used':True,'audio_transient_analysis_used':False,'outputs_are_output_native_frames':True,'rene_cut_checks':{'output1048_source':1048,'output1049_source':1230,'output1482_source':1663},'glyph_schedule_checks':{'visible_glyphs':len(glyphs),'reconstructed_full_draft':full,'whitespace_has_no_fake_keyframes':True,'starts':[e['frame']for e in O05['events']if e['kind']=='typing']},'evidence_sources':[{'path':str(p.relative_to(R)),'sha256':sha(p)}for p in evidence_sources],'generator':{'path':str(Path(__file__).relative_to(R)),'sha256':sha(Path(__file__))},'notice':'Cue sheets only. No source/scene/media/cache/library/Git/site/publishing/paid calls edited or used. Optional inferred events are not UI/audio ground truth.'},indent=2,ensure_ascii=False)+'\n')
