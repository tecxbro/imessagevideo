from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent;a=R/'scene-candidate.json';b=R/'helper-candidate.scene.json';x=json.loads(a.read_text());y=json.loads(b.read_text())
for d in[x,y]:
 d.pop('phonebook_v14',None);d.pop('phonebook_grid_review',None)
identical=x==y;report={'candidate':str(a),'helperOutput':str(b),'candidateSha256':hashlib.sha256(a.read_bytes()).hexdigest(),'helperOutputSha256':hashlib.sha256(b.read_bytes()).hexdigest(),'drawingAndAllOriginalMetadataIdentical':identical,'onlyExcludedFields':['phonebook_v14','phonebook_grid_review']};(R/'helper-equivalence.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));assert identical
