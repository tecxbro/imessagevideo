from pathlib import Path
import json,html
root=Path(__file__).resolve().parent
q=json.loads((root/'findings.json').read_text())
sections=[]
for f in q['findings']+q.get('followup_findings',[]):
 sections.append(f'<article><h2>{html.escape(f["source"])} {f["time"]}s · {html.escape(f["severity"])}</h2><p>{html.escape(f["observation"])}</p><p>{html.escape(f["status"])}</p><a href="{html.escape(f["evidence"])}"><img loading="lazy" src="{html.escape(f["evidence"])}"></a></article>')
page='<!doctype html><meta charset="utf-8"><title>Independent fidelity review</title><style>body{max-width:1600px;margin:auto;padding:28px;font:16px system-ui;background:#f4f5f7;color:#111}article{background:white;padding:20px;margin:20px 0;border-radius:12px}img{width:100%}h2{font-size:21px}p{line-height:1.6}a{color:#1466cc}</style><h1>Independent fidelity review</h1><p>'+html.escape(q['gate'])+'</p><p>'+html.escape(q['raster_assistance'])+'</p><p><a href="05-boarding/index.html">Linq boarding exposure</a> · <a href="02-capsule-collapse/index.html">Daniel capsule collapse</a> · <a href="05-flight/index.html">Linq continuous flight document</a> · <a href="05-games-exit/index.html">Linq Games exit</a> · <a href="05-menu-games/index.html">Linq menu/Games handoff</a> · <a href="02-intro/index.html">Daniel opening correction</a> · <a href="06-intro/index.html">Rene opening camera/state correction</a> · <a href="01-title-lifetimes/index.html">PhotonHQ title lifetime correction</a> · <a href="01-intro/index.html">PhotonHQ intro + CTA accepted correction</a> · <a href="02-birth/index.html">Photon02 five-frame field birth</a> · <a href="02-phonebook-branch/index.html">Photon02 accepted isolated corrections</a> · <a href="final-small-checks/index.html">Latest retained native checkpoints</a> · <a href="broad-cache/index.html">Mapped partial-cache timeline QA</a> · <a href="broad-encoded/index.html">Completed encoded timeline QA</a> · <a href="sample-metrics.json">Initial native-still metrics</a> · <a href="findings.json">Versioned findings</a> · <a href="steps.md">Step log</a> · <a href="v4-pairs.jpg">Linq/Rene v4 comparisons</a></p>'+''.join(sections)
(root/'index.html').write_text(page)
lines=['# Independent fidelity review','',q['gate'],'',q['raster_assistance'],'',
       'Initial metrics describe initial preview snapshots. Verified later corrections are recorded separately below.','']
for f in q['findings']+q.get('followup_findings',[]):
 lines.append(f"- **{f['source']} {f['time']}s — {f['severity']}**: {f['observation']} Status: {f['status']}. [Pair]({f['evidence']}).")
(root/'findings.md').write_text('\n'.join(lines)+'\n')
