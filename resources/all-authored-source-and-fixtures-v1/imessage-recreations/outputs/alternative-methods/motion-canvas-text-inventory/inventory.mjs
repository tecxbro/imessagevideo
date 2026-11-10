/** Read-only inventory of exact active authored Txt states; no renderer setup/capture. */
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {stateAt} from '../../../engines/common.mjs';
const out=path.resolve('outputs/alternative-methods/motion-canvas-text-inventory');
const stateFile=path.resolve('delivery-state.json'),stateBytes=fs.readFileSync(stateFile),delivery=JSON.parse(stateBytes);
fs.writeFileSync(path.join(out,'delivery-state.snapshot.json'),stateBytes);
const sha=b=>createHash('sha256').update(b).digest('hex');
const ranges=values=>{const result=[];for(const f of [...new Set(values)].sort((a,b)=>a-b)){if(result.length&&result.at(-1)[1]===f-1)result.at(-1)[1]=f;else result.push([f,f]);}return result;};
const matrix=s=>{const r=s.rotation*Math.PI/180,c=Math.cos(r),sn=Math.sin(r);return [c*s.scaleX,sn*s.scaleX,-sn*s.scaleY,c*s.scaleY];};
const mul=(a,b)=>[a[0]*b[0]+a[2]*b[1],a[1]*b[0]+a[3]*b[1],a[0]*b[2]+a[2]*b[3],a[1]*b[2]+a[3]*b[3]];
const emoji=/\p{Extended_Pictographic}|\uFE0F/u;
function textTree(layers){return layers.flatMap(n=>{if(n.type==='text')return [{...n}];const children=textTree(n.children??[]);return children.length?[{...n,children}]:[];});}
function lhMode(v){return v===undefined||v===null?'default':typeof v==='number'?'numeric':typeof v==='string'&&v.trim().endsWith('%')?'percentage':'other';}
const results=[];
for(const [reference,row]of Object.entries(delivery.scenes)){
 const input=path.resolve(row.scene);let bytes=fs.readFileSync(input),full=JSON.parse(bytes.toString('utf8'));
 const sceneSha256=sha(bytes),fps=full.fps,count=Math.round(fps*full.duration),layers=textTree(full.layers);
 const fonts=(full.fonts??[]).map(f=>{const raw=f.src.startsWith('data:')?Buffer.from(f.src.split(',')[1],'base64'):fs.readFileSync(path.resolve(path.dirname(input),f.src));return {family:f.family,weight:f.weight??400,style:f.style??'normal',source:f.src.startsWith('data:')?'embedded:data':path.resolve(path.dirname(input),f.src),sha256:sha(raw),bytes:raw.length};});
 const sourceMapping=full.source?.segments??full.source?.timeMap??full.source?.sourceFrameMap??null;
 full=null;bytes=null;global.gc?.();
 const nodes=new Map(),styles=[],styleIds=new Map(),transforms=[],transformIds=new Map(),texts=[],textIds=new Map();
 const declared=[];
 function declare(ls,parents=[]){for(const n of ls){if(n.type==='text'){const item={id:n.id,ancestors:parents,declared:{fontFamily:n.fontFamily??null,fontWeight:n.fontWeight??null,fontSize:n.fontSize??null,lineHeight:n.lineHeight??null,textDecoration:n.textDecoration??null,textAnchor:n.textAnchor??null},trackedProperties:Object.keys(n.keyframes??{}),runs:[],activeFrames:[],inkFrames:[],styleIds:new Set(),fontSizes:new Set(),flags:{multiline:false,emoji:false,underline:false,animatedFontSize:!!n.keyframes?.fontSize,animatedLineHeight:!!n.keyframes?.lineHeight,animatedFontFamily:!!n.keyframes?.fontFamily,animatedDecoration:!!n.keyframes?.textDecoration}};nodes.set(n.id,item);declared.push(item);}else declare(n.children??[],[...parents,{id:n.id,hasClip:!!n.clip}]);}}
 declare(layers);
 for(let f=0;f<count;f++){
  const t=f/fps;
  function walk(ls,world=[1,0,0,1],ancestors=[],opacity=1){for(const n of ls){const s=stateAt(n,t);if(t<(s.start??0)||t>=(s.end??count/fps)||s.opacity<=0)continue;const local=matrix(s),wm=mul(world,local),effectiveOpacity=opacity*s.opacity;
   if(n.type==='text'){
    const node=nodes.get(n.id),size=s.fontSize??32,rawLH=s.lineHeight??null,mode=lhMode(rawLH),effectiveLH=mode==='default'?size*1.2:mode==='numeric'?rawLH:mode==='percentage'?size*parseFloat(rawLH)/100:null;
    const style={fontFamily:s.fontFamily??'Arial, sans-serif',fontWeight:s.fontWeight??400,fontSize:size,lineHeightMode:mode,lineHeight:rawLH,effectiveLineHeightPx:effectiveLH,textAnchor:s.textAnchor??'start',textDecoration:s.textDecoration??'none'};
    const sk=JSON.stringify(style);let si=styleIds.get(sk);if(si===undefined){si=styles.length;styleIds.set(sk,si);styles.push({...style,id:si,nodeIds:new Set(),frames:[],flags:{multiline:false,emoji:false,underline:false},examples:[]});}
    const text=String(s.text??''),textKey=text;let xi=textIds.get(textKey);if(xi===undefined){xi=texts.length;textIds.set(textKey,xi);texts.push({id:xi,text,lines:text.split('\n').length,hasEmoji:emoji.test(text),hasInk:!!text.trim()});}
    const txt=texts[xi],deco=style.textDecoration==='underline',styleRow=styles[si];node.flags.multiline||=txt.lines>1;node.flags.emoji||=txt.hasEmoji;node.flags.underline||=deco;node.activeFrames.push(f);if(txt.hasInk)node.inkFrames.push(f);node.styleIds.add(si);node.fontSizes.add(size);styleRow.nodeIds.add(n.id);styleRow.frames.push(f);styleRow.flags.multiline||=txt.lines>1;styleRow.flags.emoji||=txt.hasEmoji;styleRow.flags.underline||=deco;if(styleRow.examples.length<3&&!styleRow.examples.includes(text))styleRow.examples.push(text);
    const ts={worldLinear:wm,nodeScale:[s.scaleX,s.scaleY,s.rotation],ancestorScales:ancestors.map(a=>[a.scaleX,a.scaleY,a.rotation]),worldXGain:Math.hypot(wm[0],wm[1]),worldYGain:Math.hypot(wm[2],wm[3]),worldYCorrectionVector:[wm[2],wm[3]],nonConformal:Math.abs(Math.hypot(wm[0],wm[1])-Math.hypot(wm[2],wm[3]))>1e-6||Math.abs(wm[0]*wm[2]+wm[1]*wm[3])>1e-6};
    const tk=JSON.stringify(ts);let ti=transformIds.get(tk);if(ti===undefined){ti=transforms.length;transformIds.set(tk,ti);transforms.push({...ts,id:ti});}
    const signature=JSON.stringify([si,ti,xi,effectiveOpacity]);const last=node.runs.at(-1);if(last&&last._signature===signature&&last.end===f-1)last.end=f;else node.runs.push({start:f,end:f,styleId:si,transformId:ti,textId:xi,effectiveOpacity,_signature:signature});
   }else walk(n.children??[],wm,[...ancestors,{scaleX:s.scaleX,scaleY:s.scaleY,rotation:s.rotation}],effectiveOpacity);
  }}
  walk(layers);
 }
 const allNodes=declared.map(n=>({...n,activeFrameRanges:ranges(n.activeFrames),inkFrameRanges:ranges(n.inkFrames),activeFrameCount:n.activeFrames.length,inkFrameCount:n.inkFrames.length,styleIds:[...n.styleIds],fontSizeRange:n.fontSizes.size?[Math.min(...n.fontSizes),Math.max(...n.fontSizes)]:null,defaultLineHeightWithAnimatedFontSize:n.flags.animatedFontSize&&[...n.styleIds].some(i=>styles[i].lineHeightMode==='default')&&n.fontSizes.size>1,runs:n.runs.map(({_signature,...r})=>r),activeFrames:undefined,inkFrames:undefined,fontSizes:undefined}));
 const styleRows=styles.map(s=>({...s,nodeIds:[...s.nodeIds],activeFrameRanges:ranges(s.frames),activeFrameCount:new Set(s.frames).size,frames:undefined}));
 const activeNodes=allNodes.filter(n=>n.activeFrameCount),activeStyles=styleRows.length;
 const result={reference,input,sceneSha256,fps,frames:count,sourceMapping,fonts,declaredTxtNodes:allNodes.length,activeTxtNodes:activeNodes.length,activeStyles,nodes:allNodes,styles:styleRows,transforms,texts,conventions:{frameTime:'candidate frame / fps',visibility:'Exact declared lifecycle and positive own/ancestor opacity. No guessed viewport/font clipping; active frame bounds are conservative for actual ink.',lineHeight:'Default is fontSize*1.2; numeric is authored pixels; percentage converted for inventory only, raw value retained.',worldLinear:'[a,b,c,d] maps local dx/dy to world[a*dx+c*dy,b*dx+d*dy]. worldYCorrectionVector maps a local text-y correction to worlddx/dy.',ancestorScales:'Triples [scaleX,scaleY,rotation] correspond in order to nodes[].ancestors; own node scale is separate.'}};
 fs.writeFileSync(path.join(out,reference+'.json'),JSON.stringify(result,null,2)+'\n');
 const summary={reference,input,sceneSha256,frames:count,declaredTxtNodes:allNodes.length,activeTxtNodes:activeNodes.length,activeStyles,lineHeightModes:Object.fromEntries(['default','numeric','percentage','other'].map(mode=>[mode,styleRows.filter(s=>s.lineHeightMode===mode).length])),multilineNodes:activeNodes.filter(n=>n.flags.multiline).map(n=>n.id),emojiNodes:activeNodes.filter(n=>n.flags.emoji).map(n=>n.id),underlineNodes:activeNodes.filter(n=>n.flags.underline).map(n=>n.id),defaultLHAnimatedSizeNodes:activeNodes.filter(n=>n.defaultLineHeightWithAnimatedFontSize).map(n=>n.id),activeFrameRanges:ranges(activeNodes.flatMap(n=>n.runs.flatMap(r=>[...Array(r.end-r.start+1)].map((_,i)=>r.start+i))))};
 results.push(summary);console.log(JSON.stringify(summary));global.gc?.();
}
fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify({deliveryStateSha256:sha(stateBytes),snapshot:'delivery-state.snapshot.json',status:'read-only authored Txt inventory; no native capture, runtime promotion, source change or final-cache mutation',scenes:results},null,2)+'\n');
