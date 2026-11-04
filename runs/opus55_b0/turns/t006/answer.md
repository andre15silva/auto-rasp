```python
import os, tracr
root = os.path.dirname(tracr.__file__)
src = open(root + '/craft/chamber/categorical_mlp.py').read()
i = src.find('def map_categorical_mlp')
print(src[i:])
```