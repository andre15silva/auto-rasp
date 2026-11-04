```python
import os, tracr
root = os.path.dirname(tracr.__file__)
src = open(root + '/craft/chamber/numerical_mlp.py').read()
print(len(src))
print(src[600:])
```