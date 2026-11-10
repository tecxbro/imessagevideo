// Private candidate only: preserve native layout/effects; normalize glyph paint.
import * as Runtime from './motion-canvas-runtime.fixture-383.mjs';
import {TxtLeaf} from '../../node_modules/@motion-canvas/2d/lib/components/TxtLeaf.js';
window.GeometryRuntime=Runtime;window.geometryLogs=[];
let active=null;
const original=TxtLeaf.prototype.drawText,fill=CanvasRenderingContext2D.prototype.fillText,stroke=CanvasRenderingContext2D.prototype.strokeText;
TxtLeaf.prototype.drawText=function(context,text,box){const old=active;active=this;try{return original.call(this,context,text,box);}finally{active=old;}};
function paint(context,text,x,y,rest,method){
 if(!active||!text.trim())return method.call(context,text,x,y,...rest);
 const leaf=active,world=leaf.localToWorld(),rms=Math.hypot(world.a,world.b,world.c,world.d)/Math.SQRT2;
 if(!Number.isFinite(rms)||rms<=0||Math.abs(rms-1)<1e-9){window.geometryLogs.push({text,rms,unchanged:true});return method.call(context,text,x,y,...rest);}
 const originalFont=context.font,oldBaseline=context.textBaseline,oldMetrics=context.measureText(''),oldWidth=context.measureText(text).width;
 const font=context.font.replace(/([\d.]+)px/,(_,size)=>`${Number(size)*rms}px`);
 context.save();context.font=font;context.textBaseline='alphabetic';
 if('letterSpacing'in context)context.letterSpacing=`${leaf.letterSpacing()*rms}px`;
 const scaledMetrics=context.measureText(''),scaledWidth=context.measureText(text).width;
 const anchor=(leaf.parent().offset().x+1)/2,xCorrection=(oldWidth-scaledWidth/rms)*anchor;
 const newX=(x+xCorrection)*rms,newY=(y-oldMetrics.fontBoundingBoxAscent)*rms+scaledMetrics.fontBoundingBoxAscent;
 const paintBefore=context.getTransform();context.scale(1/rms,1/rms);context.lineWidth*=rms;
 window.geometryLogs.push({text,rms,oldFont:originalFont,newFont:font,oldBaseline,worldYScale:Math.hypot(world.c,world.d),paintYScale:Math.hypot(paintBefore.c,paintBefore.d),worldLinear:[world.a,world.b,world.c,world.d],anchor,xCorrection,oldFontBoxHeight:oldMetrics.fontBoundingBoxAscent+oldMetrics.fontBoundingBoxDescent,normalizedFontBoxHeight:(scaledMetrics.fontBoundingBoxAscent+scaledMetrics.fontBoundingBoxDescent)/rms,scaledAscent:scaledMetrics.fontBoundingBoxAscent,oldDraw:{x,y},newDraw:{x:newX,y:newY},fontTopPreservationError:(newY-scaledMetrics.fontBoundingBoxAscent)/rms-(y-oldMetrics.fontBoundingBoxAscent)});
 try{return method.call(context,text,newX,newY,...rest);}finally{context.restore();}
}
CanvasRenderingContext2D.prototype.fillText=function(text,x,y,...rest){return paint(this,text,x,y,rest,fill);};
CanvasRenderingContext2D.prototype.strokeText=function(text,x,y,...rest){return paint(this,text,x,y,rest,stroke);};
