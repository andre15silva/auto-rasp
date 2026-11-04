```python
import os, tracr
root = os.path.dirname(tracr.__file__)
src = open(root + '/compiler/assemble.py').read()
i = src.find('def _get_model_config_and_module_names')
print(src[i:i+5000])
```