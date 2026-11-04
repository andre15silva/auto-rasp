```python
src = open('/work/program.py').read()
src = src.replace("F_HOPS = 4\nFGAIN = 2000.0", "F_HOPS = 8\nFGAIN = 1e6")
open('/work/program.py','w').write(src)
import sys; sys.path.insert(0,'/work')
import importlib, program
importlib.reload(program)
res = compile_program()
```