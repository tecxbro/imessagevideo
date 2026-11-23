import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.optimize import least_squares

project = Path('sidehoe-skill-trial/hyperframes-review/project')
scratch = Path('/tmp/sidehoe-hyperframes.wG3QA2')
scene_path = project/'scene.json'
scene = json.loads(scene_path.read_text())
tracks = scene['tracks']
def stage(frame):
    return np.array(Image.open(scratch/'source-stage'/f'{frame:06}.png').convert('RGB'),dtype=np.int16)

poses = []
lighting = []
sample_y, sample_x = np.mgrid[0:1000:10, 0:1000:10]
fields = np.array([[.88,1.07,.178,.315,.368],[-.799,1.5,.651,.585,2.0]])
for frame in range(134,162):
    a = stage(frame)
    dark = a.max(axis=2)<175
    paired = (dark[:,:120].sum(1)>3)&(dark[:,-120:].sum(1)>3)
    left = np.where(dark[:,:120]&paired[:,None])[1]
    right = np.where(dark[:,880:]&paired[:,None])[1]
    x0, x1 = np.quantile(left,.01), np.quantile(right,.99)+881
    y0 = np.argmax(dark[250:,365:635].sum(1)>210)+249
    poses.append([frame,round(float(x0),2),int(y0),round(float(x1-x0),2)])
    v = a[sample_y,sample_x]
    neutral = (v[:,:,0]>206)&(v[:,:,2]>212)
    paper = ((sample_x<35)|(sample_x>968)|(sample_y<y0-10)
             |((sample_x>107)&(sample_x<888)&(v[:,:,0]>218)&(v[:,:,2]>225)))
    use=neutral&paper
    y,x=sample_y[use]/999,sample_x[use]/999
    predict=[]
    for cx,cy,sx,sy,shear in fields:
        predict.append(np.exp(-((x-cx+shear*(y-cy))/sx)**2-((y-cy)/sy)**2))
    predict=np.array(predict).T
    target=253-v[use].astype(float)
    coeff=[]
    for j in range(3):
        def residual(q):
            return predict @ q - target[:,j]
        coeff.append(least_squares(residual,[1,1],bounds=([-12,-12],[182,210]),
                                   loss='soft_l1',f_scale=2).x)
    parameters=np.hstack((fields,np.array(coeff).T)).flatten()
    lighting.append([frame,*np.round(parameters,4).tolist()])
tracks['assistantMeasuredPosition'] = poses
tracks['assistantLighting'] = lighting

widths = {
    176:(271,463.5,464,63),
    178:(267.5,463.5,471,62.5),
    180:(266,463.5,475,62.5),
    184:(264,459.75,478,63),
    187:(263.5,441.25,479.5,63),
    188:(263.5,438.75,479.5,63),
    191:(263,431.75,480.5,63),
    195:(262.5,419.25,481.5,63.5),
    198:(262.5,406.25,481.5,63.5),
    201:(262.5,387.75,482,63),
    205:(265.5,350.25,479,61.5),
    207:(265.5,325.25,477,63.5),
    208:(266,309,482,58),
    210:(271,254,483,59),
    211:(270,211,478,59),
    212:(264,129,476,61),
}
tracks['personalLine1'] = [v for v in tracks['personalLine1'] if v[0]<176] + [[f,*v] for f,v in widths.items()]
tracks['personalLine2'] = [
    [177,240,531,518,82],[181,240,527,517,88],[184,240,520,519,88],
    [187,239.5,499.75,519.5,90],[188,239.5,497.25,520,90],
    [191,239,489.75,521.5,91],[195,238.5,477.75,523,91],
    [198,238,464,527,91.5],[201,238,445.75,530,91.5],[205,241.5,406.75,526.5,89],
    [207,242,377,523,90],[208,244,361,522,89],[210,249,303,524,86],
    [211,248,258,525,86],[212,243,189,520,87]]
# Order keeps the larger foreground shapes over the smaller distant shapes.
# Each row is frame, x, y, width, height, angle and opacity.
heart_tracks = [
 [[178,242,560,2,2,15,0],[184,246,523,19,18,15,.49],[191,245,479,25,24,12,.55],[195,244,457,26,25,11,.45],[203,244,401,26,25,9,.10],[208,245,324,26,25,8,0]],
 [[177,235,567,2,2,16,0],[181,225,555,21,20,13,.55],[187,215,523,29,27,14,.58],[191,210,509,33,29,14,.60],[195,206,493,36,31,15,.50],[201,202,464,35,31,17,.26],[206,201,427,34,30,18,0]],
 [[179,249,582,2,2,17,0],[184,239,567,28,27,17,.65],[188,235,541,38,36,19,.75],[191,231,532,42,39,18,.79],[195,230,518,45,42,19,.68],[201,228,483,45,43,20,.50],[208,228,413,45,43,21,0]],
 [[177,468,564,2,2,10,0],[181,461,538,16,15,9,.55],[187,456,500,23,21,12,.55],[191,454,484,25,22,9,.52],[196,453,465,26,23,7,.36],[204,452,412,26,23,8,.04],[208,452,335,26,23,7,0]],
 [[180,469,576,2,2,26,0],[184,474,561,29,29,26,.59],[188,478,533,37,38,28,.72],[191,481,524,42,42,27,.77],[195,482,509,44,44,27,.60],[201,484,479,44,44,24,.32],[208,486,409,44,44,22,0]],
 [[180,766,560,2,2,-8,0],[184,779,516,18,17,-6,.56],[188,785,473,22,20,-5,.59],[191,789,456,24,22,-6,.61],[195,792,434,26,23,-6,.48],[202,799,390,26,23,-6,.16],[208,803,312,26,23,-6,0]],
 [[178,775,563,2,2,8,0],[184,780,548,18,17,9,.53],[188,789,515,24,22,9,.63],[191,793,501,27,26,10,.68],[195,796,484,29,26,10,.63],[201,804,449,29,26,10,.39],[208,807,370,29,26,10,0]],
 [[179,750,571,2,2,15,0],[184,754,558,27,26,15,.63],[188,754,532,38,35,16,.68],[191,754,521,41,37,15,.74],[195,755,507,43,40,15,.64],[201,759,474,44,41,16,.35],[208,764,405,44,41,17,0]],
 [[179,777,586,2,2,-18,0],[184,768,578,28,27,-15,.63],[188,771,552,40,36,-17,.73],[191,774,542,44,38,-17,.78],[195,775,529,47,42,-18,.70],[201,777,493,47,42,-19,.42],[208,779,426,47,42,-18,0]]
]
tracks['personalHearts'] = heart_tracks

for row in tracks['calendarTileTreatment']:
    if 479 <= row[0] <= 618:
        row[1] += 6 if row[0] >= 575 else 2
for row in tracks['blueOrbit']:
    if 594 <= row[0] <= 619:
        row[1] = (row[1] + 500) / 2
        row[3] += 5
path = scratch/'fitted-cursor.json'
if path.is_file():
    tracks['followPointerStage'] = [row[0] for row in json.loads(path.read_text())]
with scene_path.open('w') as f:
    json.dump(scene,f,ensure_ascii=False,indent=2)
    f.write('\n')
