Still 69 s. Let me bisect the exact configuration by stage (each stage measured twice) to see where time goes.

```python
for stop in ['prop', 'prop', 'nbinfo', 'nbinfo']:
    open('/work/program.py','w').write(f'''
import sys
sys.path.insert(0, '/work')
import importlib, gonet
importlib.reload(gonet)
MLP_EXACTNESS = 1000
def program():
    return gonet.build(stop={stop!r})
''')
    print(stop, end=' '); r = compile_program()
```