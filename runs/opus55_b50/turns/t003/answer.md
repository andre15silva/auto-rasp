```python
import os, tracr
base = os.path.dirname(tracr.__file__)
print(open(base+'/compiler/compiling.py').read())
print(open(base+'/compiler/expr_to_craft_graph.py').read())
```