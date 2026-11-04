```python
import shutil
shutil.copy('/work/program.py', '/work/program_final.py')
src = open('/work/program.py').read()
src = src.replace("DANGW = 20.0\nCONTACT = 4", "DANGW = 20.0\nCONTACT = 5.5")
open('/work/program.py','w').write(src)
print('CONTACT = 5.5' in src)
import sys; sys.path.insert(0,'/work')
import importlib, program
importlib.reload(program)
res = compile_program()
```