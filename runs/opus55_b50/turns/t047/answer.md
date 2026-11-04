I need to restore program.py to the full build before the pass.

```python
open('/work/program.py','w').write('''
import sys
sys.path.insert(0, '/work')
import importlib, gonet
importlib.reload(gonet)
MLP_EXACTNESS = 1000
def program():
    return gonet.build()
''')
print(open('/work/program.py').read())
```