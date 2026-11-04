```python
import shutil
shutil.copy('/work/program.py', '/work/program_best.py')
src = open('/work/program.py').read()
src = src.replace("SCALE = 3.0", "SCALE = 4.5")
open('/work/program.py','w').write(src)
import sys; sys.path.insert(0,'/work')
import importlib, program
importlib.reload(program)
res = compile_program()
```