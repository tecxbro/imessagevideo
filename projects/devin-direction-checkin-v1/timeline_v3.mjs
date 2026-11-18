import {sampleTrack, stateAt} from '../../skill/imessage-motion-recreation/scripts/engines/common.mjs';

export const flatten=layers=>layers.flatMap(layer=>[layer,...flatten(layer.children??[])]);

export function frameMapping({start,end,frames}){
  if(!Number.isInteger(start)||end<=start||frames<2)throw Error('Invalid retime range');
  const outputEnd=start+frames-1,removed=end-outputEnd;
  const forward=f=>f<=start?f:f>=end?f-removed:start+(f-start)*(frames-1)/(end-start);
  const inverse=f=>f<=start?f:f>=outputEnd?f+removed:start+(f-start)*(end-start)/(frames-1);
  return {forward,inverse,removed,outputEnd};
}

export function retimeScene(authored,range){
  const {forward,inverse,removed,outputEnd}=frameMapping(range);
  const scene=structuredClone(authored),fps=scene.fps;
  const sourceFrames=Math.round(scene.duration*fps),frames=sourceFrames-removed;
  scene.duration=frames/fps;
  for(const layer of flatten(scene.layers)){
    delete layer.events;
    for(const field of ['start','end'])if(layer[field]!==undefined)layer[field]=forward(layer[field]*fps)/fps;
    for(const [property,track] of Object.entries(layer.keyframes??{})){
      const keys=[];
      for(let frame=0;frame<frames;frame++){
        const value=sampleTrack(track,inverse(frame)/fps);
        if(!keys.length||keys.at(-1).value!==value)keys.push({t:frame/fps,value,ease:'hold'});
      }
      layer.keyframes[property]=keys;
    }
  }
  const frameMap={fps,source:'scene.v2.json',output:'scene.json',sourceFrames,frames,
    range:{v2:[range.start,range.end],v3:[range.start,outputEnd]},removedFrames:removed,
    policy:'Endpoint-inclusive linear scene retime. Outside the range, native timing is unchanged except the -120 frame shift. The opening camera is separately reframed for the visible plus tap. v3Frame is the first output frame at or after the mapped source instant; compressed source frames can share it.',
    v2ToV3:Array.from({length:sourceFrames},(_,v2Frame)=>({v2Frame,v3Frame:Math.ceil(forward(v2Frame)-1e-9),v3FrameExact:forward(v2Frame)})),
    v3ToV2:Array.from({length:frames},(_,v3Frame)=>({v3Frame,v2Frame:inverse(v3Frame)}))};
  return {scene,frameMap};
}

export function visibleEvents(scene){
  const layers=new Map(flatten(scene.layers).map(layer=>[layer.id,layer]));
  const frames=Math.round(scene.duration*scene.fps),events=[];
  const at=(id,f)=>stateAt(layers.get(id),f/scene.fps);
  const active=(id,f)=>{const s=at(id,f);return f/scene.fps>=(s.start??0)&&f/scene.fps<(s.end??scene.duration)&&s.opacity>0;};
  const add=(frame,action,target,extra={})=>events.push({frame,action,target,actor:target,...extra});
  const first=(id,predicate)=>{
    for(let f=0;f<frames;f++)if(active(id,f)&&predicate(at(id,f),f))return f;
    throw Error('No visible onset: '+id);
  };
  add(first('bubbleAsk',s=>s.opacity>0),'receive','bubbleAsk');
  for(const id of ['tapPlus','tapCheckIn']){
    const frame=first(id,()=>true),camera=at('camera',frame),phone=at('phoneMaya',frame),tap=at(id,frame);
    const x=camera.x+camera.scaleX*(phone.x+tap.x),y=camera.y+camera.scaleY*(phone.y+tap.y);
    if(x<30||x>scene.width-30||y<30||y>scene.height-30)throw Error('Off-screen tap: '+id);
    add(frame,'tap',id);
  }
  add(first('tapSend',()=>true),'send','cardMaya');
  for(let frame=1;frame<frames;frame++){
    const before=at('draftSam',frame-1).text,after=at('draftSam',frame).text;
    if(before.trimEnd()===after.trimEnd())continue;
    const typing=after.length>before.length;
    add(frame,typing?'type char':'backspace','draftSam',{char:typing?after.at(-1):before.at(-1)});
  }
  for(let frame=1;frame<frames;frame++)if(at('cardSam-mode',frame-1).text!==at('cardSam-mode',frame).text){
    add(frame,'arrival','cardSam',{targets:['cardMaya','cardSam']});
  }
  add(first('bubbleHeartSam',()=>true),'send','bubbleHeartSam');
  add(first('bubbleHeart',()=>true),'receive','bubbleHeart');
  return events.sort((a,b)=>a.frame-b.frame);
}
