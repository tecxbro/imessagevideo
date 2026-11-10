#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parents[2]
raise SystemExit(subprocess.call([sys.executable,str(root/'tools/render_example.py'),'--example','02-danieltian','--method','gsap',*sys.argv[1:]],cwd=root))
