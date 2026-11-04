```python
import os, tracr
root = os.path.dirname(tracr.__file__)
src = open(root + '/compiler/compiling.py').read()
i = src.find('def compile_rasp_to_model')
print(src[i:i+3000])
```