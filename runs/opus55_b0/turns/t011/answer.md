```python
import os, tracr
root = os.path.dirname(tracr.__file__)
src = open(root + '/compiler/assemble.py').read()
i = src.find('def assemble_craft_model')
print(src[i+1500:i+7000])
```