I'll start by exploring the sandbox and Tracr's source to understand what the compiler produces.

```python
import os, sys, tracr, inspect
print(sys.version)
root = os.path.dirname(tracr.__file__)
print(root)
for dp, dn, fn in os.walk(root):
    for f in fn:
        if f.endswith('.py') and 'test' not in f:
            p = os.path.join(dp, f)
            print(p.replace(root, ''), os.path.getsize(p))
print(os.listdir('/work'))
import numpy, jax
print(numpy.__version__, jax.__version__)
print(os.cpu_count())
```