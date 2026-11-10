from pathlib import Path
import json,copy
REF=Path(__file__).parent
mail=json.load(open(REF/'peaks-review-mail-elements.json'))
avatar=json.load(open(REF/'peaks-review-avatar-elements.json'))
chat=json.load(open(REF/'peaks-review-chat-elements.json'))
node_updates={identifier:dict(keyframes={'end':track})for identifier,track in mail['gates'].items()}
node_updates.update({identifier:dict(keyframes={'end':track})for identifier,track in avatar['gate_ends'].items()})
node_updates.update(copy.deepcopy(chat['node_updates']))
append_children={mail['parent_id']:copy.deepcopy(mail['append']),**copy.deepcopy(avatar['append_children'])}
before=copy.deepcopy(avatar['insert_before_root']);before.update(copy.deepcopy(chat['insert_before']))
spec=dict(node_updates=node_updates,append_children=append_children,insert_after=copy.deepcopy(mail['insert_after']),insert_before=before,changed_ranges=mail['changed_ranges']+avatar['changed_ranges']+chat['changed_ranges'],provenance=dict(mail=mail['provenance'],avatar=avatar['provenance'],chat=chat['provenance']))
(REF/'remaining-peaks-review-elements.json').write_text(json.dumps(spec,indent=2))
print(spec['changed_ranges'])
