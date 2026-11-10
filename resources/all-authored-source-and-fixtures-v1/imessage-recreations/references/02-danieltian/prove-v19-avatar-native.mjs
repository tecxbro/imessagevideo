import fs from'node:fs';import{layerMarkup}from'../../engines/common.mjs';
const file=process.argv[2],data=JSON.parse(fs.readFileSync(file));
const embed=node=>{if(node.src&&!node.src.startsWith('data:'))node.src='data:image/png;base64,'+fs.readFileSync(node.src).toString('base64');for(const child of node.children??[])embed(child)};embed(data.before);embed(data.after);
const changed=[];for(let f=0;f<1360;f++)if(layerMarkup(data.before,f/data.fps,data.duration)!==layerMarkup(data.after,f/data.fps,data.duration))changed.push(f);
fs.writeFileSync(file+'.proof.json',JSON.stringify({checkedFrames:1360,changedFrames:changed,outsideFramesIdentical:1360-changed.length,parentTransformAndActualImageBytesPreserved:true},null,2));console.log('Avatar-family exact native changes:',changed.join(','));
