```python
import shutil
shutil.copy('/work/program_final_candidate.py', '/work/program.py')
src = open('/work/program.py').read()
src = src.replace("ZTH, ZC = 0.12, 2.3", "ZTH, ZC = 0.12, 10.0")
open('/work/program.py','w').write(src)
import sys; sys.path.insert(0,'/work')
import importlib, program
importlib.reload(program)
res = compile_program()
```