"""Apply frozen, independently measured genuine-Memoji component state."""
import copy,json

def apply(scene,p):
    by={l['id']:l for l in scene['layers']};fps=scene['fps'];fits=json.loads((p/'measurements-v8/favorites-state-fit-v11.json').read_text())['layers']
    for id in['p0007','p0010']:
        original=by[id];late=copy.deepcopy(original);original['end']=109/fps;late['start']=109/fps
        def rename(node):
            node['id']='v11-late-'+node['id']
            for child in node.get('children',[]):rename(child)
        rename(late);scene['layers'].insert(scene['layers'].index(original)+1,late)
        for group in[original,late]:
            image=group['children'][0];state=fits[group['id']];image['src']=state['src'];image['keyframes']=copy.deepcopy(state['keyframes'])
    return scene
