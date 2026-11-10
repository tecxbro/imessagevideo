// UNEXECUTED conversion prototype. Read audit.json and required Figma skills first.
// Submit only after a known file/session, read-only canvas inspection, and Motion capability probe.
const scene={"title":"CAPABILITY TEST — not a reference recreation","width":640,"height":360,"fps":30,"duration":1,"background":"#eff2f6","layers":[{"id":"notice","type":"text","text":"RENDER CAPABILITY TEST","x":32,"y":22,"fontFamily":"Arial, sans-serif","fontSize":20,"fontWeight":700,"fill":"#293444"},{"id":"bubble","type":"group","x":180,"y":120,"keyframes":{"x":[{"t":0,"value":120},{"t":0.6,"value":180,"ease":"easeOut"}],"opacity":[{"t":0,"value":0},{"t":0.3,"value":1}]},"children":[{"id":"bubble-shape","type":"rect","width":280,"height":100,"radius":34,"fill":"#1688ff"},{"id":"bubble-text","type":"text","text":"Measured motion","x":25,"y":30,"fontSize":26,"fontFamily":"Arial, sans-serif","fill":"#ffffff"}]},{"id":"dot","type":"circle","x":305,"y":260,"width":24,"height":24,"fill":"#222222","keyframes":{"scaleX":[{"t":0,"value":0.5},{"t":1,"value":1}],"scaleY":[{"t":0,"value":0.5},{"t":1,"value":1}]}}]};
const imageAssets={};
const blockers=[];
if(blockers.length)throw new Error('Preparation has blocking features: '+blockers.join('; '));
function cubic(a,b,c,t){let u=1-t;return 3*u*u*t*a+3*u*t*t*b+t*t*t*c;}
function easeValue(p,name='linear'){
  if(name==='hold')return p>=1?1:0;
  if(name==='easeIn')return p*p*p;
  if(name==='easeOut')return 1-(1-p)**3;
  if(name==='easeInOut')return p<.5?4*p*p*p:1-(-2*p+2)**3/2;
  const match=name.match(/^cubic-bezier\(([^)]+)\)$/);
  if(match){const [x1,y1,x2,y2]=match[1].split(',').map(Number);let lo=0,hi=1;for(let i=0;i<24;i++){let m=(lo+hi)/2;if(cubic(x1,x2,1,m)<p)lo=m;else hi=m;}return cubic(y1,y2,1,(lo+hi)/2);}
  return p;
}
function interpolate(a,b,p){
 if(typeof a==='number'&&typeof b==='number')return a+(b-a)*p;
 if(/^#[0-9a-f]{6}$/i.test(a)&&/^#[0-9a-f]{6}$/i.test(b)){const channels=[1,3,5].map(i=>Math.round(parseInt(a.slice(i,i+2),16)+(parseInt(b.slice(i,i+2),16)-parseInt(a.slice(i,i+2),16))*p));return '#'+channels.map(v=>v.toString(16).padStart(2,'0')).join('');}
 return p>=1?b:a;
}
function sampleTrack(track,t){const keys=[...track].sort((a,b)=>a.t-b.t);if(t<=keys[0].t)return keys[0].value;for(let i=1;i<keys.length;i++){const a=keys[i-1],b=keys[i];if(t<=b.t)return interpolate(a.value,b.value,easeValue((t-a.t)/(b.t-a.t),b.ease));}return keys.at(-1).value;}

const createdNodeIds=[], mutatedNodeIds=[], nativeFonts=await figma.listAvailableFontsAsync();
const available=nativeFonts.map(x=>x.fontName);
const record=n=>{createdNodeIds.push(n.id);return n;};
const color=s=>{if(!s||s==='none')return null;let v=s.slice(1);if(v.length===3)v=v.split('').map(c=>c+c).join('');return {r:parseInt(v.slice(0,2),16)/255,g:parseInt(v.slice(2,4),16)/255,b:parseInt(v.slice(4,6),16)/255,a:v.length===8?parseInt(v.slice(6,8),16)/255:1};};
const paint=s=>{const c=color(s);return c?[{type:'SOLID',color:{r:c.r,g:c.g,b:c.b},opacity:c.a}]:[];};
const easing=s=>{if(!s||s==='linear')return {type:'LINEAR'};if(s==='hold')return {type:'HOLD'};const named={easeIn:'EASE_IN',easeOut:'EASE_OUT',easeInOut:'EASE_IN_AND_OUT'};if(named[s])return {type:named[s]};const m=s.match(/^cubic-bezier\(([^)]+)\)$/);if(m){const [x1,y1,x2,y2]=m[1].split(',').map(Number);return {type:'CUSTOM_CUBIC_BEZIER',easingFunctionCubicBezier:{x1,y1,x2,y2}};}throw new Error('Unknown easing '+s);};
const kf=(k,value)=>({timelinePosition:k.t,value:{type:'FLOAT',value},easing:easing(k.ease)});
const opacityKeys=l=>{const a=l.start??0,b=l.end??scene.duration,track=l.keyframes?.opacity;const at=t=>track?sampleTrack(track,t):(l.opacity??1);const keys=[{t:0,value:a>0?0:at(0)}];if(a>0)keys.push({t:a,value:at(a),ease:'hold'});for(const k of (track??[]))if(k.t>a&&k.t<b)keys.push(k);if(b<scene.duration)keys.push({t:b,value:0,ease:'hold'});return keys;};
function fontFor(l){const family=String(l.fontFamily??'Arial').split(',')[0].trim().replace(/^['"]|['"]$/g,'');const fonts=available.filter(f=>f.family===family);if(!fonts.length)throw new Error('Font family unavailable: '+family);const w=Number(l.fontWeight??400),target=w>=800?['Extra Bold','ExtraBold','Black']:w>=700?['Bold']:w>=600?['Semi Bold','SemiBold','Semibold']:w>=500?['Medium']:w<=300?['Light']:['Regular','Normal','Book'];const found=fonts.find(f=>target.some(x=>x.toLowerCase()===f.style.toLowerCase()));if(!found)throw new Error('Exact font style unavailable for '+family+' weight '+w);return found;}
// Validate all declared font families/styles before creating any nodes.
const verifyFonts=async ls=>{for(const l of ls){if(l.type==='text')await figma.loadFontAsync(fontFor(l));await verifyFonts(l.children??[]);}};
await verifyFonts(scene.layers);
const existing=figma.currentPage.children;
const right=existing.reduce((m,n)=>Math.max(m,n.x+n.width),0);
const stage=record(figma.createFrame());stage.name=scene.title??'Measured recreation';stage.resize(scene.width,scene.height);stage.x=right+160;stage.y=80;stage.fills=paint(scene.background??'#ffffff');stage.clipsContent=true;
async function create(l,parent){
  const originX=l.originX??0,originY=l.originY??0;
  const wrapper=record(figma.createFrame());wrapper.name=l.id+' / motion';wrapper.resize(1,1);wrapper.fills=[];wrapper.clipsContent=false;parent.appendChild(wrapper);wrapper.x=(l.x??0)+originX-.5;wrapper.y=(l.y??0)+originY-.5;
  let n;
  if(l.type==='group'){
    n=record(figma.createFrame());n.name=l.id+' / content';n.resize(Math.max(1,l.width??1),Math.max(1,l.height??1));n.fills=[];n.clipsContent=false;
  }else if(l.type==='rect'){n=record(figma.createRectangle());n.resize(Math.max(.01,l.width??1),Math.max(.01,l.height??1));n.cornerRadius=l.radius??0;}
  else if(l.type==='circle'){n=record(figma.createEllipse());const w=l.width??(l.radius??1)*2;n.resize(w,l.height??w);}
  else if(l.type==='text'){
    n=record(figma.createText());n.fontName=fontFor(l);n.fontSize=l.fontSize??32;n.characters=String(l.text??'');n.textAutoResize='WIDTH_AND_HEIGHT';n.lineHeight={unit:'PIXELS',value:l.lineHeight??(l.fontSize??32)*1.2};n.letterSpacing={unit:'PIXELS',value:l.letterSpacing??0};if(l.textDecoration==='underline')n.textDecoration='UNDERLINE';
  }else if(l.type==='image'){
    n=record(figma.createRectangle());n.resize(l.width,l.height);n.fills=[{type:'IMAGE',imageHash:figma.createImage(new Uint8Array(imageAssets[l.id])).hash,scaleMode:'FILL'}];
  }else if(l.type==='path'){n=record(figma.createVector());n.vectorPaths=[{windingRule:'NONZERO',data:l.d}];}
  wrapper.appendChild(n);n.name=l.id;n.x=.5-originX;n.y=.5-originY;
  if(l.type==='text'&&l.textAnchor==='middle')n.x-=n.width/2;if(l.type==='text'&&l.textAnchor==='end')n.x-=n.width;
  if(l.type!=='image'&&l.type!=='group')n.fills=paint(l.fill??'#000000');
  if(l.stroke){n.strokes=paint(l.stroke);n.strokeWeight=l.strokeWidth??0;}
  for(const c of l.children??[])await create(c,n);
  const transformFields={x:'TRANSLATION_X',y:'TRANSLATION_Y',rotation:'ROTATION',scaleX:'SCALE_X',scaleY:'SCALE_Y'};
  const tracks={OPACITY:{keyframes:opacityKeys(l).map(k=>kf(k,k.value))}};
  for(const [p,field] of Object.entries(transformFields)){
    const keys=l.keyframes?.[p]??([{t:0,value:l[p]??(['scaleX','scaleY'].includes(p)?1:0)}]);
    tracks[field]={keyframes:keys.map(k=>kf(k,p==='x'?k.value-(l.x??0):p==='y'?k.value-(l.y??0):p==='rotation'?-k.value:k.value))};
  }
  wrapper.manualKeyframeTracks=tracks;
  const shapeTracks={};
  for(const [p,field]of Object.entries({width:'WIDTH',height:'HEIGHT',radius:'CORNER_RADIUS',strokeWidth:'STROKE_WEIGHT'}))if(l.keyframes?.[p])shapeTracks[field]={keyframes:l.keyframes[p].map(k=>kf(k,k.value))};
  for(const [p,indexed]of Object.entries({fill:'fills',stroke:'strokes'}))if(l.keyframes?.[p])shapeTracks[indexed]={0:{keyframes:l.keyframes[p].map(k=>({timelinePosition:k.t,value:{type:'COLOR',value:color(k.value)},easing:easing(k.ease)}))}};
  if(Object.keys(shapeTracks).length)n.manualKeyframeTracks=shapeTracks;
  return wrapper;
}
const roots=[];for(const l of scene.layers)roots.push(await create(l,stage));
if(roots.length){const [timeline]=roots[0].timelines;if(!timeline)throw new Error('No native Motion timeline was created');if(timeline.duration<scene.duration){roots[0].setTimelineDuration(timeline.id,scene.duration);mutatedNodeIds.push(timeline.id);}}
stage.placeholder=false;
return {createdNodeIds,mutatedNodeIds,stageId:stage.id,width:stage.width,height:stage.height,timeline:roots[0]?.timelines,warning:'Generated conversion was unverified before this write. Export and compare before claiming fidelity.'};
