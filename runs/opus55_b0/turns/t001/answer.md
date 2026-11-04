I'll start by exploring the sandbox and Tracr's source.

```python
import os, sys, inspect
import tracr
print(tracr.__file__)
root = os.path.dirname(tracr.__file__)
for d, _, fs in os.walk(root):
    for f in fs:
        if f.endswith('.py') and 'test' not in f:
            p = os.path.join(d, f)
            print(p.replace(root, ''), os.path.getsize(p))
print(os.listdir('/work'))
print(compile_program.__doc__)
try:
    print(inspect.getsource(compile_program)[:3000])
except Exception as e:
    print('no source', e)
```