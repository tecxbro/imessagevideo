import {rect, text, group, Avatar, CameraRig} from '../director/components.mjs';

export const FONT = 'Arial, "Apple Color Emoji", sans-serif';
const graphemes = value => [...new Intl.Segmenter(undefined, {granularity:'grapheme'}).segment(value)].map(part => part.segment);
const fail = (ok, message) => { if (!ok) throw new Error(message); };
const positive = n => Number.isFinite(n) && n > 0;
const label = (id, value, x, y, size=17, extra={}) => text(id, value, x, y, size, {fontFamily:FONT,...extra});

export function canvasMeasure(context) {
  return (value, size=17, weight=400) => {
    context.font = `${weight} ${size}px ${FONT}`;
    return context.measureText(value).width;
  };
}

export function wrapText(value, width, measure, size=17, weight=400) {
  fail(typeof value === 'string', 'Copy must be a string');
  fail(positive(width) && typeof measure === 'function', 'Provide a width and real font measurement');
  const lines = [];
  for (const paragraph of value.split('\n')) {
    let line = '';
    for (const token of paragraph.match(/\s+|\S+/gu) ?? []) {
      if (measure(line + token, size, weight) <= width) { line += token; continue; }
      if (line.trim()) { lines.push(line.trimEnd()); line = ''; }
      for (const cluster of graphemes(token.trimStart())) {
        fail(measure(cluster, size, weight) <= width, 'A grapheme is wider than its text container');
        if (measure(line + cluster, size, weight) > width) { lines.push(line); line = ''; }
        line += cluster;
      }
    }
    lines.push(line.trimEnd());
  }
  return lines;
}

export function Message({id, copy, outgoing, maxWidth=274, measure}) {
  if (/^[\p{Extended_Pictographic}\p{Emoji_Component}\s\u200d\ufe0f]+$/u.test(copy) && /\p{Extended_Pictographic}/u.test(copy)) {
    const lines=wrapText(copy,maxWidth,measure,48);
    return {width:Math.max(...lines.map(line=>measure(line,48))),height:lines.length*58+6,lines,layer:group(id,0,0,[label(id+'-copy',lines.join('\n'),0,0,48,{lineHeight:58})])};
  }
  const lines = wrapText(copy, maxWidth-32, measure);
  const width = Math.max(54, ...lines.map(line => measure(line) + 32));
  const height = lines.length*23 + 24;
  const fill = outgoing ? '#087ff5' : '#e9e9eb';
  const tail = outgoing ? `M ${width-18} ${height-18} Q ${width-2} ${height+1} ${width+6} ${height-2} Q ${width-3} ${height-7} ${width-2} ${height-22} Z` : `M 18 ${height-18} Q 2 ${height+1} -6 ${height-2} Q 3 ${height-7} 2 ${height-22} Z`;
  return {width,height,lines,layer:group(id,0,0,[
    {id:id+'-tail',type:'path',d:tail,fill},
    rect(id+'-surface',0,0,width,height,fill,18),
    label(id+'-copy',lines.join('\n'),16,11,17,{lineHeight:23,fill:outgoing?'#ffffff':'#19191c'})
  ])};
}

export function Reaction({id, reaction, owner, outgoing, measure}) {
  const width=Math.max(44,measure(owner.initials,9,600)+34), height=34;
  return {width,height,layer:group(id,0,0,[
    {id:id+'-anchor',type:'circle',x:width/2-4,y:height-5,width:8,height:8,fill:outgoing?'#dcecff':'#eff0f3'},
    rect(id+'-pill',0,0,width,height,outgoing?'#dcecff':'#eff0f3',17,{stroke:'#ffffff',strokeWidth:2}),
    label(id+'-emoji',reaction.emoji,6,4,21),
    label(id+'-owner',owner.initials,29,19,9,{fontWeight:600,fill:'#23425f'})
  ],{ownerId:owner.id,ownerName:owner.name})};
}

export function AttachmentStack({id, cards, switches=[], measure, duration}) {
  const width=258, height=240;
  fail(cards.length>=1 && cards.length<=10, 'Use 1–10 attachment cards');
  let previous=-1;
  for (const entry of switches) {
    fail(Number.isFinite(entry.at) && entry.at>previous && entry.at>=0 && entry.at<duration,'Attachment switches must increase within the film');
    fail(Number.isInteger(entry.index) && entry.index>=0 && entry.index<cards.length,'Attachment index out of range');
    previous=entry.at;
  }
  const indices=[{at:0,index:0},...switches];
  const art=cards.map((card,index) => {
    fail(typeof card.title==='string' && typeof card.body==='string','Attachment needs editable title and body');
    const title=wrapText(card.title,218,measure,22,600), body=wrapText(card.body,218,measure,16);
    fail(title.length<=2 && body.length<=4,'Attachment copy exceeds its authored capacity');
    const poses=[];
    for (const [i,entry] of indices.entries()) {
      const target=(index-entry.index)*width;
      poses.push({t:entry.at,value:i ? (index-indices[i-1].index)*width : target,ease:'hold'});
      if (i) poses.push({t:Math.min(entry.at+.35,duration),value:target,ease:'easeInOut'});
    }
    return group(`${id}-card-${index}`,0,0,[
      rect(`${id}-card-${index}-paper`,0,0,width,height,card.color ?? '#e9f2eb',17),
      label(`${id}-card-${index}-symbol`,card.symbol ?? '✦',20,16,34),
      label(`${id}-card-${index}-title`,title.join('\n'),20,66,22,{fontWeight:600,lineHeight:27}),
      label(`${id}-card-${index}-body`,body.join('\n'),20,132,16,{lineHeight:21,fill:'#394951'})
    ],{keyframes:{x:poses}});
  });
  return {width,height:height+32,layer:group(id,0,0,[
    group(id+'-cards',0,0,art,{clip:{x:0,y:0,width,height,radius:17}}),
    label(id+'-counter','1 / '+cards.length,width,248,12,{textAnchor:'end',fill:'#6b7280',keyframes:{text:indices.map(entry=>({t:entry.at+.35,value:`${entry.index+1} / ${cards.length}`,ease:'hold'}))}})
  ])};
}

export function LinkPreview({id, title, color, url, measure}) {
  const lines=wrapText(title,242,measure,17,600);
  fail(lines.length<=2,'Link preview title exceeds two lines');
  let host;
  try { host=new URL(url).hostname; } catch { throw new Error('Link preview requires a valid URL'); }
  const hostLines=wrapText(host,242,measure,11);
  return {width:274,height:173+hostLines.length*14,layer:group(id,0,0,[
    rect(id+'-surface',0,0,274,173+hostLines.length*14,'#f0f0f2',15),
    rect(id+'-thumbnail',0,0,274,104,color ?? '#c4a484',15),
    label(id+'-title',lines.join('\n'),16,115,17,{lineHeight:21,fontWeight:600}),
    label(id+'-domain',hostLines.join('\n'),16,160,11,{lineHeight:14,fill:'#6d7177'})
  ])};
}

export function PhotoStack({id, photos, caption, measure}) {
  fail(photos.length>=1 && photos.length<=10,'Photo stack requires 1–10 photos');
  const width=274, nodes=[];
  for (const [index,photo] of [...photos].entries()) {
    fail(positive(photo.aspectRatio) && /^#[0-9a-f]{6}$/i.test(photo.color),'Photo needs a positive aspect ratio and hex placeholder color');
    const height=Math.min(150,186/photo.aspectRatio), w=height*photo.aspectRatio;
    fail(w<=258,'Photo ratio is too wide for this stack');
    const column=index%3, row=Math.floor(index/3);
    nodes.push(group(`${id}-photo-${index}`,7+column*36,12+column*46+row*210,[
      rect(`${id}-photo-${index}-border`,-3,-3,w+6,height+6,'#ffffff',10),
      rect(`${id}-photo-${index}-image`,0,0,w,height,photo.color,8)
    ],{rotation:(index%2?1:-1)*3}));
  }
  const captionLines=wrapText(caption ?? '',width-20,measure,14);
  const artworkHeight=Math.ceil(photos.length/3)*230;
  const height=artworkHeight+30+captionLines.length*19;
  const firstHeight=Math.min(150,186/photos[0].aspectRatio);
  return {width,height,reactionAnchor:{x:7+firstHeight*photos[0].aspectRatio,y:12},layer:group(id,0,0,[...nodes,label(id+'-photo-count',`${photos.length} photos`,width,artworkHeight,12,{textAnchor:'end',fill:'#6b7280'}),label(id+'-caption',captionLines.join('\n'),10,artworkHeight+23,14,{lineHeight:19})])};
}

export function ComposerState({id, copy='', attachment, start, end, measure, phoneWidth=390}) {
  const lines=wrapText(copy,phoneWidth-142,measure);
  fail(lines.length<=3, 'Composer exceeds three lines; shorten draft or enlarge the explicit component');
  const height=Math.max(44,lines.length*23+18)+(attachment?26:0);
  const width=phoneWidth-70, y=810-height;
  const enabled=Boolean(copy.trim() || attachment);
  const children=[
    rect(id+'-field',0,0,width,height,'#ffffff',22,{stroke:'#c9cbd0',strokeWidth:1}),
    label(id+'-input',copy?lines.join('\n'):'iMessage',14,attachment?35:10,17,{lineHeight:23,fill:copy?'#17191d':'#85858c'}),
    {id:id+'-send',type:'circle',x:width-38,y:height-36,width:30,height:30,fill:enabled?'#087ff5':'#d3d5db'},
    {id:id+'-arrow',type:'path',d:`M ${width-23} ${height-13} L ${width-23} ${height-29} M ${width-29} ${height-23} L ${width-23} ${height-29} L ${width-17} ${height-23}`,stroke:'#ffffff',strokeWidth:2,fill:'none'}
  ];
  if (attachment) children.push(label(id+'-attachment',attachment,14,9,12,{fill:'#39684c'}));
  return {enabled,height,lines,layer:group(id,52,y,children,{start,end})};
}

export function validateConversation(config) {
  const {participants,messages,composer=[],duration,fps=30,camera=[]}=config;
  fail(positive(duration) && positive(fps),'Provide positive duration and fps');
  fail(Array.isArray(participants) && participants.length>=2,'At least two participants are required');
  const ids=new Set();
  for (const actor of participants) {
    fail(typeof actor.id==='string' && /^[-a-zA-Z0-9_]+$/.test(actor.id) && !ids.has(actor.id),'Participant IDs must be unique simple identifiers');
    fail(typeof actor.name==='string' && actor.name.trim() && typeof actor.initials==='string','Participant needs a name and initials');
    ids.add(actor.id);
  }
  fail(participants.filter(actor=>actor.self).length===1,'Exactly one participant must be self');
  fail(Array.isArray(messages) && messages.length>0,'Provide messages');
  const messageIds=new Set();
  let previous=-1;
  for (const message of messages) {
    fail(typeof message.id==='string' && /^[-a-zA-Z0-9_]+$/.test(message.id) && !messageIds.has(message.id),'Message IDs must be unique simple identifiers');
    fail(ids.has(message.senderId),'Unknown message sender');
    fail(Number.isFinite(message.at) && message.at>=previous && message.at>=0 && message.at<duration,'Message times must increase within duration');
    fail((typeof message.copy==='string' && message.copy.trim()) || message.cards?.length || message.photos?.length,'Message needs copy or attachments');
    previous=message.at; messageIds.add(message.id);
    for (const reaction of message.reactions ?? []) {
      fail(ids.has(reaction.ownerId),'Unknown reaction owner');
      fail(typeof reaction.emoji==='string' && reaction.emoji.trim(),'Reaction needs an emoji');
      fail(Number.isFinite(reaction.at) && reaction.at>=message.at && reaction.at<duration,'Reaction must follow its message');
    }
  }
  previous=-1;
  fail(composer.length>0 && composer[0].at===0,'Composer states must start at zero');
  for (const state of composer) {
    fail(Number.isFinite(state.at) && state.at>previous && state.at<duration,'Composer states must increase within duration');
    fail(typeof state.copy==='string','Composer copy is required');
    if (state.sendMessageId) {
      const sent=messages.find(message=>message.id===state.sendMessageId);
      fail(sent && participants.find(actor=>actor.id===sent.senderId).self && sent.at===state.at && sent.copy===composer[composer.indexOf(state)-1]?.copy && state.copy==='','Send must transfer the prior draft once to a self message and clear composer');
    }
    previous=state.at;
  }
  previous=-1;
  for (const pose of camera) {
    fail(Number.isFinite(pose.at) && pose.at>previous && pose.at>=0 && pose.at<duration,'Camera times must increase within duration');
    fail(positive(pose.scale) && pose.scale<=3 && Number.isFinite(pose.x) && Number.isFinite(pose.y),'Camera requires finite x/y and scale in (0,3]');
    previous=pose.at;
  }
  return config;
}

export function buildConversation(config, measure) {
  validateConversation(config);
  fail(typeof measure==='function','A font measurement function is required');
  const {participants,messages,composer,duration,fps=30}=config;
  const actors=new Map(participants.map(actor=>[actor.id,actor]));
  const stageWidth=config.stageWidth ?? 540, stageHeight=stageWidth*16/9;
  fail(positive(stageWidth),'Stage width must be positive');
  const rows=[], audit=[], scroll=[{t:0,value:0}];
  let cursor=12;
  for (const message of messages) {
    const sender=actors.get(message.senderId), outgoing=Boolean(sender.self), id='msg-'+message.id;
    const displayCopy=message.link ? message.copy.replace(message.link.url,'').trimEnd() : message.copy;
    let built=message.cards ? AttachmentStack({id,cards:message.cards,switches:message.switches,measure,duration}) : message.photos ? PhotoStack({id,photos:message.photos,caption:message.caption,measure}) : Message({id,copy:displayCopy,outgoing,measure});
    if (message.link) {
      const preview=LinkPreview({id:id+'-link',...message.link,measure});
      built={...built,width:Math.max(built.width,preview.width),height:built.height+8+preview.height,layer:group(id+'-with-link',0,0,[built.layer,{...preview.layer,y:built.height+8}])};
    }
    const reactions=(message.reactions ?? []).map((reaction,index)=>({reaction,...Reaction({id:`${id}-reaction-${index}`,reaction,owner:actors.get(reaction.ownerId),outgoing:actors.get(reaction.ownerId).self,measure})}));
    const reactionHeight=reactions.length?34:0;
    const y=cursor+reactionHeight+(outgoing?0:19), x=outgoing?370-built.width:55;
    const rowChildren=[];
    if (!outgoing) rowChildren.push(Avatar({id:id+'-avatar',x:16,y:Math.max(20,built.height-28),size:27,initials:sender.initials,fill:sender.color ?? '#d9e6e4'}),label(id+'-sender',sender.name,55,reactions.length?-46:-19,12,{fill:'#72757c'}));
    rowChildren.push({...built.layer,x});
    let reactionX=outgoing?x:x+(built.reactionAnchor?.x ?? built.width)-reactions.reduce((sum,reaction)=>sum+reaction.width+3,0);
    for (const reaction of reactions) {
      rowChildren.push({...reaction.layer,x:reactionX,y:(built.reactionAnchor?.y ?? 0)-24,start:reaction.reaction.at});
      reactionX+=reaction.width+3;
    }
    rows.push(group(id+'-row',0,y,rowChildren,{start:message.at,keyframes:{y:[{t:message.at,value:y+14},{t:message.at+.24,value:y,ease:'easeOut'}],opacity:[{t:message.at,value:0},{t:message.at+.16,value:1,ease:'easeOut'}]}}));
    cursor=y+built.height+19;
    const offset=-Math.max(0,cursor-574);
    if (message.at>0) scroll.push({t:message.at,value:scroll.at(-1).value,ease:'hold'},{t:message.at+.3,value:offset,ease:'easeOut'});
    else scroll[0].value=offset;
    audit.push({id:message.id,senderId:sender.id,x,y,width:built.width,height:built.height,lines:built.lines,reactions:reactions.map(r=>({ownerId:r.reaction.ownerId,messageId:message.id,at:r.reaction.at})),scroll:offset});
  }
  const drafts=composer.map((state,index)=>({...ComposerState({id:'draft-'+index,copy:state.copy,attachment:state.attachment,start:state.at,end:composer[index+1]?.at ?? duration,measure}),at:state.at,copy:state.copy}));
  const titleLines=wrapText(config.title ?? 'A conversation',250,measure,16,600);
  fail(titleLines.length<=2,'Conversation title exceeds two lines');
  const phone=group('phone',stageWidth/2-195,stageHeight/2-422,[
    rect('phone-shell',-6,-6,402,856,'#1d2228',49),rect('phone-paper',0,0,390,844,'#ffffff',44),
    group('phone-screen',0,0,[
      group('transcript-viewport',0,112,[group('transcript-scroll',0,0,rows,{keyframes:{y:scroll}})],{clip:{x:8,y:0,width:374,height:594}}),
      rect('header',0,0,390,112,'#f7f8fa'),label('clock','9:41',29,19,14,{fontWeight:600}),label('status','5G  ▰',307,19,12),
      rect('island',140,12,110,28,'#111419',15),label('back','‹',20,54,34,{fill:'#087ff5'}),
      label('conversation-title',titleLines.join('\n'),195,62,16,{fontWeight:600,textAnchor:'middle',lineHeight:20}),
      rect('header-line',0,111,390,1,'#e4e5e8'),
      rect('composer-matte',0,706,390,138,'#ffffff'),label('plus','+',17,775,29,{fill:'#85858c'}),
      ...drafts.map(draft=>draft.layer),rect('home-indicator',128,830,134,5,'#111419',3)
    ],{clip:{x:0,y:0,width:390,height:844,radius:44}})
  ]);
  const camera=config.camera?.length ? config.camera : [{at:0,x:0,y:0,scale:1}];
  const tracks=property=>camera.map(pose=>({t:pose.at,value:pose[property],ease:'easeInOut'}));
  const width=config.width ?? 1080,height=config.height ?? 1920;
  fail(Number.isInteger(width) && Number.isInteger(height) && width>0 && height>0,'Output dimensions must be positive integers');
  const fit=Math.min(width/stageWidth,height/stageHeight);
  const scene={width,height,fps,duration,background:'#edf2f4',title:config.title,
    source:{notes:'Authored Messages-inspired UI, not a measured iOS recreation. 390×844 logical-point iPhone 13-class proportions; desktop Chromium/macOS render. No native device/OS gesture fidelity claimed. Arial and Apple Color Emoji require remeasurement when replaced.'},
    layers:[group('output-fit',(width-stageWidth*fit)/2,(height-stageHeight*fit)/2,[CameraRig({id:'conversation-camera',originX:stageWidth/2,originY:stageHeight/2,children:[phone],keyframes:{x:tracks('x'),y:tracks('y'),scaleX:tracks('scale'),scaleY:tracks('scale')}})],{scaleX:fit,scaleY:fit})]};
  return {scene,audit:{messages:audit,composer:drafts.map(({at,copy,enabled,height,lines})=>({at,copy,enabled,height,lines})),font:FONT,measurement:'CanvasRenderingContext2D.measureText',nativeGestureClaims:false}};
}
