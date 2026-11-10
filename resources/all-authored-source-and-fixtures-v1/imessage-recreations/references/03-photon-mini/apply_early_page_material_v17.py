"""Give the receding Messages page its own material instead of stretching display white."""
from pathlib import Path
import copy,json
P=Path(__file__).resolve().parent

def apply_page_material(scene):
    scene=copy.deepcopy(scene)
    root=next(layer for layer in scene['layers'] if layer['id']=='p03-86')
    ui=next(layer for layer in root['children'] if layer['id']=='early-messages-ui-v13')
    black=dict(id='early-physical-black-display-v17',type='rect',x=28,y=30,width=744,height=1600,radius=120,fill='#000000',start=211/30,end=230/30,semanticText='Physical black display beneath receding Messages page')
    index=next(i for i,layer in enumerate(root['children']) if layer['id']=='p03-9')
    root['children'].insert(index+1,black)
    white=dict(id='early-receding-page-white-material-v17',type='rect',x=28,y=30,width=744,height=1600,radius=120,fill='#fdfdfd',start=211/30,end=230/30,semanticText='White Messages page recedes under its existing independently measured UI camera')
    ui['children'].insert(0,white)
    scene['early_page_material_v17']=dict(scope=[211,229],notice='Separate native black physical display and native white receding Messages page. Existing ink/camera/dimming/foregroundMail/hardware stay independent. This corrects material ownership; no source artwork or full-frame layer.')
    return scene

if __name__=='__main__':
    scene=json.loads((P/'final-v15.scene.json').read_text())
    (P/'early-page-material-v17-prototype.scene.json').write_text(json.dumps(apply_page_material(scene),indent=2))
    print('built isolated native early material prototype')
