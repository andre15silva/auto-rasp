```python
src = open('/work/program.py').read()
src = src.replace("        if k == 0: return (0.1 + 2.0) if q == 'F' else 0.1\n", "        if k == 0: return (0.1 + 5.0) if q == 'F' else 0.1\n")
open('/work/program.py','w').write(src)
import sys; sys.path.insert(0,'/work')
import importlib, program
importlib.reload(program)
res = compile_program()
```