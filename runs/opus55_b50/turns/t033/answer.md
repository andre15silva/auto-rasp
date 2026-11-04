The timing is erratic. Let me measure the noise directly by compiling the same small model three times.

```python
open('/work/program.py','w').write('''
import sys
sys.path.insert(0, '/work')
import importlib, gonet
importlib.reload(gonet)
gonet.UNSEL = 0.0
MLP_EXACTNESS = 1000
def program():
    return gonet.build(stop='prop')
''')
for i in range(3):
    r = compile_program()
```