```python
import os, tracr
root = os.path.dirname(tracr.__file__)
src = open(root + '/craft/chamber/selector_width.py').read()
print(src[1200:])
```