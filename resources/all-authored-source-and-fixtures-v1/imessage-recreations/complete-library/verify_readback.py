#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,sys
p=Path(sys.argv[1]).resolve();expected=sys.argv[2];size=int(sys.argv[3])
if not str(p).startswith('/workspace/attachments/'):raise ValueError('Only the newly materialized attachment may be cleaned up')
actual=hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
if actual!=expected or p.stat().st_size!=size:raise ValueError('Private Drive readback differs from upload source; retaining diagnostic bytes')
p.unlink();print(json.dumps({'verified':True,'bytes':size,'sha256':actual,'readback_removed_after_verification':True}))
