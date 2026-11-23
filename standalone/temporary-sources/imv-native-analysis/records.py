import csv
import json
from pathlib import Path

refs = {
    '02-danieltian': ('Daniel Tian · Photon Agent to Agent', 'https://x.com/danieltian/status/2108261717600063915', 1920, 1080, '30/1'),
    '03-photon-mini': ('Photon Mini Apps', 'https://x.com/daniel_tian1/status/2067327329161064688', 1920, 1080, '30/1'),
    '04-poke': ('Poke Apple Messages', 'https://x.com/interaction/status/2062575428213285352', 1440, 1080, '30000/1001'),
    '05-linq': ('Linq iMessage Apps', 'https://www.linkedin.com/posts/elliottpotter_your-users-never-have-to-leave-imessage-again-activity-7477784121293950976-Dlap', 960, 720, '30/1'),
}
assets_dir = Path('../../../../projects/05-linq-complete-v1/imessage-recreations/scenes/05-linq/assets')

def evidence(film, interval, sample=None, study=None, case=None):
    title,url,w,h,fps = refs[film]
    scan_path = Path('../analysis')/film/'scan.json'
    scan = json.loads(scan_path.read_text())
    a,b = interval
    with scan_path.with_name('frames.csv').open() as f:
        mapped = [int(row['candidate_frame']) for row in csv.DictReader(f) if a <= int(row['reference_frame']) <= b]
    assert len(mapped) == b-a+1 and mapped == list(range(a,b+1))
    return dict(film=film, title=title, sourceUrl=url, caseId=case,
                sourcePath=f'../../../../projects/{film}-complete-v1/imessage-recreations/references/{film}/source.mp4',
                sourceSha256=scan['referenceSHA256'], nativeSize=[w,h], nativeRate=fps,
                sourceFrames=interval, referencePreviewFrames=sample or interval,
                acceptedOutputFrames=[mapped[0],mapped[-1]], acceptedScanOutputSha256=scan['candidateSHA256'],
                acceptedMappingPath=str(scan_path.with_name('frames.csv')), study=study)

def entry(id,title,kind,description,queries,choose,avoid,source,anatomy,phases,edits,cues,limits):
    result=dict(id=id,title=title,status=kind,description=description,queries=queries,choose=choose,avoid=avoid,source=source,
                anatomy=anatomy,phases=phases,edits=edits,cues=cues,limits=limits)
    if source:
        result['previews']={'source':f'previews/{id}.source.mp4', 'isolated':f'previews/{id}.mp4'}
        result['implementation']={'api':'mountMotion','module':'./blocks.mjs','renderEngine':'html','fps':30,
                                  'sceneCommand':f'node director/cli.mjs scene --motion {id} --out work/{id}.json',
                                  'renderCommand':f'node scripts/engines/render.mjs --method html --scene work/{id}.json --out work/{id}.mp4',
                                  'verifyCommand':'node --test director/motion-catalog/blocks.test.mjs'}
    return result

def phase(name,first,last,observation):
    return dict(name=name,sourceFrames=[first,last],observation=observation)

def hook(frame,kind,detail):
    return dict(sourceFrame=frame,kind=kind,detail=detail,provenance='authored option; source sound unconfirmed')

restaurant = 'linq-restaurant-photo-strip'
entries = [
 entry(restaurant, 'Restaurant photo strip', 'measured',
 'Browse five photos side to side while the restaurant name, action row, tabs and address stay fixed.',
 ['restaurant photo strip', 'restaurant photo swipe', 'browse photos while the place name stays fixed', 'bounded photo carousel', 'fixed title and actions', 'horizontal image rail', 'swipe through venue photos', '05-linq:057'],
 'Show the same venue from several angles while keeping the viewer oriented to one place and its next action.',
 'Use a different motion for sending attachments, switching between venues, or acquiring a new screen.',
 evidence('05-linq',[1091,1111],[1090,1112],case='05-linq:057'),
 {'moving':'One horizontal rail containing five independent images. The image positions share the same x displacement.',
  'fixed':'Venue name, detail line, action row, tabs, divider, address, and the photo viewport. All four tested text/control patches had zero integer x/y shift.',
  'mask':'The restaurant document owns the bounded photo viewport. The viewport clips the rail. Individual images also own their corner masks.',
  'anchor':'Viewport top left at source (195,303). The fixed venue name sits above it, outside the viewport.'},
 [phase('entry control',1090,1090,'Mid-motion pose showing the clipped façade and a table photo. Earlier frames already show leftward travel.'),
  phase('action',1091,1100,'Façade and table translate left. The wide overhead food image enters from the right.'),
  phase('action',1101,1106,'The rail accelerates across the overhead photo and reaches the next plated dish.'),
  phase('action',1107,1111,'Plated dish and interior take over. Speed decreases but remains nonzero at the boundary.'),
  phase('exit control',1112,1112,'Rail moves about 37 px farther left. This control is part of the same observed action.'),
  phase('horizontal settle outside event',1126,1134,'The final interior approaches x≈320 by about 1130 and remains within ~2 px through 1134. The lower document/text changes separately after the event.')],
 {'safe':['Replace image files in the same five slots. Images use centered cover and stay independently editable.',
          'Change adjacent copy/palette in an authored context. Check for overflow.',
          'Move or uniformly scale the complete block via its parent.'],
  'changesInteraction':['Changing count, slot width, gap, viewport, travel direction, duration or sample spacing changes the observed interaction.',
                        'A reading hold on the last event frame is an editorial freeze during the swipe.']},
 {'source':'Source has an audio track. No isolated source swipe or finger/contact cue is established.',
  'options':[]},
 ['The 21-frame preset is a mid-swipe extract. No release/contact, actual settled hold or exit occurs within it.',
  'Offscreen objects and finger trajectory remain unknown. Sample arrivals and pauses are visible picture behavior.',
  'Relative rail x is measured. Rounded corners, invisible image extents and isolated/context styling are authored approximations.']),
 entry('daniel-typing-to-reply', 'Typing indicator becomes a reply', 'source-informed',
 'Convert waiting dots into a readable incoming reply at the same left-edge and tail anchor.',
 ['typing dots become reply', 'typing indicator becoming a reply', 'incoming bubble expands from dots', 'agent waiting response', 'daniel muse typing indicator'],
 'Make the transition from waiting to a single readable answer legible.',
 'Avoid for human composer typing, multiple separate replies, or any workflow with no visible waiting state.',
 evidence('02-danieltian',[205,237],[204,237]),
 {'moving':'Incoming lozenge grows in width, dots fade away, reply resolves. The original thread has mild camera drift.',
  'fixed':'Reply shares the incoming lane with the dots. The authored example keeps the previous outgoing turn and outer frame still.',
  'mask':'Incoming bubble bounds own the content mask for the widening/reveal.',
  'anchor':'Bubble left edge with its tail near the lower-left; text reveal is downstream of width growth.'},
 [phase('entry',205,215,'Blurred low-contrast state grows into a readable three-dot indicator. A faint precursor was visible at 204.'),
  phase('wait',215,229,'Dots change emphasis within the small bubble.'),phase('action',230,233,'Surface widens in the same lane as the dots yield to a left-to-right reply reveal.'),
  phase('settle and hold',233,237,'Readable complete reply. No separate release or exit is visible.')],
 {'safe':['Change reply and preceding request. Keep the response short enough for one line.',
          'Change palette or uniformly scale the mount.'],
  'changesInteraction':['A multiline response requires new reveal and bubble geometry.',
                        'Stretching the dots hold changes perceived response latency.']},
 {'source':'Source mix present. No keystroke or discrete dot sound is established.', 'options':[hook(233,'message_arrival','Optional quiet arrival when the reply is readable. Never sound dots individually.')]},
 ['Native phase anchors with authored layout, dot cadence, blur, and widths. No claim of source-pixel trajectory parity.']),
 entry('poke-choice-to-outgoing', 'A selected option becomes an outgoing result', 'source-informed',
 'Dim just the selected row, release it, then replace the list with a right-aligned conversation result.',
 ['selected option becomes outgoing message', 'choice to message', 'press row commits choice', 'selection becomes sent result', 'poke choice indian'],
 'Show that one committed choice became part of the conversation and can prompt a follow-up.',
 'Avoid for hover, a tentative choice, multiselect, or a shape morph between the row and the message.',
 evidence('04-poke',[330,375],[329,375],study='poke-choice_to_message'),
 {'moving':'Selected row ink changes opacity, list pulls back. The right-aligned result uses a separate actor and settles independently.',
  'fixed':'Physical stage is the reference frame for these planes. The authored composer stays fixed.',
  'mask':'Conversation viewport clips the separate list and result groups.',
  'anchor':'Selected row stays inside the left list until cut. Result lands on the right message lane.'},
 [phase('entry',330,338,'Existing list is readable before the press.'),phase('action',339,347,'Selected row reaches its dimmest opacity; neighboring rows remain readable.'),
  phase('release',348,360,'Row ink recovers as the parent list pulls back.'),phase('handoff',361,361,'List ends after 360. Outgoing result and the task label appear as new actors.'),
  phase('settle',361,375,'Result and camera settle. The next incoming response first appears around 375; no useful reading hold on that reply within this range.')],
 {'safe':['Replace the six labels and the selected label within the row width.', 'Change surface colors or uniformly scale the result.'],
  'changesInteraction':['Moving a different row changes the selected result. Changing row count or timing changes the framing and pullback.']},
 {'source':'Source mix present. Discrete cue attribution unconfirmed.','options':[hook(339,'choice_press','Accent the selected row only.'),hook(361,'choice_commit','Optional result/send accent at the cut.')]},
 ['Stage runs at 30 fps by frame index; source is 30000/1001. Local geometry, easing and camera travel are authored.',
  'Output frame numbers follow the matched director GSAP scan. Equal frame numbers do not imply identical content.']),
 entry('mini-anchored-rich-card', 'Anchored rich-card arrival', 'source-informed',
 'Let one actionable result grow from its position in chat, hold long enough to read, then darken just that card on press.',
 ['rich card springs in', 'anchored rich-card arrival', 'card that grows from conversation', 'mini app result action card', 'message result spring'],
 'Give one meaningful rich result a clear arrival and a readable action beat.',
 'Avoid for routine replies, large bounces on every message, or a full-screen app opening.',
 evidence('03-photon-mini',[546,617],[545,618],study='mini-rich_card_arrival'),
 {'moving':'Card shell and art scale and fade together; original thread and parent camera also move. Press overlay operates only inside the card.',
  'fixed':'Card origin is stable inside the message stack. In the authored version the outer frame is stationary.',
  'mask':'Conversation viewport contains the thread. The card owns the rounded press tint.',
  'anchor':'Lower-left attachment lane under the agent reply. The block uses a near-upper-left origin for the new card inside that lane.'},
 [phase('entry',546,547,'Tiny, low-confidence first image at the anchor.'),phase('action',548,551,'Fast growth to opaque; art reads before the later press.'),
  phase('settle',552,566,'Small scale overshoot near 555; camera and thread continue settling.'),
  phase('reading hold',567,604,'Card remains readable as its parent drifts into the final composition.'),
  phase('press',605,608,'Local card darkens.'),phase('release',609,614,'Tint clears.'),phase('hold',615,617,'Card remains before separate sheet arrival at 618.')],
 {'safe':['Replace card title, subtitle, action and colors within their boxes.', 'Uniformly scale the whole block.'],
  'changesInteraction':['Changing the anchor, press onset, meaning of the press, or camera timing changes the continuity.']},
 {'source':'Source mix present. Visible motion supplies timing; source sound attribution is unconfirmed.',
  'options':[hook(546,'card_arrival','Optional soft arrival.'),hook(605,'card_press','Optional single press accent.')]},
 ['The layout, image placeholder, scales and parent path are authored. Source card artwork and camera curve remain visible in the linked footage.']),
 entry('linq-conversation-to-app', 'Conversation opens a mini app', 'source-informed',
 'Bring a clipped working panel up over a still-visible conversation so the preview becomes useful detail.',
 ['expand conversation into a mini app', 'chat card expands to mini app', 'embedded app opens in chat', 'conversation to working sheet', 'linq flight app opening'],
 'Show a recommendation leading to an interactive document on top of the conversation.',
 'Avoid when the whole experience leaves the conversation, or there is no visible app to use.',
 evidence('05-linq',[351,367],[350,367],study='linq-chat-to-mini-app'),
 {'moving':'Independent foreground document fades in, travels upward and lands; the underlying thread softens.',
  'fixed':'Chat stays on a separate plane. Foreground panel keeps its width while revealing through an anchored portal.',
  'mask':'Panel own top corners plus a fixed vertical portal. Chat uses its own stage and blur.',
  'anchor':'App portal centered at x≈188..772 on the 960×720 source. The authored stage places the portal on a new conversation.'},
 [phase('entry',351,354,'Chat reply and compact preview are already readable.'),phase('action',355,358,'App panel arrives from low in the portal, initially translucent.'),
  phase('settle',359,366,'Panel resolves into a clear full-width document; background thread softens.'),
  phase('hold',366,367,'App is readable. Later scrolling is outside this entry; no exit or visible finger release.')],
 {'safe':['Change preview title, app title, detail copy and palette within their boxes.', 'Move/scale whole composition.'],
  'changesInteraction':['Repositioning the portal relative to chat, changing its clip, or extending into document scroll requires re-timing and new evidence.']},
 {'source':'Source mix present. No actual tap/contact is visible or attributable.', 'options':[hook(355,'panel_open','Optional opener tied to the first foreground frame.')]},
 ['This shorter entrance is part of the existing 351–510 Linq chat-to-app study. Layout, geometry and easing of the playable version are authored.']),
 entry('keiki-native-attachment-stack','Native Messages attachment stack','evidence-gap',
 'Send four product photos together as one native Messages attachment stack.',
 ['four product images sent together as a native messages attachment stack', 'send multiple photos in one imessage', 'multi-image message bundle', 'attachment stack', 'native image pile', 'four product photos sent together'],
 'Show how multiple selected images appear together in an actual sent message.',
 'Do not use a restaurant gallery swipe, floating card orbit, or web carousel for the native send.',
 None, None, [], None, None,
 ['Needs verified capture from imv/imessage-ui showing selection, send, native arrival and settled stack for four attachments. Source, tap path, overlap, offsets, clipping and cue timing are pending.'])
]
r=entries[0]
r['previews'].update(context='previews/linq-restaurant-photo-strip.context.mp4',
                     controls='previews/linq-restaurant-photo-strip.controls.mp4',
                     comparison='previews/linq-restaurant-photo-strip.comparison.mp4',
                     frames='previews/linq-restaurant-photo-strip.frames.jpg')
r['implementation']['contexts']=['isolated','restaurant','conversation']
r['implementation']['variants']=['measured','controls']
r['measurement']={
    'referenceFrame':1090,
    'viewport':{'x':195,'y':303,'width':578,'height':334},
    'method':'Integer edge measurements across y=355–589. Threshold median background difference, match photo edges/gutters across frames and register title, tabs, action and address patches independently. Compare positional repeats and adjacent controls before fitting. Native source frames were decoded without resampling.',
    'uncertainty':'Rail dx about ±2 px from thresholding/chroma/compression; 499 px bowl extent is a visible edge fit. The y boundary varies about 1 px, and fixed elements have zero integer x/y shift (subpixel/codec differences remain). Hidden façade extent is inferred from the retained crop. No hand or off-viewport trajectory is visible.',
    'slots':[{'actor':name,'x':x,'width':w,'asset':str(next(assets_dir.glob(f'*-restaurant-{name}.png')))}
             for name,x,w in [('facade',-124,417),('table',313,268),('bowl',602,499),('octopus',1122,334),('interior',1478,444)]],
    'railDxPx':[0,-19,-41,-41,-66,-95,-129,-168,-168,-215,-272,-344,-438,-438,-563,-719,-867,-977,-977,-1057,-1116,-1162,-1199],
    'slotAssetProvenance':'Existing individual source-derived component crops in Linq scene assets. No source page/movie is used as a moving layer.'
}
Path('registry.json').write_text(json.dumps({'version':1,'frameConvention':'Zero-based decoded native source frame numbers, inclusive. Preview footage is a trimmed native source selection.',
 'entries':entries}, indent=2, ensure_ascii=False)+'\n')
