#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {buildMotion,MOTIFS} from './motions.mjs';
import {COMPONENTS} from './components.mjs';
import {directorPlan} from './decisions.mjs';
import {svgMarkup,stateAt} from '../scripts/engines/common.mjs';
import {entries,getMotion,searchMotions} from './motion-catalog/registry.mjs';
import {motionScene} from './motion-catalog/blocks.mjs';

const catalogDirectory=fileURLToPath(new URL('./motion-catalog/',import.meta.url));
const args=process.argv.slice(2),command=args.shift();
const option=(name,fallback)=>{const i=args.indexOf('--'+name);return i<0?fallback:args[i+1];};
const save=(filename,value)=>{fs.mkdirSync(path.dirname(filename),{recursive:true});fs.writeFileSync(filename,typeof value==='string'?value:JSON.stringify(value,null,2)+'\n');};
if(command==='list'){
  const studies=JSON.parse(fs.readFileSync(new URL('./catalogue.json',import.meta.url))).studies;
  console.log(JSON.stringify({motifs:MOTIFS,components:COMPONENTS,sourceStudies:studies.length,
    savedMotions:entries.map(({id,status})=>({id,status}))},null,2));
}else if(command==='search'){
  const query=args.filter(arg=>arg!=='--').join(' ');
  const results=searchMotions(query).map(({entry,matches})=>({
    id:entry.id,title:entry.title,status:entry.status,description:entry.description,matches,
    sourcePreview:entry.previews?.source?path.join(catalogDirectory,entry.previews.source):undefined,
    isolatedPreview:entry.previews?.isolated?path.join(catalogDirectory,entry.previews.isolated):undefined,
    next:entry.implementation?.sceneCommand??entry.limits[0]
  }));
  console.log(JSON.stringify({query,results},null,2));
}else if(command==='show'){
  const entry=getMotion(args[0]);
  if(!entry)throw Error('Unknown catalog motion: '+args[0]);
  console.log(JSON.stringify({catalogDirectory,...entry},null,2));
}else if(command==='plan'){
  const result=directorPlan(option('brief',''));const out=option('out');if(out)save(out,result);else console.log(JSON.stringify(result,null,2));
}else if(command==='scene' && option('motion')){
  const out=option('out');
  if(!out)throw Error('An explicit --out path is required');
  const configPath=path.resolve(option('config','motion-config.json'));
  const config=option('config')?JSON.parse(fs.readFileSync(configPath,'utf8')):{};
  const override={};
  for(const key of ['context','variant','title','copy','color','action']){
    if(option(key)!==undefined)override[key]=option(key);
  }
  if(option('duration')!==undefined)override.duration=Number(option('duration'));
  const result=motionScene(option('motion'),{...config,...override});
  const asAssetPath=layer=>{
    if(layer.src && !/^(data:|https?:)/.test(layer.src)){
      const source=path.resolve(path.dirname(configPath),layer.src);
      if(!fs.existsSync(source))throw Error('Image file not found: '+source);
      layer.src=path.relative(path.dirname(path.resolve(out)),source);
    }
    layer.children?.forEach(asAssetPath);
  };
  result.scene.layers.forEach(asAssetPath);
  save(out,result.scene);
  save(out.replace(/\.json$/,'')+'.events.json',{events:result.events,provenance:result.provenance,description:result.description});
}else if(['scene','frames','trajectory'].includes(command)){
  const result=buildMotion(option('motif','conversation-handoff'),{duration:Number(option('duration',4)),copy:option('copy','Can you book a table?'),title:option('title','Friday dinner'),color:option('color','#1688fa'),count:Number(option('count',9))});
  const out=option('out');if(!out)throw Error('An explicit --out path is required');
  if(command==='scene'){
    save(out,result.scene);save(out.replace(/\.json$/,'')+'.events.json',{events:result.events,provenance:result.provenance,description:result.description});
  }else if(command==='frames'){
    fs.mkdirSync(out,{recursive:true});for(const f of [0,24,48,72,96,119].map(f=>Math.min(Math.round(f/120*result.scene.duration*result.scene.fps),Math.round(result.scene.duration*result.scene.fps)-1))){save(path.join(out,String(f).padStart(6,'0')+'.svg'),svgMarkup(result.scene,f/result.scene.fps));}
  }else{
    const frames=[];const walk=(layers,t)=>layers.flatMap(l=>{const s=stateAt(l,t);return [{id:l.id,type:l.type,x:s.x,y:s.y,scaleX:s.scaleX,scaleY:s.scaleY,rotation:s.rotation,opacity:s.opacity,text:s.text,active:t>=(s.start??0)&&t<(s.end??result.scene.duration)},...walk(l.children??[],t)];});
    for(let frame=0;frame<Math.round(result.scene.fps*result.scene.duration);frame++)frames.push({frame,time:frame/result.scene.fps,layers:walk(result.scene.layers,frame/result.scene.fps)});
    save(out,{provenance:result.provenance,notice:'Evaluated starter trajectories, not measured source pixels. Local transforms; parent matrices must be composed for world coordinates.',frames});
  }
}else{
  console.log('list | search TEXT | show ID | scene --motion ID [--config options.json] [--context isolated|restaurant|conversation] [--variant measured|controls] --out scene.json | plan --brief TEXT | scene --motif ID --out scene.json | frames --motif ID --out DIR | trajectory --motif ID --out frames.json');
  if(command)process.exitCode=1;
}
