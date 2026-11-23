/** Adaptable choreography. Timing below is authored starter timing, not a
 * measurement of the six reference films. See catalogue.json for measured evidence.
 */
import {TOKENS,MessageBubble,Composer,AppIcon,AppCard,BottomSheet,PhoneFrame,ActionButton,Avatar,CameraRig,rect,text,group} from './components.mjs';
import {stateAt} from '../scripts/engines/common.mjs';
export const MOTIFS=Object.freeze(['message-wall','conversation-handoff','mini-app-expand','app-drawer','identity-morph','circle-to-panel','selection-confirm','camera-focus','card-orbit']);
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const k=(t,value,ease='easeInOut')=>({t,value,ease});
const pulse=(start,end,value=1)=>[k(0,0),k(start,0),k(end,value,'easeOut')];

export function buildMotion(motif,options={}){
  if(!MOTIFS.includes(motif))throw Error('Unknown motion motif');
  const duration=options.duration??4;
  if(!Number.isFinite(duration)||duration<2||duration>12)throw Error('Duration must be 2–12 seconds');
  const fps=options.fps??30;if(![24,25,30,60].includes(fps))throw Error('Unsupported starter frame rate');
  const d=duration,copy=Array.from(String(options.copy??'Can you book a table?')).slice(0,72).join(''),title=Array.from(String(options.title??'Friday dinner')).slice(0,36).join(''),color=/^#[0-9a-f]{6}$/i.test(options.color??'')?options.color:TOKENS.blue;
  const layers=[],events=[];let description='';
  const addEvent=(t,kind,target)=>{const frame=Math.ceil(t*fps-1e-8);events.push({frame,time:frame/fps,kind,target,evidence:'authored starter UI action; not a measured source cue'});};
  if(motif==='message-wall'){
    if(!Number.isFinite(options.count??9))throw Error('Message count must be finite');
    const count=clamp(Math.round(options.count??9),3,15),nodes=[];
    for(let i=0;i<count;i++){
      const col=i%3,row=Math.floor(i/3),x=18+col*302,y=26+row*114;
      const b=MessageBubble({id:'wall-message-'+i,x,y,width:264,height:80,copy:i===0?copy:['On it.','Your table is ready.','Let’s make it happen.'][i%3],side:i%3?'incoming':'outgoing',fill:i%3?undefined:color,fontSize:18});
      const start=.05*d+i*.025*d;
      b.keyframes={y:[k(start,y+55),k(start+.14*d,y,'easeOut')],opacity:pulse(start,start+.1*d)};nodes.push(b);
    }
    layers.push(CameraRig({children:nodes,keyframes:{y:[k(0,130),k(.7*d,-35),k(d,-65)],scaleX:[k(0,.9),k(d,1.02)],scaleY:[k(0,.9),k(d,1.02)]}}));
    description='Many conversations imply reach; one camera carries the whole field.';
    // A montage of already-existing messages is not a series of new sends.
  } else if(motif==='conversation-handoff'){
    const children=[Avatar({id:'contact',x:23,y:92,initials:'AI'})];
    const chars=Array.from(copy),hasInput=copy.trim().length>0;
    const typed=Composer({id:'composer',x:20,y:428,width:400,copy:'',active:hasInput});
    typed.children.find(x=>x.id==='composer-input').keyframes={text:[k(0,''),...chars.map((_,i)=>k((.1+.26*(i+1)/chars.length)*d,chars.slice(0,i+1).join(''),'hold')),k(.44*d,'','hold')]};
    const out=MessageBubble({id:'sent',x:143,y:294,width:272,height:72,copy,fill:color,fontSize:17});
    out.keyframes={y:[k(.44*d,365),k(.58*d,294,'easeOut')],opacity:pulse(.44*d,.48*d)};
    const incoming=MessageBubble({id:'reply',x:22,y:95,width:280,height:82,copy:'A table for two.\nReady to confirm?',side:'incoming',fontSize:17});
    incoming.keyframes={opacity:pulse(.7*d,.76*d),y:[k(.7*d,115),k(.84*d,95,'easeOut')]};
    if(hasInput)children.push(out,incoming);children.push(typed);layers.push(PhoneFrame({id:'phone',x:260,y:18,title:'Your assistant',children}));
    const input=typed.children.find(x=>x.id==='composer-input');let previous='';
    for(let frame=0;frame<Math.round(d*fps);frame++){
      const value=String(stateAt(input,frame/fps).text??'');
      if(value&&value!==previous){addEvent(frame/fps,'typing','composer-input');events.at(-1).observed_character_delta=Array.from(value).length-Array.from(previous).length;}
      previous=value;
    }
    if(hasInput){addEvent(.44*d,'message_send','sent');addEvent(.7*d,'message_arrival','reply');}
    description='Typed input becomes a sent message; the reply arrives without fake AI keystrokes.';
  } else if(motif==='mini-app-expand'){
    const card=AppCard({id:'mini-app',x:36,y:180,width:368,height:240,title,detail:'For two · 7:00 PM',action:'Reserve',color:'#e1eddc'});
    card.keyframes={y:[k(0,220),k(.45*d,154),k(.8*d,154)],scaleX:[k(0,.58),k(.45*d,1)],scaleY:[k(0,.58),k(.45*d,1)],originX:[k(0,184)],originY:[k(0,240)],opacity:pulse(0,.12*d)};
    layers.push(PhoneFrame({id:'phone',x:260,y:18,children:[MessageBubble({id:'request',x:142,y:90,width:270,height:62,copy:'Find a table for two.',fill:color,fontSize:17}),card,Composer({id:'composer',x:20,y:428,width:400,active:false})]}));
    addEvent(0,'panel_open','mini-app');description='A useful action expands inside its conversation; keep the parent context visible.';
  } else if(motif==='app-drawer'){
    const icons=Array.from({length:6},(_,i)=>AppIcon({id:'app-'+i,x:22+(i%3)*132,y:92+Math.floor(i/3)*106,size:64,color:['#252a31',color,'#6e9c74'][i%3],label:['A','B','C','D','E','F'][i]}));
    const sheet=BottomSheet({id:'drawer',x:5,y:205,width:430,height:300,children:icons});
    sheet.keyframes={y:[k(0,500),k(.42*d,205,'easeOut')]};
    layers.push(PhoneFrame({id:'phone',x:260,y:18,children:[MessageBubble({id:'message',x:135,y:100,width:276,height:64,copy:'Everything, right here.',fill:color,fontSize:17}),sheet]}));
    addEvent(0,'panel_open','drawer');description='Reveal available tools as one sheet rather than unrelated floating screens.';
  } else if(motif==='identity-morph'){
    const surface=rect('identity-surface',0,0,128,128,color,64,{keyframes:{x:[k(0,416),k(.55*d,396)],y:[k(0,206),k(.55*d,186)],width:[k(0,128),k(.55*d,168)],height:[k(0,128),k(.55*d,168)],radius:[k(0,64),k(.55*d,34)],fill:[k(0,color),k(.55*d,'#17252c')]}});
    const oldMark={id:'identity-old-mark',type:'path',x:480,y:270,d:'M -22 0 L -6 16 L 24 -18',fill:'none',stroke:'#ffffff',strokeWidth:7,keyframes:{opacity:[k(0,1),k(.25*d,1),k(.48*d,0)]}};
    const newMark=text('identity-new-mark','A',480,235,64,{fill:'#ffffff',textAnchor:'middle',fontWeight:600,keyframes:{opacity:pulse(.38*d,.6*d)}});
    layers.push(surface,oldMark,newMark);description='A neutral identity study: surface geometry, material and internal mark have separate tracks. Source Poke uses its own measured palm-tree silhouette poses.';
  } else if(motif==='circle-to-panel'){
    // Maintain one physical surface: radius and dimensions change together.
    const surface=rect('morph-surface',0,0,128,128,color,64,{keyframes:{x:[k(0,416),k(.6*d,280)],y:[k(0,206),k(.6*d,126)],width:[k(0,128),k(.6*d,400)],height:[k(0,128),k(.6*d,288)],radius:[k(0,64),k(.6*d,26)]}});
    const contents=group('morph-contents',304,154,[text('morph-title',title,0,0,30,{fill:'#ffffff',fontWeight:600}),text('morph-detail','From a small action\nto something useful.',0,55,21,{fill:'#ffffff',lineHeight:29}),ActionButton({id:'morph-action',x:0,y:166,width:352,copy:'Open app',fill:'#172c45'})],{keyframes:{opacity:pulse(.48*d,.7*d)}});
    layers.push(surface,contents);addEvent(0,'tap','morph-surface');description='One surface changes size and corner radius before content becomes readable.';
  } else if(motif==='selection-confirm'){
    const card=AppCard({id:'selection-card',x:300,y:124,width:360,height:280,title,detail:'For two · Friday',action:'Confirm',color:'#edf0e6'});
    const action=card.children.find(l=>l.id==='selection-card-action');
    action.children[0].keyframes={fill:[k(0,color),k(.46*d,color,'hold'),k(.5*d,'#193627'),k(.57*d,'#3f8057')]};
    action.children[1].keyframes={text:[k(0,'Confirm'),k(.57*d,'Confirmed','hold')]};
    layers.push(card);addEvent(.46*d,'tap','selection-card-action');description='Preserve the same control through press, result and confirmation; no duplicate action actor.';
  } else if(motif==='camera-focus'){
    const card=AppCard({id:'focus-card',x:310,y:150,width:340,height:240,title,detail:'The meaningful detail',action:'View booking'});
    layers.push(CameraRig({children:[rect('context-plane',90,65,780,425,'#eef0f2',28),MessageBubble({id:'context-message',x:120,y:90,width:260,height:62,copy:'Here is the result.',side:'incoming',fontSize:17}),card],keyframes:{scaleX:[k(0,.72),k(.55*d,1.15)],scaleY:[k(0,.72),k(.55*d,1.15)],y:[k(0,0),k(.55*d,-30)]}}));
    description='A camera moves toward a stable object; typography and card layout keep local dimensions.';
  } else if(motif==='card-orbit'){
    const cards=Array.from({length:3},(_,i)=>{
      const c=AppCard({id:'orbit-card-'+i,x:110+i*245,y:172,width:235,height:205,title:['Dinner','A show','A weekend'][i],detail:'Made for your plans',action:'Explore',color:['#e6e6d6','#ecd9d1','#d8e6e9'][i]});
      c.originX=117;c.originY=102;c.keyframes={x:[k(0,30+i*310),k(.55*d,110+i*245)],y:[k(0,360-i*60),k(.55*d,172+i%2*22)],rotation:[k(0,(i-1)*-16),k(.55*d,(i-1)*7)],opacity:pulse(i*.07*d,(.18+i*.07)*d)};return c;
    });layers.push(...cards);description='A bounded set of independent cards converges into a readable product family.';
  }
  const scene={width:960,height:540,fps,duration,background:TOKENS.paper,title:motif,source:{notes:'New reusable starter, not an exact reference recreation. Arial fallback; replace and remeasure typography for production.'},layers};
  return {scene,events,description,provenance:'new adaptable choreography',options:{...options,duration,fps}};
}
