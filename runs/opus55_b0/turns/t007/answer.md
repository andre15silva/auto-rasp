```python
import os, tracr
root = os.path.dirname(tracr.__file__)
src = open(root + '/craft/chamber/numerical_mlp.py').read()
i = src.find('class DiscretisingLayerMaterializer')
print(src[i:])
```