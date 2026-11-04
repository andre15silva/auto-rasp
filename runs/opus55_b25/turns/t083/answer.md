```python
src = open('/work/program.py').read()
src = src.replace("F_HOPS = 8\nFGAIN = 1e6", "F_HOPS = 4\nFGAIN = 2000.0")
src = src.replace("DANGW = 20.0\nCONTACT = 3", "DANGW = 20.0\nCONTACT = 4")
open('/work/program.py','w').write(src)
import sys; sys.path.insert(0,'/work')
import importlib, program
importlib.reload(program)
res = compile_program()
```