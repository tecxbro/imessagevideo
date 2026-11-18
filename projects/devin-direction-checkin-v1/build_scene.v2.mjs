import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {rect, text, group, MessageBubble, Composer, Avatar, BottomSheet, CameraRig} from '../../skill/imessage-motion-recreation/director/components.mjs';
import {stateAt} from '../../skill/imessage-motion-recreation/scripts/engines/common.mjs';

export const CONFIG = {
  width:1920,height:1080,fps:30,frames:840,
  names:{sender:'Maya',friend:'Sam'},
  copy:{ask:"Text me when you're home?",title:'Check In',mode:'When I Arrive',destination:'Home · Walking',eta:'About {min} min',received:'Check In · Maya · Home',arrived:'Arrived',arrival:'Maya has arrived · 12:00',completed:'✓  Completed',date:'Today 11:42 PM',home:'Home',draft:'are you home yet?',heart:'❤️',end:'Check In. Right in Messages.',placeholder:'iMessage',apps:['Photos','Camera','Location','Check In']},
  times:{ask:12,plus:90,sheet:96,sheetUp:120,row:132,draft:140,draftIn:165,send:186,sent:204,pull:210,pullEnd:265,route:230,routeEnd:405,reveal:420,center:444,typeStart:445,typeEnd:560,home:575,arrival:580,deleteStart:608,deleteEnd:661,heartSend:690,heartReceive:735,end:750,settle:800,tapDuration:12,flightDuration:15,askMove:12,askFade:7},
  typingGaps:[6,8,5,12,6,7,10,5,7,6,9,5,8,6,7,8],
  eta:[{frame:204,min:18,clock:'11:42'},{frame:250,min:15,clock:'11:45'},{frame:280,min:12,clock:'11:48'},{frame:310,min:9,clock:'11:51'},{frame:340,min:6,clock:'11:54'},{frame:370,min:3,clock:'11:57'},{frame:400,min:1,clock:'11:59'},{frame:575,min:1,clock:'12:00'}],
  colors:{background:'#F1F0ED',blue:'#0A84FF',incoming:'#E9E9EB',ink:'#17181C',muted:'#85858B',green:'#24834B',greenLight:'#E9F6ED',bezel:'#18191D',line:'#D9D9DE',white:'#FFFFFF'},
  layout:{mayaX:520,mayaWalkX:520,samX:1900,phoneY:80,routeY:650,homeX:1770,homeY:532.5},
  camera:[{f:0,s:1.6,x:-304,y:-75},{f:74,s:1.6,x:-304,y:-105},{f:120,s:1.4,x:-146,y:-550},{f:186,s:1.4,x:-146,y:-535},{f:209,s:1.4,x:-146,y:-220},{f:265,s:.82,x:-240,y:70},{f:419,s:.84,x:-252,y:58},{f:444,s:1.35,x:-1950.6,y:-470},{f:560,s:1.35,x:-1950.6,y:-470},{f:608,s:1.35,x:-1950.6,y:-468},{f:705,s:1.35,x:-1950.6,y:-466},{f:735,s:.8,x:-175,y:0},{f:780,s:.8,x:-175,y:0},{f:839,s:.81,x:-194,y:-8}],
  presence:{maya:[[0,1],[420,1],[424,0],[728,0],[735,1]],sam:[[0,0],[420,0],[432,1]]},
};
const C=CONFIG.colors,T=CONFIG.times,P=CONFIG.copy;
const seconds=f=>f/CONFIG.fps;
const key=(f,value,ease='easeInOut')=>({t:seconds(f),value,ease});
const track=entries=>entries.map(([f,v,e])=>key(f,v,e));
const txt=(id,value,x,y,size=24,extra={})=>text(id,value,x,y,size,{fill:C.ink,...extra});
const circle=(id,x,y,size,fill,extra={})=>({id,type:'circle',x,y,width:size,height:size,fill,...extra});
const line=(id,d,stroke,width=3,extra={})=>({id,type:'path',d,fill:'none',stroke,strokeWidth:width,...extra});
const eventsOn=(layer,events)=>Object.assign(layer,{events});
const show=(layer,frame)=>Object.assign(layer,{start:seconds(frame)});
const tap=(id,x,y,frame)=>eventsOn(group(id,x,y,[circle(id+'-ring',-27,-27,54,'none',{stroke:C.blue,strokeWidth:3})],{start:seconds(frame),end:seconds(frame+T.tapDuration),originX:0,originY:0,keyframes:{scaleX:track([[frame,.7],[frame+T.tapDuration,1.5]]),scaleY:track([[frame,.7],[frame+T.tapDuration,1.5]]),opacity:track([[frame,.75],[frame+T.tapDuration,0]])}}),[{frame,action:'tap',target:id}]);
const arrivalKeys=(before,after)=>[key(0,before,'hold'),key(T.arrival,after,'hold')];

function checkCard(id,received=false){
  const title=received?P.received:P.title;
  const width=received?390:340;
  const outgoingX=512-28-width;
  const card=group(id,received?32:outgoingX,received?320:580,[
    rect(id+'-surface',0,0,width,222,'#F2F5FA',25,{stroke:'#D9E1EC',strokeWidth:1.5,keyframes:{fill:arrivalKeys('#F2F5FA',C.greenLight)}}),
    circle(id+'-icon',20,20,40,C.blue,{keyframes:{fill:arrivalKeys(C.blue,C.green)}}),
    line(id+'-check','M 31 40 L 38 47 L 50 32',C.white,3),
    txt(id+'-title',title,72,26,received?23:28,{fontWeight:700}),
    txt(id+'-mode',P.mode,22,82,29,{fontWeight:700,keyframes:{text:arrivalKeys(P.mode,P.arrived),fill:arrivalKeys(C.ink,C.green)}}),
    txt(id+'-destination',P.destination,22,125,24,{fill:'#555C66',keyframes:{text:arrivalKeys(P.destination,P.arrival),fontSize:arrivalKeys(24,23)}}),
    txt(id+'-eta',P.eta.replace('{min}',CONFIG.eta[0].min),22,174,25,{fill:C.blue,keyframes:{text:[...CONFIG.eta.map(e=>key(e.frame,P.eta.replace('{min}',e.min),'hold')),key(T.arrival,P.completed,'hold')],fill:arrivalKeys(C.blue,C.green)}}),
    txt(id+'-chevron','›',width-40,175,27,{fill:C.muted}),
  ]);
  if(!received){
    card.start=seconds(T.draft);
    card.keyframes={x:track([[T.draft,outgoingX],[T.send,outgoingX],[T.sent,outgoingX]]),y:track([[T.draft,925],[T.draftIn,580],[T.send,580],[T.sent,320]]),scaleX:track([[T.draft,.93],[T.draftIn,1]]),scaleY:track([[T.draft,.93],[T.draftIn,1]])};
    eventsOn(card,[{frame:T.draft,action:'draft appears',target:id},{frame:T.send,action:'send',target:id},{frame:T.arrival,action:'arrival',target:id}]);
  }else {
    card.keyframes={y:track([[T.reveal,320],[T.center,400]])};
    eventsOn(card,[{frame:T.reveal,action:'receive',target:id},{frame:T.arrival,action:'arrival',target:id}]);
  }
  return card;
}

function phone(id,x,name,isMaya){
  const threadId=isMaya?'threadMaya':'threadSam';
  const composer=Composer({id:id+'-composer',x:88,y:846,width:394,active:true});
  composer.children.find(l=>l.id.endsWith('-input')).text=P.placeholder;
  composer.children.find(l=>l.id.endsWith('-input')).fontSize=24;
  composer.children.find(l=>l.id.endsWith('-input')).y=10;
  const plus=group(id+'-plus',34,850,[circle(id+'-plus-bg',0,0,40,'#EDEDF0'),txt(id+'-plus-label','+',20,-1,35,{textAnchor:'middle',fill:'#77777D'})]);
  const children=[
    rect(id+'-screen-paper',0,0,512,916,C.white,48),
    txt(isMaya?'clockMaya':'clockSam','11:42',36,22,23,{fontWeight:700,keyframes:{text:CONFIG.eta.map(e=>key(e.frame,e.clock,'hold'))}}),
    rect(id+'-island',179,12,154,35,'#101115',18),
    ...[0,1,2,3].map(i=>rect(id+'-signal-'+i,405+i*6,37-i*4,4,6+i*4,C.ink,1)),
    rect(id+'-battery',442,25,30,15,'none',4,{stroke:C.ink,strokeWidth:1.5}),rect(id+'-charge',445,28,23,9,C.ink,2),
    txt(id+'-back','‹',22,75,50,{fill:C.blue}),
    Avatar({id:id+'-avatar',x:231,y:66,size:50,initials:name.slice(0,1),fill:'#BABCC4'}),
    txt(id+'-name',name,256,123,23,{textAnchor:'middle',fontWeight:600}),txt(id+'-name-arrow','›',292,122,23,{fill:C.muted}),
    rect(id+'-header-line',0,163,512,1,'#EEEEF0'),
    txt(id+'-date',P.date,256,190,18,{textAnchor:'middle',fill:C.muted}),
    group(threadId,0,0,[]),composer,plus,
    rect(id+'-home-indicator',162,898,188,6,'#111216',3),
  ];
  const thread=children.find(l=>l.id===threadId);
  if(isMaya){
    const ask=MessageBubble({id:'bubbleAsk',x:26,y:240,width:371,height:64,side:'incoming',copy:P.ask,fill:C.incoming,fontSize:26});
    ask.start=seconds(T.ask);ask.keyframes={y:track([[T.ask,275],[T.ask+T.askMove,240]]),opacity:track([[T.ask,0],[T.ask+T.askFade,1]])};
    eventsOn(ask,[{frame:T.ask,action:'receive',target:'bubbleAsk'}]);
    thread.children.push(ask,checkCard('cardMaya'));
    const sheet=BottomSheet({id:'sheetApps',x:12,y:920,width:488,height:378,title:'',children:[]});
    sheet.children=sheet.children.filter(l=>!l.id.endsWith('-heading'));
    sheet.start=seconds(T.sheet);sheet.end=seconds(T.draft);
    sheet.keyframes={y:track([[T.sheet,920],[T.sheetUp,454],[T.row,454],[T.draft,920]])};
    P.apps.forEach((label,i)=>{
      const row=group(i===3?'rowCheckIn':'row-'+i,18,38+i*78,[rect('row-bg-'+i,0,0,452,74,'#F5F5F7',16,{keyframes:i===3?{fill:track([[T.row-1,'#F5F5F7','hold'],[T.row,'#D9DBDF','hold']])}:{}}),circle('row-icon-'+i,12,12,49,[C.blue,'#66686E','#35A56B','#E8A229'][i]),txt('row-mark-'+i,['✿','●','↗','✓'][i],36,17,28,{textAnchor:'middle',fill:C.white}),txt('row-label-'+i,label,82,21,27,{fontWeight:600})]);
      sheet.children.push(row);
    });
    children.push(sheet,tap('tapPlus',54,870,T.plus),tap('tapCheckIn',244,762,T.row),tap('tapSend',458,870,T.send));
    const receivedHeart=heart('bubbleHeart',false,T.heartReceive);
    thread.children.push(receivedHeart);
  }else{
    const earlierQuestion=MessageBubble({id:'bubbleAskSam',x:114,y:240,width:371,height:64,side:'outgoing',copy:P.ask,fill:C.blue,fontSize:26});
    earlierQuestion.keyframes={y:track([[T.reveal,240],[T.center,160]])};
    thread.children.push(earlierQuestion);
    thread.children.push(checkCard('cardSam',true),heart('bubbleHeartSam',true,T.heartSend));
    const draft=txt('draftSam','',106,853,32);
    const gapTotal=CONFIG.typingGaps.reduce((a,b)=>a+b,0);
    const typing=Array.from(P.draft).map((char,i)=>({frame:T.typeStart+Math.round(CONFIG.typingGaps.slice(0,i).reduce((a,b)=>a+b,0)/gapTotal*(T.typeEnd-T.typeStart)),value:Array.from(P.draft).slice(0,i+1).join(''),action:'type char',char}));
    const deleting=Array.from(P.draft).map((char,i)=>({frame:Math.round(T.deleteStart+i*(T.deleteEnd-T.deleteStart)/(P.draft.length-1)),value:Array.from(P.draft).slice(0,P.draft.length-i-1).join(''),action:'backspace',char:Array.from(P.draft).at(-i-1)}));
    draft.keyframes={text:[key(0,'','hold'),...typing.concat(deleting).map(e=>key(e.frame,e.value,'hold'))]};
    eventsOn(draft,typing.concat(deleting).map(({frame,action,char})=>({frame,action,char,target:'draftSam'})));
    composer.children.find(l=>l.id.endsWith('-input')).keyframes={opacity:track([[0,1,'hold'],[T.typeStart,0,'hold'],[T.deleteEnd,1,'hold']])};
    children.push(draft,tap('tapHeartSend',458,870,T.heartSend));
  }
  return group(id,x,CONFIG.layout.phoneY,[rect(id+'-rim',-14,-14,540,944,'#424349',62,{stroke:'#9B9CA1',strokeWidth:2,shadow:{x:0,y:22,blur:30,color:'#00000025'}}),rect(id+'-bezel',-9,-9,530,934,C.bezel,58),group(id+'-screen',0,0,children,{clip:{x:0,y:0,width:512,height:916,radius:48}})]);
}
function heart(id,outgoing,frame){
  const b=MessageBubble({id,x:outgoing?326:28,y:665,width:158,height:116,side:outgoing?'outgoing':'incoming',copy:'',fill:outgoing?C.blue:C.incoming});
  b.children.push(txt(id+'-glyph',P.heart,39,9,76,{fontFamily:'Arial, Apple Color Emoji, sans-serif'}));
  b.start=seconds(frame);b.keyframes={y:track([[frame,730],[frame+T.flightDuration,665]])};
  return eventsOn(b,[{frame,action:outgoing?'send':'receive',target:id}]);
}

const L=CONFIG.layout;
const maya=phone('phoneMaya',L.mayaX,CONFIG.names.friend,true);
maya.keyframes={x:track([[0,L.mayaX],[T.pull,L.mayaX],[T.pullEnd,L.mayaWalkX],[T.reveal-1,L.mayaWalkX],[T.center,L.mayaX]]),opacity:track(CONFIG.presence.maya)};
const sam=phone('phoneSam',L.samX,CONFIG.names.sender,false);
sam.keyframes={opacity:track(CONFIG.presence.sam)};
const routePoints=Array.from({length:48},(_,i)=>({x:L.mayaWalkX+540+i/47*(L.homeX-L.mayaWalkX-540),y:L.routeY-Math.sin(i/47*Math.PI)*120+i/47*(L.homeY-L.routeY)}));
const route=group('route',0,0,routePoints.map((p,i)=>show(circle('route-dot-'+i,p.x,p.y,8,'#A7B8AB',{keyframes:{x:track([[T.reveal-1,p.x],[T.center,p.x+(L.mayaX-L.mayaWalkX)*(1-i/47)]])}}),Math.round(T.route+i*(T.routeEnd-T.route)/47))));
const walkerKeys=routePoints.map((p,i)=>{
  const frame=Math.round(T.route+i*(T.home-T.route)/47);
  const shift=stateAt(maya,seconds(frame)).x-L.mayaWalkX;
  return {frame,x:p.x+shift*(1-i/47),y:p.y};
});
const walker=group('walker',0,0,[circle('walker-halo',-32,-32,64,'#FFFFFF'),circle('walker-core',-21,-21,42,C.blue)],{start:seconds(T.route),end:seconds(T.arrival),keyframes:{x:walkerKeys.map(p=>key(p.frame,p.x)),y:walkerKeys.map(p=>key(p.frame,p.y))}});
eventsOn(walker,[{frame:T.home,action:'arrival',target:'homePin'}]);
const hp=routePoints.at(-1);
const home=show(group('homePin',hp.x-33,hp.y-33,[circle('home-disc',0,0,66,C.white,{stroke:'#DCE4DC',strokeWidth:2}),line('home-roof','M 15 31 L 33 15 L 51 31',C.green,4),line('home-walls','M 20 28 L 20 48 L 46 48 L 46 28 M 30 48 L 30 36 L 37 36 L 37 48',C.green,3),txt('home-label',P.home,33,-43,28,{textAnchor:'middle',fill:C.green,fontWeight:600})]),T.route);
const cam=CameraRig({id:'camera',originX:0,originY:0,children:[route,home,walker,maya,sam],keyframes:{x:CONFIG.camera.map(c=>key(c.f,c.x)),y:CONFIG.camera.map(c=>key(c.f,c.y)),scaleX:CONFIG.camera.map(c=>key(c.f,c.s)),scaleY:CONFIG.camera.map(c=>key(c.f,c.s))}});
const endLine=show(txt('endLine',P.end,960,936,66,{textAnchor:'middle',fontWeight:600,keyframes:{opacity:track([[T.end,0],[T.end+15,1]])}}),T.end);
const endMark=show(group('endMark',960,490,[rect('mark-green',-70,-70,140,140,C.green,36),{id:'mark-bubble',type:'path',d:'M -38 -30 H 38 Q 46 -30 46 -22 V 20 Q 46 30 36 30 H -12 L -36 47 L -31 30 H -38 Q -46 30 -46 20 V -22 Q -46 -30 -38 -30 Z',fill:C.white},...[-20,0,20].map((x,i)=>circle('mark-dot-'+i,x-5,-5,10,C.green))],{keyframes:{opacity:track([[T.end,0],[T.end+15,1]]),scaleX:track([[T.end,1.16],[CONFIG.frames-1,1]]),scaleY:track([[T.end,1.16],[CONFIG.frames-1,1]]),rotation:track([[T.end,-6],[CONFIG.frames-1,0]]),y:track([[T.end,510],[CONFIG.frames-1,490]])}}),T.end);
const scene={width:CONFIG.width,height:CONFIG.height,fps:CONFIG.fps,duration:CONFIG.frames/CONFIG.fps,background:C.background,title:'Check In — One thread, one walk (v2)',source:{notes:'Authored v2 revision: readable worry draft, outgoing card, closer walking composition and live authored end mark. Arial fallback; no Apple artwork or SF Symbols. Silent picture.'},layers:[group('world',0,0,[cam]),endLine,endMark]};
const walk=layers=>layers.flatMap(l=>[l,...walk(l.children??[])]);
const all=walk(scene.layers);
if(new Set(all.map(l=>l.id)).size!==all.length)throw Error('Duplicate actor IDs');
function eventFrame(layer,event){
  if(event.action==='tap'||event.action==='draft appears'||['bubbleAsk','bubbleHeart','bubbleHeartSam'].includes(layer.id))return Math.round(layer.start*scene.fps);
  if(event.action==='type char'||event.action==='backspace'){
    const changes=layer.keyframes.text.slice(1).filter((k,i)=>{
      const previous=layer.keyframes.text[i].value;
      return event.action==='type char'?k.value.length>previous.length:k.value.length<previous.length;
    });
    const index=layer.events.filter(e=>e.action===event.action).indexOf(event);
    return Math.round(changes[index].t*scene.fps);
  }
  if(event.action==='send')return Math.round(layer.keyframes.y.at(-2).t*scene.fps);
  if(event.action==='arrival'){
    const anchor=layer.id==='walker'?layer.keyframes.x.at(-1):layer.children.find(l=>l.id===layer.id+'-mode').keyframes.text.at(-1);
    return Math.round(anchor.t*scene.fps);
  }
  if(layer.id==='cardSam'&&event.action==='receive'){
    for(let frame=0;frame<CONFIG.frames;frame++){
      const t=frame/scene.fps,camera=stateAt(cam,t),phoneState=stateAt(sam,t),cardState=stateAt(layer,t);
      const left=camera.x+camera.scaleX*(phoneState.x+cardState.x);
      if(phoneState.opacity>.05&&left<scene.width&&left+camera.scaleX*390>0)return frame;
    }
    throw Error('Receiving card is never revealed');
  }
  throw Error('No generated scene anchor for '+layer.id);
}
const events=all.flatMap(layer=>(layer.events??[]).map(e=>{
  const frame=eventFrame(layer,e),time=frame/scene.fps,s=stateAt(layer,time);
  if(time<(s.start??0)||time>=(s.end??scene.duration))throw Error('Inactive event actor '+layer.id);
  return {...e,frame,actor:layer.id};
})).sort((a,b)=>a.frame-b.frame);
const byFrame={};for(const e of events)(byFrame[e.frame]??=[]).push(e);
const output=path.dirname(fileURLToPath(import.meta.url));
fs.writeFileSync(path.join(output,'scene.json'),JSON.stringify(scene,null,2)+'\n');
fs.writeFileSync(path.join(output,'events.json'),JSON.stringify({fps:scene.fps,frames:CONFIG.frames,events:byFrame},null,2)+'\n');
console.log(JSON.stringify({layers:all.length,frames:CONFIG.frames,events:events.length,output}));
