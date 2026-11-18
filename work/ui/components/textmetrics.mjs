/** Text measurement for the component kit v2.
 * Width tables measured with canvas.measureText at fontSize 100 on macOS Chrome.
 * The kit's font stack resolves to Helvetica Neue in Chromium (-apple-system is
 * unrecognized there — verified by rendered-width comparison), so the DEFAULT table
 * is Helvetica Neue; 'sf' (SF Pro) is available for the Pillow/native path.
 * Emoji/SMP glyphs are ~1em wide; VS16 is zero width. Unknown chars fall back to
 * class averages. This sizes boxes only — engines still shape the real glyphs.
 */
const W100_HN = {
  '0':55.6,'1':55.6,'2':55.6,'3':55.6,'4':55.6,'5':55.6,'6':55.6,'7':55.6,'8':55.6,'9':55.6,
  a:53.7,b:59.3,c:53.7,d:59.3,e:53.7,f:29.6,g:57.4,h:55.6,i:22.2,j:22.2,k:51.9,l:22.2,
  m:85.3,n:55.6,o:57.4,p:59.3,q:59.3,r:33.3,s:50,t:31.5,u:55.6,v:50,w:75.8,x:51.8,y:50,z:48,
  A:64.8,B:68.5,C:72.2,D:70.4,E:61.1,F:57.4,G:75.9,H:72.2,I:25.9,J:51.9,K:66.7,
  L:55.6,M:87.1,N:72.2,O:76,P:64.8,Q:76,R:68.5,S:64.8,T:61.1,U:72.2,V:66.7,
  W:92.6,X:61.1,Y:64.8,Z:61.1,
  ' ':27.8,'.':27.8,',':27.8,'?':55.6,'!':25.9,':':27.8,';':27.8,"'":27.8,'"':42.6,
  '(' :25.9,')':25.9,'-':33.3,'—':66.7,'–':50,'/':38.9,'\\':33.3,'+':60,'$':55.6,
  '&':63,'@':80,'#':55.6,'%':100,'*':35.2,'_':55.6,'=':60,'<':60,'>':60,
  '[':27.8,']':27.8,'{':33.3,'}':33.3,'|':22.2,'~':55.6,'^':50,'€':55.6,'£':55.6,'•':33.3,
  '’':27.8,'‘':27.8,'“':42.6,'”':42.6,'…':83.3,'·':27.8
};
const W100_SF = {
  '0':50,'1':50,'2':50,'3':50,'4':50,'5':50,'6':50,'7':50,'8':50,'9':50,
  a:44.38,b:50,c:44.38,d:50,e:44.38,f:33.3,g:50,h:50,i:27.78,j:27.78,k:50,l:27.78,
  m:77.78,n:50,o:50,p:50,q:50,r:33.3,s:38.92,t:27.78,u:50,v:50,w:72.22,x:50,y:50,z:44.38,
  A:72.22,B:66.7,C:66.7,D:72.22,E:61.08,F:55.62,G:72.22,H:72.22,I:33.3,J:38.92,K:72.22,
  L:61.08,M:88.92,N:72.22,O:72.22,P:55.62,Q:72.22,R:66.7,S:55.62,T:61.08,U:72.22,
  V:72.22,W:94.38,X:72.22,Y:72.22,Z:61.08,
  ' ':25,'.':25,',':25,'?':44.38,'!':33.3,':':27.78,';':27.78,"'":18.02,'"':40.82,
  '(' :33.3,')':33.3,'-':33.3,'—':66.7,'–':50,'/':27.78,'\\':27.78,'+':56.4,'$':50,
  '&':77.78,'@':92.09,'#':50,'%':83.3,'*':50,'_':50,'=':56.4,'<':56.4,'>':56.4,
  '[':33.3,']':33.3,'{':33.3,'}':33.3,'|':22.2,'~':50,'^':50,'€':50,'£':50,'•':33.3,
  '’':18.02,'‘':18.02,'“':40.82,'”':40.82,'…':75,'·':27.78
};
const TABLES = {helvetica: W100_HN, sf: W100_SF};
let W100 = TABLES.helvetica;
export function setMetricFont(name) { W100 = TABLES[name] ?? W100; }
function charWidth(ch) {
  if (ch === undefined || ch === '️') return 0;
  const direct = W100[ch];
  if (direct !== undefined) return direct;
  const cp = ch.codePointAt(0);
  if (cp >= 0x1F000 || (cp >= 0x2600 && cp <= 0x2BFF)) return 100;         // emoji ~1em
  if (cp >= 0x4E00 && cp <= 0x9FFF || cp >= 0x3040 && cp <= 0x30FF || cp >= 0xAC00 && cp <= 0xD7AF) return 95; // CJK
  return 50;                                                             // default mid
}
/** Width of a single line of copy in px at the given fontSize. */
export function measureLine(text, fontSize = 17) {
  let units = 0;
  for (const ch of String(text)) units += charWidth(ch);
  return units * fontSize / 100;
}
/** Word-wrap copy into lines no wider than maxWidth. Respects \n. Never breaks inside
 *  a word; a single too-long word keeps its width and reports via overflow flag. */
export function wrapText(copy, fontSize = 17, maxWidth = 240) {
  const lines = [];
  let overflow = false;
  for (const para of String(copy).split('\n')) {
    const words = para.split(/(\s+)/).filter(s => s.length);
    let line = '';
    for (const word of words) {
      const candidate = line + word;
      if (line !== '' && !/^\s+$/.test(word) && measureLine(candidate, fontSize) > maxWidth) {
        lines.push(line.trimEnd());
        line = word;
      } else line = candidate;
      if (measureLine(word, fontSize) > maxWidth) overflow = true;
    }
    lines.push(line.trimEnd() || ' ');
  }
  const widths = lines.map(l => measureLine(l, fontSize));
  return { lines, widths, maxLineWidth: Math.max(...widths, 0), overflow };
}
/** Full bubble text box: line count, widest line px, box height px. */
export function textBox(copy, fontSize = 17, maxWidth = 240, lineHeight) {
  const lh = lineHeight ?? Math.round(fontSize * 1.2 * 2) / 2;
  const { lines, widths, maxLineWidth, overflow } = wrapText(copy, fontSize, maxWidth);
  return { lines, widths, maxLineWidth, lineHeight: lh, height: lines.length * lh, overflow };
}
