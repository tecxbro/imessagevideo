from pathlib import Path
p=Path('/workspace/imessage-recreations/references/01-photonhq/build-scenes.py');s=p.read_text()
old="L.append(group(mail,9.5,10.7,keyframes={'x':k((9.5,-240,None),(10.7,180,None))}));L.append(center('100,000+ emails',466,96,9.5,10.7,width=680))"
new="""# Higher fidelity native camera over declared static notification artwork. Each asset is ONE notification/card artwork, never a whole reference frame or a video.
card_boxes=[(137,0,934,91),(988,0,1785,91),(0,111,510,275),(558,111,1359,275),(1412,111,1920,275),(0,293,80,457),(137,293,934,457),(988,293,1785,457),(1840,293,1920,457),(0,621,510,785),(558,621,1359,785),(1412,621,1920,785),(0,804,80,968),(137,804,934,968),(988,804,1785,968),(1840,804,1920,968),(0,990,510,1080),(558,990,1359,1080),(1412,990,1920,1080)]
artcards=[]
for idx,box in enumerate(card_boxes):
 src=crop(R1,f'notification-art-{idx:02d}.png',10,box,False)
 artcards.append(image(src,box[0],box[1],box[2]-box[0],box[3]-box[1]))
L.append(group(artcards,9.5,10.666667,originX=960,originY=540,keyframes={'x':k((9.5,39,None),(10,0,None),(10.666667,-52,None)),'scaleX':k((9.5,.955,None),(10,1,None),(10.666667,1.06,None)),'scaleY':k((9.5,.955,None),(10,1,None),(10.666667,1.06,None)),'opacity':k((9.5,0,None),(9.73,1,'easeOut'))}))
L.append(center('100,000+ emails',486,96,9.5,10.666667,width=680))"""
assert old in s;s=s.replace(old,new);p.write_text(s)
