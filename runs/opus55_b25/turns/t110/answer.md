```python
import shutil
shutil.copy('/work/program_best.py', '/work/program.py')
src = open('/work/program.py').read()
src = src.replace("        if v is None or v is False: return -FSC\n", "        if v is None or v is False: return -20.0 * FSC\n")
src = src.replace("BIG = 1e6", "BIG = 1e8")
src = src.replace("F_HOPS = 4\nFGAIN = 2000.0", "F_HOPS = 4\nFGAIN = 1e6")
src = src.replace("ZTH, ZC = 0.12, 10.0", "ZTH, ZC = 0.12, 2.3")
open('/work/program.py','w').write(src)
for k in ["-20.0 * FSC", "BIG = 1e8", "FGAIN = 1e6", "ZC = 0.12, 2.3", "SCALE = 3.0"]:
    print(k, k in src)
import sys; sys.path.insert(0,'/work')
import importlib, program
importlib.reload(program)
res = compile_program()
```