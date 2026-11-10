import * as Runtime from './motion-canvas-runtime.fixture-383.mjs';
import {TxtLeaf} from '../../node_modules/@motion-canvas/2d/lib/components/TxtLeaf.js';
window.GeometryRuntime=Runtime;window.geometryLogs=[];
const original=TxtLeaf.prototype.drawText,fill=CanvasRenderingContext2D.prototype.fillText;
let active=null;
const point=(m,x,y)=>({x:m.a*x+m.c*y+m.e,y:m.b*x+m.d*y+m.f});
const inversePoint=(m,p)=>{const det=m.a*m.d-m.b*m.c,x=p.x-m.e,y=p.y-m.f;return{x:(m.d*x-m.c*y)/det,y:(-m.b*x+m.a*y)/det};};
TxtLeaf.prototype.drawText=function(context,text,box){const old=active;active=this;try{return original.call(this,context,text,box);}finally{active=old;}};
CanvasRenderingContext2D.prototype.fillText=function(text,x,y,...rest){
 if(active&&text.trim()){
  const leaf=active,parent=leaf.parent(),world=leaf.localToWorld(),parentWorld=parent.localToWorld(),paint=this.getTransform();
  const metrics=this.measureText(''),fontTopWorld=point(world,x,y-metrics.fontBoundingBoxAscent),fontTopParent=inversePoint(parentWorld,fontTopWorld);
  const normalized=s=>s.replace(/\s+/g,' ').trim();const lines=leaf.text().split('\n').map(normalized),lineIndex=Math.max(0,lines.indexOf(normalized(text))),lineHeight=parseFloat(leaf.styles.lineHeight);
  const topRelativeTxt=fontTopParent.y+parent.size().y/2,expected=lineIndex*lineHeight;
  window.geometryLogs.push({text,font:this.font,baseline:this.textBaseline,lineIndex,lineHeight,logicalFontBoxTopInTxt:topRelativeTxt,expectedSVGLineTop:expected,logicalError:topRelativeTxt-expected,worldYScale:Math.hypot(world.c,world.d),paintYScale:Math.hypot(paint.c,paint.d),worldRotation:Math.atan2(world.b,world.a)*180/Math.PI,draw:{x,y},fontBBoxAscent:metrics.fontBoundingBoxAscent,parentSize:{x:parent.size().x,y:parent.size().y}});
 }
 return fill.call(this,text,x,y,...rest);
};
