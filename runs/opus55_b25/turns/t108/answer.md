```python
src = open('/work/program.py').read()
src = src.replace("                return 0.1 - 3.2 * 0.5 - 8.0\n", "                return 0.1 - 3.2 * 0.5\n")
open('/work/program.py','w').write(src)
import sys; sys.path.insert(0,'/work')
import importlib, program
importlib.reload(program)
res = compile_program()
```