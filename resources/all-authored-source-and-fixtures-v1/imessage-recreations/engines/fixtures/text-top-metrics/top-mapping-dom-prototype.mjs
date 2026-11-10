// Private robust variant: read the browser's actual quantized inline leading.
import {TxtLeaf} from '../../node_modules/@motion-canvas/2d/lib/components/TxtLeaf.js';
const original=TxtLeaf.prototype.drawText;
export function measuredInlineLeadingCorrection(leaf){
 const range=document.createRange();range.selectNodeContents(leaf.element);
 return -(range.getBoundingClientRect().top-leaf.parent().element.getBoundingClientRect().top);
}
TxtLeaf.prototype.drawText=function(context,text,box){
 if(window.metricFixtureMode!=='native-dom-prototype')return original.call(this,context,text,box);
 const delta=measuredInlineLeadingCorrection(this);
 if(!delta)return original.call(this,context,text,box);
 return original.call(this,context,text,{x:box.x,y:box.y+delta});
};
