// Private release candidate, deliberately not imported by the production runtime.
// TxtLeaf.draw has already applied font/style and bottom-baseline metrics here.
// Adjusting its draw box keeps fill/stroke in sync and preserves native actors,
// transforms, line spacing, letter spacing and the separately authored underline.
import {TxtLeaf} from '../../node_modules/@motion-canvas/2d/lib/components/TxtLeaf.js';

export function measuredFontBoxCorrection(context, leaf) {
 const metrics=context.measureText('');
 const naturalHeight=metrics.fontBoundingBoxAscent+metrics.fontBoundingBoxDescent;
 const lineHeight=parseFloat(leaf.styles.lineHeight);
 if(!Number.isFinite(naturalHeight)||!Number.isFinite(lineHeight))return 0;
 return -Math.floor((lineHeight-naturalHeight)/2);
}

const original=TxtLeaf.prototype.drawText;
TxtLeaf.prototype.drawText=function(context,text,box){
 if(window.metricFixtureMode!=='native-prototype')return original.call(this,context,text,box);
 const delta=measuredFontBoxCorrection(context,this);
 return original.call(this,context,text,{x:box.x,y:box.y+delta});
};
