```python
import os, tracr
root = os.path.dirname(tracr.__file__)
src = open(root + '/transformer/attention.py').read()
i = src.find('def __call__')
print(src[i:i+3500])
src = open(root + '/transformer/model.py').read()
i = src.find('class Transformer')
print(src[i:i+3500])
```