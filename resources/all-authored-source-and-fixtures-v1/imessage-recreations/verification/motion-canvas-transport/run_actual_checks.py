from pathlib import Path
import subprocess,sys,time
mode=sys.argv[1];R=Path('verification/motion-canvas-transport');engine='engines/render_motion_canvas.before-transport.mjs' if mode=='old' else 'engines/render_motion_canvas.mjs'
for n in [420,421,422,423,599,735]:
 scene=R/f'actual-{n}-manual-exact.json' if mode=='old' else Path('outputs/02-danieltian/final-v12/scene.json');cmd=['node',engine,'--scene',str(scene),'--out',str(R/f'actual-{n}-{mode}.png'),'--frame',str(n)];t=time.monotonic()
 with (R/f'actual-{n}-{mode}.log').open('w') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True)
 print(mode,n,round(time.monotonic()-t,3),flush=True)
