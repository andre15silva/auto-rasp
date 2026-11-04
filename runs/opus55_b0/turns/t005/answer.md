```python
import os, tracr
root = os.path.dirname(tracr.__file__)
src = open(root + '/craft/chamber/categorical_attn.py').read()
print(src[600:])
src = open(root + '/compiler/expr_to_craft_graph.py').read()
print(src[:2000])
```