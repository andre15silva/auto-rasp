```python
import os, tracr
root = os.path.dirname(tracr.__file__)
src = open(root + '/compiler/craft_graph_to_model.py').read()
print(src[700:])
```