/** Editable starter components. Coordinates in a 960x540 design space.
 * These are new reusable designs, not traced/proprietary source UI assets.
 * All builders emit the same measured-scene contract consumed by the engines.
 */
export const TOKENS=Object.freeze({paper:'#f7f7f5',ink:'#17191d',muted:'#777b84',blue:'#1688fa',incoming:'#e9e9ed',line:'#d8dbe0',font:'Arial, sans-serif'});
const finite=(n,label,min=0,max=10000)=>{if(!Number.isFinite(n)||n<min||n>max)throw Error(`Invalid ${label}`);return n;};
const safeId=id=>{if(typeof id!=='string'||!/^[-a-zA-Z0-9_]+$/.test(id))throw Error('Use a unique simple component id');return id;};
const rect=(id,x,y,width,height,fill,radius=0,extra={})=>({id,type:'rect',x,y,width,height,fill,radius,...extra});
const text=(id,value,x,y,size=18,extra={})=>({id,type:'text',text:String(value),x,y,fontSize:size,fontFamily:TOKENS.font,fill:TOKENS.ink,...extra});
const group=(id,x,y,children,extra={})=>({id:safeId(id),type:'group',x,y,children,...extra});
export {rect,text,group};

export function MessageBubble({id,x=0,y=0,width=248,height=70,side='outgoing',copy='Can you book it?',tail=true,fill,fontSize=19}){
  safeId(id);finite(width,'bubble width',80);finite(height,'bubble height',38);
  if(!['incoming','outgoing'].includes(side))throw Error('Invalid message side');
  const color=fill??(side==='outgoing'?TOKENS.blue:TOKENS.incoming);
  const nodes=[rect(id+'-body',0,0,width,height,color,20)];
  if(tail){const d=side==='outgoing'?`M ${width-16} ${height-18} Q ${width-3} ${height+1} ${width+7} ${height-2} Q ${width-3} ${height-6} ${width-2} ${height-20} Z`:`M 16 ${height-18} Q 3 ${height+1} -7 ${height-2} Q 3 ${height-6} 2 ${height-20} Z`;nodes.push({id:id+'-tail',type:'path',d,fill:color});}
  nodes.push(text(id+'-copy',copy,17,14,fontSize,{fill:side==='outgoing'?'#ffffff':TOKENS.ink,lineHeight:24}));
  return group(id,x,y,nodes);
}
export function ActionButton({id,x=0,y=0,width=140,height=42,copy='Continue',fill=TOKENS.blue}){
  return group(id,x,y,[rect(id+'-shape',0,0,width,height,fill,height/2),text(id+'-label',copy,width/2,11,16,{fill:'#ffffff',textAnchor:'middle',fontWeight:600})]);
}
export function Composer({id,x=0,y=0,width=430,copy='',active=true}){
  return group(id,x,y,[rect(id+'-field',0,0,width,48,'#ffffff',24,{stroke:TOKENS.line,strokeWidth:1}),text(id+'-input',copy||'Message',18,14,17,{fill:copy?TOKENS.ink:TOKENS.muted}),
    {id:id+'-send',type:'circle',x:width-40,y:8,width:32,height:32,fill:active?TOKENS.blue:TOKENS.line},
    {id:id+'-arrow',type:'path',d:`M ${width-24} 33 L ${width-24} 16 M ${width-31} 23 L ${width-24} 16 L ${width-17} 23`,fill:'none',stroke:'#ffffff',strokeWidth:2}]);
}
export function AppIcon({id,x=0,y=0,size=64,roundness=.24,color='#22252a',label='A'}){
  finite(roundness,'icon roundness',0,.5);
  return group(id,x,y,[rect(id+'-shape',0,0,size,size,color,size*roundness),text(id+'-mark',label,size/2,size*.23,size*.42,{fill:'#ffffff',textAnchor:'middle',fontWeight:600})]);
}
export function AppCard({id,x=0,y=0,width=340,height=226,title='Your booking',detail='Friday · 7:00 PM',action='Confirm',color='#e9f1e7'}){
  finite(width,'card width',180);finite(height,'card height',160);
  return group(id,x,y,[rect(id+'-surface',0,0,width,height,'#ffffff',22,{stroke:TOKENS.line,strokeWidth:1}),rect(id+'-art',12,12,width-24,height*.36,color,14),
    text(id+'-title',title,20,height*.46,23,{fontWeight:600}),text(id+'-detail',detail,20,height*.46+33,16,{fill:TOKENS.muted}),
    ActionButton({id:id+'-action',x:20,y:height-58,width:width-40,copy:action})]);
}
export function Avatar({id,x=0,y=0,size=42,initials='JD',fill='#d8e2f0'}){
  return group(id,x,y,[{id:id+'-disc',type:'circle',width:size,height:size,fill},text(id+'-initials',initials,size/2,size*.27,size*.32,{textAnchor:'middle',fontWeight:600})]);
}
export function BottomSheet({id,x=0,y=0,width=430,height=310,title='Apps',children=[]}){
  return group(id,x,y,[rect(id+'-surface',0,0,width,height,'#f5f5f7',25),rect(id+'-handle',width/2-19,10,38,4,'#c4c7cc',2),text(id+'-heading',title,22,33,24,{fontWeight:600}),...children],{clip:{x:0,y:0,width,height,radius:25}});
}
export function PhoneFrame({id,x=0,y=0,width=440,height=500,title='A conversation',children=[]}){
  return group(id,x,y,[rect(id+'-matte',0,0,width,height,'#ffffff',28,{stroke:TOKENS.line,strokeWidth:1}),
    group(id+'-screen',0,0,[...children],{clip:{x:0,y:0,width,height,radius:28}}),
    rect(id+'-bar',1,1,width-2,66,'#f8f8fa',27),rect(id+'-bar-square',1,33,width-2,33,'#f8f8fa'),
    text(id+'-back','‹',18,17,30,{fill:TOKENS.blue}),text(id+'-title',title,width/2,25,17,{textAnchor:'middle',fontWeight:600}),rect(id+'-divider',1,66,width-2,1,TOKENS.line)]);
}
export function CameraRig({id='camera',children=[],keyframes={},x=0,y=0,originX=480,originY=270}){
  return group(id,x,y,children,{originX,originY,keyframes});
}
export const COMPONENTS=Object.freeze([
  {name:'MessageBubble',purpose:'Incoming/outgoing message, editable copy and tail',parameters:['copy','side','width','height','fill','tail']},
  {name:'Composer',purpose:'Typed input and send control as separate layers',parameters:['copy','width','active']},
  {name:'AppIcon',purpose:'An icon whose surface can change corner radius',parameters:['size','roundness','color','label']},
  {name:'AppCard',purpose:'Artwork, heading, detail and action in one reusable card',parameters:['width','height','title','detail','action','color']},
  {name:'BottomSheet',purpose:'Clipped panel with handle and nested app controls',parameters:['width','height','title','children']},
  {name:'PhoneFrame',purpose:'Conversation viewport; screen children are clipped independently',parameters:['width','height','title','children']},
  {name:'ActionButton',purpose:'Action surface and label with stable identity',parameters:['width','height','copy','fill']},
  {name:'Avatar',purpose:'Generic initials, not a copied source portrait',parameters:['size','initials','fill']},
  {name:'CameraRig',purpose:'Parent transform, separate from local UI layout',parameters:['children','keyframes','originX','originY']}
]);
