```python
import shutil
shutil.copy('/work/program_final.py', '/work/program.py')
src = open('/work/program.py').read()
src = src.replace("DANGW = 20.0\nCONTACT = 4", "DANGW = 20.0\nCONTACT = 3")
open('/work/program.py','w').write(src)
print('CONTACT = 3\n' in src, 'ZC = 0.12, 10.0' in src)
import sys; sys.path.insert(0,'/work')
import importlib, program
importlib.reload(program)
res = compile_program()
```