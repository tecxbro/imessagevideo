"""Produce conservative SFX design cue sheets from measured reference attacks.

Only sfx-* analysis files are written. No waveform, source sample, generated
sound, or output media is copied into a soundtrack by this script.
"""
from pathlib import Path
import json, re, subprocess
import numpy as np

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
# Visual targets are approximate scene landmarks, not claimed audible effects.
EVENTS={
'01-photonhq': '''0.10|title_tick|Introducing title reveal
1.87|ui_click|Cursor/pill click and phrase entrance
4.10|soft_transition|Your agent phrase entrance
5.25|scroll_ticks|Channel-list scroll
6.40|soft_transition|Free for everyone line
8.20|soft_transition|SMS wall entrance
9.50|soft_transition|Email wall transition
10.6667|soft_transition|Call wall transition
11.6667|soft_transition|iMessage wall transition
12.9667|soft_transition|WhatsApp wall transition
14.20|soft_transition|Telegram wall transition
15.77|confirm_tick|Registration badge/title
16.70|title_tick|On us punctuation
17.30|soft_transition|Try it today title
18.00|shimmer_short|URL letter reveal
19.67|logo_resolve|Photon mark entrance''',
'02-danieltian': '''0.16|title_tick|Intro type and inline icons
2.33|soft_transition|Composer entrance
3.00|typing_cluster|Composer typing passage
5.80|ui_send|Message send and burst
6.20|soft_transition|Phone entrance
7.60|message_pop|Muse reply
8.73|soft_transition|Reasoning text replaces phone
12.03|search_tick|Search capsule entrance
13.83|scatter_ticks|Phone-number field birth
16.13|ui_pop|Provider capsules emerge
17.80|confirm_tick|Provider selection checks
18.35|soft_transition|Group avatar assembly
20.40|soft_transition|Group header settles
21.00|message_pop|Kickoff message
22.50|message_pop|Agent assignment messages
24.80|message_pop|Budget question
26.30|ui_send|Budget response
27.20|ui_pop|Thumbs-up reaction
28.20|card_open|Cabin rich card entrance
30.55|ui_send|Love it reply
31.50|confirm_tick|Booking confirmation
32.50|message_pop|Ride booking confirmation
33.50|message_pop|Restaurant booking confirmation
34.20|title_tick|Phone book title
37.70|scroll_ticks|Provider capsule title cycle
41.25|logo_resolve|Final URL''',
'03-photon-mini': '''0.20|title_tick|Mini Apps intro title
1.80|soft_transition|Phone entrance
3.20|ui_send|Email request message
6.00|card_open|Draft email rich panel
7.00|ui_click|Email panel interaction
9.40|card_open|Contact picker
10.67|soft_transition|Rapid close-up camera
11.25|soft_transition|Camera pullback
13.70|soft_transition|Large Memoji transition
14.60|soft_transition|Lunch conversation phone entrance
15.70|message_pop|Lunch question
16.70|ui_send|Something light reply
18.80|card_open|Food recommendation rich card
20.70|card_open|Food sheet rise
22.00|ui_click|Food selection interaction
23.40|soft_transition|Phone pullback
24.40|ui_pop|Food avatars and order bubbles
26.73|soft_transition|Rapid mini-app montage starts
27.20|soft_impact|Jump Jump game entry
28.33|soft_transition|Uber app cut
28.90|soft_transition|Health app cut
29.30|soft_transition|Manus app cut
29.60|soft_transition|Google app cut
30.00|soft_transition|App-card collage
32.80|scroll_ticks|Category title sequence begins
33.90|scroll_ticks|Category-list acceleration
35.00|scroll_ticks|Category-list changes
36.50|title_tick|Available today CTA''',
'04-poke': '''0.40|ui_pop|Favorites row entrance
0.90|soft_transition|Poke icon push and morph
3.60|soft_transition|Messages inbox pullback
4.40|message_pop|Sarah dinner message close-up
6.00|card_open|Calendar sheet rises
7.50|ui_click|Friday time selection
8.80|message_pop|Locked Friday message
9.30|message_pop|Food question
10.20|card_open|Cuisine options open
11.90|ui_click|Indian selection
12.80|message_pop|Find a spot reply
13.50|ui_pop|Thumbs-up reaction
15.30|soft_transition|Keyboard/composer camera move
16.70|message_pop|Location card shared
18.90|card_open|Restaurant sheet opens
21.50|ui_click|Restaurant selected
22.00|soft_transition|Restaurant sheet dismisses
23.70|message_pop|Map rich card arrives
27.00|soft_transition|Audio-message waveform close-up
28.80|message_pop|Reminder confirmation
30.00|soft_transition|Feature bubbles begin
32.00|scroll_ticks|Feature bubble scroll
35.80|card_open|Connect app cards
37.80|soft_transition|Service-icon grid opens
40.70|logo_resolve|Poke.com end title''',
'05-linq': '''0.80|typing_cluster|Opening chess request typing
3.20|ui_click|Plus/app drawer interaction
3.60|card_open|App drawer scroll
4.3333|card_open|Games drawer opens
4.95|message_pop|Chess rich preview
6.30|message_pop|Always down reply
7.20|game_piece_tick|Chess pawn move
8.60|ui_send|Flight request
10.70|message_pop|Flight reply/card
11.90|card_open|Flight Details app entrance
12.40|soft_transition|Fast flight-document scroll
13.9333|soft_transition|Fare to seat-map handoff
14.75|ui_click|Book seat interaction
15.80|confirm_tick|Flight booked reply
17.20|ui_send|Jewelry request
19.30|card_open|Jewelry product grid opens
20.40|soft_transition|Pendant detail camera
21.70|confirm_tick|Jewelry order confirmation
23.00|ui_send|Groceries request
24.00|card_open|Apple Cash request card
25.50|card_open|Cash amount panel opens
27.50|confirm_tick|Cash send/ordering confirmation
28.80|card_open|Chess game resumes
29.70|game_piece_tick|Queen move
30.30|celebration_short|Chess win and confetti
31.50|card_open|Four in a Row entrance
31.90|game_piece_tick|Counter drop
33.30|card_open|Foodash group order opens
34.60|ui_pop|Participant/subtotal update
35.80|card_open|Restaurant business card
36.70|soft_transition|Restaurant image carousel
38.30|message_pop|Check-in notification
39.40|card_open|Boarding pass expands
40.70|soft_transition|Phone gallery pullback
42.35|title_tick|iMessage Apps headline
44.80|title_tick|What will you build
46.00|logo_resolve|Linq wordmark''',
'06-gallery': '''0.10|message_pop|Opening Marcus message
1.10|soft_transition|Group phone pullback
1.80|soft_transition|Group phone camera/state cut
3.60|soft_transition|Push into lower thread
4.00|message_pop|Cabin booking suggestion
5.60|ui_send|Book it message
6.90|confirm_tick|Done/calendar reply
8.40|title_tick|Introducing Rene title
10.60|title_tick|Best contact title
12.50|soft_transition|Watches your inbox title
13.45|ui_pop|Messages icon insertion
14.00|notification_tick|Lockscreen notification
15.50|message_pop|Rent pushback suggestion
16.40|ui_send|Yes plz reply
17.00|soft_transition|Phone and email panes
18.50|title_tick|Remembers your people
20.50|soft_transition|Portrait burst
21.50|notification_tick|Emma birthday notification
23.00|soft_transition|Birthday phone entrance
24.00|ui_send|Wait you remember that
24.86|ui_send|Order it message
25.65|confirm_tick|Gift wrap confirmation
26.40|message_pop|I remember everything reply
27.40|title_tick|Tracks what title
28.50|title_tick|You title
29.70|soft_impact|Love/ball typographic handoff
30.40|ball_tick|Ball and soccer-news scene
31.00|message_pop|Transfer news message
32.00|ui_send|LETS GOOOO reply
33.70|message_pop|Transfer details
41.00|title_tick|Does the work for you black card
43.30|title_tick|Lives where you title
44.40|title_tick|Already/text white card
46.00|ui_pop|Messaging app icon cycle
47.40|logo_resolve|Rene mascot and wordmark
49.10|title_tick|Just like a friend
50.60|title_tick|Start now
51.70|logo_resolve|QR and rene.co end card'''
}
DURATION={'typing_cluster':.7,'scroll_ticks':.35,'soft_transition':.22,'card_open':.16,'logo_resolve':.4,'shimmer_short':.32,'celebration_short':.45,'ui_send':.14,'ui_click':.035,'message_pop':.09,'ui_pop':.08,'confirm_tick':.10,'title_tick':.07,'soft_impact':.10,'game_piece_tick':.045,'ball_tick':.08,'search_tick':.06,'scatter_ticks':.26,'notification_tick':.13}
PALETTES={
'01-photonhq':'Music-led, very restrained UI layer. Use a dry narrow click for the cursor, low-level filtered-air sweeps for wall changes, and a short original glass-like URL/logo accent. Do not add literal phone ringing to the call wall merely because call graphics appear.',
'02-danieltian':'Small dry taps and rounded message pops; airy search/number-field movement; sparse light confirmation ticks. Keep provider assembly tactile, not a cascade of loud notifications. A short synthetic send sweep may follow the outgoing bubble, with no imitation of a proprietary notification recording.',
'03-photon-mini':'Tactile mini-app accents, soft sheet swipes, light game/contact-selection clicks and a restrained rising sweep for the collage. Category changes should use at most a few delicate ticks. Source tail is quiet; avoid inventing a loud end-logo sting without content-aware evidence.',
'04-poke':'Soft rounded UI pops and dry selection taps; short filtered sheet movements. Feature-card scroll and icon grid can use a single airy texture rather than one sound per card/logo. The displayed audio message does not prove an audible voice; speech is outside this SFX-only cue proposal.',
'05-linq':'Fast, lightly mechanical app taps; gentle slide/whoosh layers for native app entrances; dry wood-like game-piece ticks; one short restrained win flourish. Cash amount changes should not become a loud cash-register effect. Boarding pass and final brand resolve should stay compact.',
'06-gallery':'Warmer, conversational rounded message pops and gentle chimes, restrained portrait/phone sweeps, a soft ball contact if desired. Use clean title accents for black/white cards. Preserve the live-action cut map and leave room for any reference speech/lyrical content to be handled by the main audio analysis.'
}

def map_time(t,k):
    if k!='06-gallery':return t
    if 1049/30<=t<41:return None
    return t if t<1049/30 else t-181/30

def silence(k):
    p=ROOT/'references'/k/'source.mp4'
    r=subprocess.run(['ffmpeg','-hide_banner','-nostats','-threads','1','-i',str(p),'-vn','-af','silencedetect=noise=-55dB:d=0.1','-f','null','-'],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True,check=True)
    starts=[float(x) for x in re.findall(r'silence_start: ([0-9.]+)',r.stderr)]
    ends=[float(x) for x in re.findall(r'silence_end: ([0-9.]+)',r.stderr)]
    spans=[]
    for start in starts:
        end=next((e for e in ends if e>=start),None)
        spans.append({'source_start':start,'source_end':end})
    return spans

def build(k):
    m=json.loads((OUT/f'sfx-{k}-measurements.json').read_text()); candidates=m['onset_candidates']; valid=[c for c in candidates if c['output_time'] is not None and c['output_time']<m['output_video_duration']]
    # Fit a recurring subdivision directly to observed attacks. This is not
    # labeled a tempo: divisions can represent beat, half-beat or sixteenths.
    ts=np.array([c['source_time'] for c in candidates]); weights=np.array([min(c['onset_score'],6) for c in candidates])
    options=[]
    for lag in m['measurement']['beat_grid']['alternatives'][:5]:
        for div in [1,2,4,8]:
            period=lag['period_s']/div
            if not .10<=period<=.7:continue
            for phase in np.arange(0,period,.005):
                distance=np.abs((ts-phase+period/2)%period-period/2)
                support=float((weights*np.exp(-(distance/.018)**2)).sum()/weights.sum())
                options.append((support,period,float(phase)))
    support,period,phase=max(options)
    for c in valid:
        dist=abs((c['source_time']-phase+period/2)%period-period/2)
        low=c['band_energy_fraction']['low_0_180']; musical=dist<.028
        c['recurring_subdivision_distance_s']=round(dist,4)
        c['attribution']='music_or_percussion_likely' if musical else 'ambiguous_mixed_transient'
        c['attribution_confidence']=.7 if musical and low>.25 else (.6 if musical else .25)
    silent=silence(k); cues=[]
    for line in EVENTS[k].splitlines():
        st,cat,visual=line.split('|'); st=float(st); ot=map_time(st,k)
        if ot is None or ot>=m['output_video_duration']:continue
        nearest=min(valid,key=lambda c:abs(c['source_time']-st))
        delta=nearest['source_time']-st; measured=abs(delta)<=.16
        source_time=nearest['source_time'] if measured else st
        output_time=map_time(source_time,k)
        quiet=any(s['source_start']<=source_time<(s['source_end'] or float('inf')) for s in silent)
        recurring=measured and nearest['attribution']=='music_or_percussion_likely'
        confidence=.24 if not measured else (.30 if recurring else .46)
        if quiet:confidence=.1
        rationale=f'Visual context: {visual}. '
        if measured:
            rationale+=f'Mixed-audio attack measured at source {source_time:.3f}s ({delta:+.3f}s from the approximate visual anchor), onset score {nearest["onset_score"]:.3f}, centroid {nearest["centroid_hz"]:.0f}Hz. '
            rationale+=('It recurs near the musical subdivision grid; this may be percussion rather than an independent effect. ' if recurring else 'This attack is away from the fitted musical subdivision grid, but that alone does not establish a UI source. ')
        else:rationale+='No retained measured attack is within160ms; timing and category are a visual-only sound-design proposal. '
        rationale+='Category is a proposed newly synthesized accent, not a verified identification of the original sound.'
        if quiet:rationale+=' The source is below the -55dBFS silence threshold here; omit by default.'
        cues.append({'output_time':round(output_time,4),'source_time':round(source_time,4),'source_visual_anchor_time':st,'category':cat,'strength':nearest['strength_relative'] if measured else .2,'strength_definition':'Measured attack score normalized to this film\'s95th-percentile attack, not recommended mix amplitude.','recommended_mix_strength':.15 if cat in ['typing_cluster','scroll_ticks'] else (.28 if cat in ['logo_resolve','soft_transition'] else .22),'duration':DURATION[cat],'duration_definition':'Proposed synthetic effect length; isolated reference tail is not established.','measured_mixed_decay_duration':nearest['duration_estimate'] if measured else None,'rationale':rationale,'confidence':confidence,'source_presence':'mixed_transient_candidate' if measured else 'visual_only_proposal','independent_sfx_confirmed':False,'music_overlap_likely':bool(recurring),'optional':True,'omit_by_default':bool(quiet),'auditioned':False})
    out={'reference':k,'source_sha256':m['source_sha256'],'output_visual':'outputs/'+k+'/gsap.mp4','output_duration':m['output_video_duration'],'status':'MEASURED_MIXED_AUDIO_PLUS_OPTIONAL_SOUND_DESIGN_CUES_NOT_ISOLATED_SFX_CERTIFICATION','auditioned':False,'source_samples_reused':False,'original_audio_written':False,'timing':{'detector_hop_s':.005,'window_s':m['measurement']['window_s'],'acoustic_attack_uncertainty_s':.03,'visual_anchor_uncertainty_s':.16,'rene_time_map':'Source[1049/30,41) excluded; source>=41 maps to output=source-181/30.' if k=='06-gallery' else 'Identity source/output time map; video duration governs.'},'measurements':{'rms_dbfs':m['measurement']['rms_dbfs'],'peak_dbfs':m['measurement']['peak_dbfs'],'recurring_attack_subdivision_s':round(period,6),'recurring_attack_phase_s':round(phase,4),'weighted_grid_support':round(support,4),'recurrence_limit':'This identifies attack repetition, not a uniquely identified musical tempo.','silence_threshold_dbfs':-55,'silence_spans_source':silent,'candidate_cap':180,'cap_limit':'Up to180 strongest attack peaks retained per film; weak or masked UI sounds may be absent. Silence detection uses the full audio, independently of that cap.'},'palette':PALETTES[k],'mix_guidance':'Music should carry the rhythm. Treat every cue as optional; do not double the drum pattern with an SFX tick. For a first pass, use only key sends/selections/large transitions at low level, then verify against actual content-aware audio analysis. No reference audio samples may be used in the new soundtrack.','cues':cues,'measured_music_or_ambiguous_transients':valid,'excluded_live_action_candidates':[c for c in candidates if c['output_time'] is None]}
    (OUT/f'sfx-{k}-cues.json').write_text(json.dumps(out,indent=2)+'\n')
    return out

if __name__=='__main__':
    reports=[build(k) for k in EVENTS]
    text=['# SFX analysis and palette','', 'These sheets measure mixed reference audio and align optional, newly synthesized accents to visual context. No listening endpoint was available to this analysis worker. No isolated sound identity is asserted, and no reference waveform/sample is saved or reused. Root\'s content-aware audio captions may later refine attribution.','', 'The detected recurring attacks are kept separate from the proposed cue list. Repetition is evidence for music/percussion, not proof that every off-grid event is UI sound. The180-peak cap favors strong attacks and can miss weak masked effects. Durations in the cue list are design lengths, not isolated source decay claims.','']
    for r in reports:
        text += [f'## {r["reference"]}', '',r['palette'],'',f'Measured mono RMS {r["measurements"]["rms_dbfs"]}dBFS; channel peak {r["measurements"]["peak_dbfs"]}dBFS. Recurring attack subdivision candidate {r["measurements"]["recurring_attack_subdivision_s"]}s (not a certified tempo). {len(r["cues"])} optional cues. Full measured silence intervals are in the JSON.','']
    text += ['## Production constraints','','Create all sounds from oscillators/noise/envelopes or newly licensed/generated material. Use short rounded message transients, dry taps, filtered air movement and restrained tonal confirmations. Avoid literal cash registers, phone ringing or speech inferred only from UI pictures. Keep UI accents quieter than main musical hits, with sparse short tails; do not cover every changing word or icon. Rene omits source34.9666667–41s; all published output cue times already apply the181/30s offset after that cut.']
    (OUT/'sfx-palette-notes.md').write_text('\n'.join(text)+'\n')
    print(json.dumps([{'reference':r['reference'],'cue_count':len(r['cues']),'recurring_subdivision':r['measurements']['recurring_attack_subdivision_s'],'silence':r['measurements']['silence_spans_source']} for r in reports],indent=2))
