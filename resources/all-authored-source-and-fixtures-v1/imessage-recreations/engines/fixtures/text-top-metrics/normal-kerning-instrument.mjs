import * as Runtime from './motion-canvas-runtime.fixture-7080.mjs';
import {TxtLeaf} from '../../node_modules/@motion-canvas/2d/lib/components/TxtLeaf.js';
window.GeometryRuntime=Runtime;window.geometryLogs=[];
const original=TxtLeaf.prototype.drawText;
TxtLeaf.prototype.drawText=function(context,text,box){
 if(!text.trim())return original.call(this,context,text,box);
 const normalized=text.replace(/\s+/g,' '),before=context.fontKerning;
 context.save();
 try{
  context.fontKerning='auto';const auto=context.measureText(normalized).width;
  context.fontKerning='normal';const normal=context.measureText(normalized).width;
  const multi=this.text().includes('\n');
  window.geometryLogs.push({text:normalized,font:context.font,originalPolicy:before,candidatePolicy:'normal',textRendering:context.textRendering,anchor:this.parent().offset().x,domLineBoxWidth:box.width,autoWidth:auto,normalWidth:normal,multiline:multi,normalMinusDOM:normal-box.width,autoMinusDOM:auto-box.width});
  return original.call(this,context,text,box);
 }finally{context.restore();}
};
