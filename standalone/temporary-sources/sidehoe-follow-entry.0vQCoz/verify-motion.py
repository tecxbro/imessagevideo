import hashlib
import json
from pathlib import Path
import sys
path=Path(sys.argv[1])
media=Path('/Users/darshan/Downloads/sidehoe.mp4')
def digest(x):
    return hashlib.sha256(x.read_bytes()).hexdigest()
rules=json.loads((path/'motion-plan.json').read_text())['tracks']
report=json.loads((path/'motion/motion-observations.json').read_text())
assert report['sourceSHA256']==digest(media)
assert report['planSHA256']==digest(path/'motion-plan.json')
assert report['clock']['frames']==778 and report['clock']['time_base']=='1/60000'
count=0
for rule,record in zip(rules,report['tracks'],strict=True):
    assert record['actor']==rule['id'] and record['searchRect']==rule['rect']
    assert not record['unobservedFrames'], record['actor']
    assert [s['frame'] for s in record['samples']]==list(range(rule['start'],rule['end']+1))
    for sample in record['samples']:
        assert sample['pixels']>0
        assert sample['pts']==2400*sample['frame'], sample
        assert sample['evidence']['sha256']==digest(path/'motion'/sample['evidence']['path'])
        count+=1
assert count==30
print('Verified 30 source observations, each with positive pixel count, timestamp and crop hash.')
