const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const ts = require('./ast/node_modules/typescript');
const registryRoot = path.join(__dirname, 'upstream', 'registry', 'imessage');
const files = fs.readdirSync(registryRoot).sort();
function position(source, start, end) {
  const from = source.getLineAndCharacterOfPosition(start).line + 1;
  const to = source.getLineAndCharacterOfPosition(Math.max(start, end - 1)).line + 1;
  return {from,to};
}
function declarationName(n) {
  if (n.name) return n.name.getText();
  if (ts.isVariableStatement(n)) return n.declarationList.declarations.map(d => d.name.getText()).join(' / ');
  if (ts.isExportDeclaration(n)) return n.exportClause?.getText() ?? '*';
  return '';
}
const signatures = {
  layout: /\b(?:measure|clientWidth|clientHeight|offsetWidth|offsetHeight|getBoundingClientRect|ResizeObserver|scrollTop|scrollLeft|intersectionRatio)\b/i,
  filmRisk: /(?:Date\.now|performance\.now|requestAnimationFrame|setTimeout|setInterval|animation:|onAnimationEnd|\.animate\(|viewTransition|transitionend|@keyframes|Math\.random)/,
  interaction: /(?:Pointer|pointer(?:down|up|move|cancel)|passive|touch[A-Z]|Wheel|keydown|useLongPress)/,
  platformAsset: /(?:apple\.com|emoji|sf-symbol|unsplash|\.png|\.svg|\.woff|\.jpg|\.mp4)/i,
  shaping: /(?:Array\.from\(|Segmenter|codePointAt|charCodeAt|attr\('size'|grapheme|isEmoji)/,
  legacyProof: /(?:\bmeasured\b|unmeasured|native|assum|inferred|approximat|calibrat|reference|unverified|not yet|capture)/i,
  accessibility: /(?:aria-|role=|ariaLabel|sr-only|prefers-reduced-motion)/i,
  editing: /(?:onEdit|onChange|onSend|onChange|onSelect|onDraft|onSubmit|value\?:|contentEdit|useState|onCancel)/,
  external: /(?:MediaRecorder|AudioContext|getUserMedia|XMLHttpRequest|\bfetch\(|postMessage|window\.open|https?:\/\/)/,
};
const records = [];
for (const name of files) {
  const data = fs.readFileSync(path.join(registryRoot, name));
  const text = data.toString('utf8');
  const lines = text.split(/\r?\n/);
  if (lines.at(-1) === '') lines.pop();
  const source = ts.createSourceFile(name, text, ts.ScriptTarget.Latest, true, name.endsWith('.tsx') ? ts.ScriptKind.TSX : ts.ScriptKind.TS);
  const statements = source.statements.map(n => ({
    kind: ts.SyntaxKind[n.kind],
    name: declarationName(n),
    exported: n.modifiers?.some(m => m.kind === ts.SyntaxKind.ExportKeyword) ?? ts.isExportDeclaration(n),
    ...position(source,n.getStart(source,false),n.getEnd())
  }));
  const imports = source.statements.filter(ts.isImportDeclaration).map(n => ({module:n.moduleSpecifier.text, ...position(source,n.getStart(source,false),n.getEnd())}));
  const refs = {};
  for (const [key,re] of Object.entries(signatures)) refs[key] = lines.map((line,i) => re.test(line) ? i+1 : null).filter(Boolean);
  const functions = [];
  let syntaxNodes = 0;
  function scan(node) {
    syntaxNodes++;
    if (ts.isFunctionDeclaration(node) && node.name && !source.statements.includes(node)) {
      functions.push({name:node.name.getText(), ...position(source,node.getStart(source,false),node.getEnd())});
    }
    ts.forEachChild(node, scan);
  }
  scan(source);
  records.push({name, lines:lines.length, bytes:data.length, sha256:crypto.createHash('sha256').update(data).digest('hex'), syntaxNodes,
    parseDiagnostics:source.parseDiagnostics.map(e => ts.flattenDiagnosticMessageText(e.messageText,' ')),
    imports, statements, functions, refs,
    leadingComments:lines.map((line,i) => /^\s*(?:\/\*\*?|\* |\/\/)/.test(line) ? [i+1,line.trim()] : null).filter(Boolean),
  });
}
fs.writeFileSync(path.join(__dirname,'registry-scan.json'), JSON.stringify(records,null,2));
for (const row of records) {
  const flags = Object.entries(row.refs).map(([k,v])=>[k,v.length]).filter(([,n])=>n);
  console.log([row.name,row.lines,row.syntaxNodes,row.parseDiagnostics.length,row.statements.filter(s=>s.exported).map(s=>`${s.name}@${s.from}`).join(' '),flags.filter(([k])=>['filmRisk','shaping','external'].includes(k)).map(([k,n])=>`${k}=${n}`).join(' ')].join('\t'));
}
