"""Reproduce the measured90-state Mail fix from immutableV16."""
from pathlib import Path
import json
from apply_mail_edit_v17 import apply_mail_edit
from apply_mail_return_copy_v17 import apply_return_copy
P=Path(__file__).resolve().parent
scene=json.loads((P/'final-v16.scene.json').read_text())
scene=apply_mail_edit(scene)
scene=apply_return_copy(scene)
scene['source']['notes']+=' V17 Mail230–309/335–344: true selection242–267,deletion268–269,25partialtyping states270–309,onecaret/nativeglyphs,measuredgraybacksheetY/fill,andverifiedsinglebezelaboveUI.335–341retain originallayout withbakedcaret removed/finalperiodrestored;only342–344use independentlymeasuredfinalcopyplane. Originalphysical/UI/papercameras,310–334specialfade,345+paneexit andallworldactorspreserved. No new runtime raster asset.'
(P/'joint-v17-provisional.scene.json').write_text(json.dumps(scene,indent=2)+'\n')
print('JointV17provisionalcomplete')
