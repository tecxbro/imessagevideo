/* Combined into index.html by build_explorer.py; no runtime service required. */
const $=id=>document.getElementById(id);
const node=(tag,cls,content)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(content!==undefined)n.textContent=content;return n;};
const state={id:'identity-morph',frame:0,playing:false,then:0,config:{duration:4,copy:'Can you book a table?',title:'Friday dinner',color:'#1688fa',count:9},result:null};
let animation=0;
const download=(name,value,type='application/json')=>{const url=URL.createObjectURL(new Blob([typeof value==='string'?value:JSON.stringify(value,null,2)],{type}));const a=node('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);};
function paint(){
  const s=state.result.scene,frames=Math.round(s.duration*s.fps);state.frame=Math.min(frames-1,Math.max(0,state.frame));
  $('stage').innerHTML=svgMarkup(s,state.frame/s.fps);
  $('scrub').max=frames-1;$('scrub').value=state.frame;$('frame-label').textContent=`frame ${state.frame} / ${frames-1} · ${(state.frame/s.fps).toFixed(3)}s`;
  $('play').textContent=state.playing?'Pause':'Play';$('play').setAttribute('aria-pressed',String(state.playing));
}
function renderEvidence(){
  const matches=CATALOGUE.studies.filter(x=>x.starters.includes(state.id));const box=$('evidence');box.replaceChildren();
  if(!matches.length){box.append(node('p','muted','This is a new design extension. No exact corresponding source motion is claimed.'));return;}
  for(const r of matches){
    const article=node('article','study'),head=node('div','study-heading');head.append(node('h3','',r.title),node('span','tag',r.film));article.append(head,node('p','',r.intent),node('p','muted',r.caveat));
    if(r.atlas){const image=node('img','atlas');image.src=r.atlas;image.alt=r.alt;image.loading='lazy';const a=node('a');a.href=r.atlas;a.target='_blank';a.rel='noopener';a.append(image);article.append(a);}
    const details=node('details');details.append(node('summary','','Frame ranges, design notes and measured properties'));
    details.append(node('p','',r.anatomy),node('p','',`Use: ${r.choose}`),node('p','',`Avoid: ${r.avoid}`),node('pre','',JSON.stringify({frames:r.frames,scene:r.scene,bindings:r.bindings,evidence:r.evidence},null,2)));article.append(details);box.append(article);
  }
}
function select(id){
  state.id=id;state.frame=0;state.playing=false;cancelAnimationFrame(animation);
  state.result=buildMotion(id,state.config);const choice=CHOICES.find(c=>c.id===id);
  for(const b of $('motifs').children)b.setAttribute('aria-pressed',String(b.dataset.id===id));
  $('motif-title').textContent=choice.goal;$('intent').textContent=state.result.description;
  $('choice-reason').textContent=choice.choose;$('choice-risk').textContent=choice.risk;
  $('choice-components').textContent=choice.components.join(' + ');$('source-code').textContent=JSON.stringify(state.result.scene,null,2);
  $('event-code').textContent=JSON.stringify({events:state.result.events,provenance:state.result.provenance},null,2);
  renderEvidence();paint();
}
function tick(now){
  if(!state.playing)return;
  state.frame=((now-state.then)/1000*state.result.scene.fps)|0;
  if(state.frame>=Math.round(state.result.scene.duration*state.result.scene.fps)){state.playing=false;state.frame=Math.round(state.result.scene.duration*state.result.scene.fps)-1;}
  paint();if(state.playing)animation=requestAnimationFrame(tick);
}
for(const c of CHOICES){const b=node('button','motif',c.goal);b.type='button';b.dataset.id=c.id;b.setAttribute('aria-pressed','false');b.addEventListener('click',()=>select(c.id));$('motifs').append(b);}
$('play').addEventListener('click',()=>{state.playing=!state.playing;if(state.playing){if(state.frame===Math.round(state.result.scene.duration*state.result.scene.fps)-1)state.frame=0;state.then=performance.now()-state.frame/state.result.scene.fps*1000;animation=requestAnimationFrame(tick);}else cancelAnimationFrame(animation);paint();});
$('scrub').addEventListener('input',()=>{state.playing=false;cancelAnimationFrame(animation);state.frame=Number($('scrub').value);paint();});
for(const [id,key] of [['duration','duration'],['copy','copy'],['title','title'],['color','color']])$(id).addEventListener('input',()=>{if(!$(id).checkValidity()||(id==='duration'&&!$(id).value))return;state.config[key]=id==='duration'?Number($(id).value):$(id).value;select(state.id);});
$('export-scene').addEventListener('click',()=>download(state.id+'.scene.json',state.result.scene));
$('export-events').addEventListener('click',()=>download(state.id+'.events.json',{events:state.result.events,provenance:state.result.provenance}));
$('export-svg').addEventListener('click',()=>download(state.id+'-'+state.frame+'.svg',svgMarkup(state.result.scene,state.frame/state.result.scene.fps),'image/svg+xml'));
$('brief-form').addEventListener('submit',e=>{e.preventDefault();const plan=directorPlan($('brief').value),box=$('recommendations');box.replaceChildren();
  if(!plan.suggestions.length)box.append(node('p','muted',plan.unresolved[0]));
  for(const r of plan.suggestions){const b=node('button','suggestion');b.type='button';b.append(node('strong','',CHOICES.find(c=>c.id===r.motif).goal),node('span','',r.why),node('small','',`Matched: ${r.matchedWords.join(', ')}`));b.addEventListener('click',()=>select(r.motif));box.append(b);}
  $('plan-code').textContent=JSON.stringify(plan,null,2);$('plan-export').hidden=false;
});
$('plan-export').addEventListener('click',()=>download('director-plan.json',directorPlan($('brief').value)));
const componentDemos={
 MessageBubble:()=>MessageBubble({id:'demo-bubble',x:25,y:30,width:255,height:76,copy:'A table for two?'}),
 Composer:()=>Composer({id:'demo-composer',x:18,y:46,width:274,copy:'Friday, please.'}),
 AppIcon:()=>AppIcon({id:'demo-icon',x:115,y:25,size:84,label:'A'}),
 AppCard:()=>AppCard({id:'demo-card',x:55,y:10,width:240,height:210,title:'Friday dinner',detail:'7:00 PM · For two',action:'Reserve'}),
 BottomSheet:()=>BottomSheet({id:'demo-sheet',x:20,y:10,width:285,height:200,children:[AppIcon({id:'sheet-a',x:20,y:85,size:60,label:'A'}),AppIcon({id:'sheet-b',x:112,y:85,size:60,label:'B',color:'#6e9c74'})]}),
 PhoneFrame:()=>PhoneFrame({id:'demo-phone',x:55,y:8,width:230,height:225,title:'Assistant',children:[MessageBubble({id:'demo-phone-bubble',x:15,y:90,width:184,height:66,copy:'Ready to go.',side:'incoming',fontSize:17})]}),
 ActionButton:()=>ActionButton({id:'demo-button',x:65,y:48,width:190,copy:'Confirm'}),
 Avatar:()=>Avatar({id:'demo-avatar',x:125,y:32,size:70,initials:'JD'}),
 CameraRig:()=>CameraRig({id:'demo-camera',originX:160,originY:80,children:[rect('camera-context',20,20,270,105,'#e6e9ec',15),MessageBubble({id:'camera-bubble',x:42,y:40,width:222,height:65,copy:'Focus on the result.',fontSize:17})]})
};
for(const c of COMPONENTS){const article=node('article','component');article.append(node('h3','',c.name),node('p','muted',c.purpose));const picture=node('div','component-picture');picture.innerHTML=svgMarkup({width:330,height:240,fps:30,duration:1,background:'#fafafa',layers:[componentDemos[c.name]()]},0);article.append(picture,node('code','',c.parameters.join(' · ')));$('components').append(article);}
document.addEventListener('visibilitychange',()=>{if(document.hidden){state.playing=false;cancelAnimationFrame(animation);paint();}});
select(state.id);
