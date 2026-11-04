```python
import os, tracr
base = os.path.dirname(tracr.__file__)
s=open(base+'/compiler/craft_graph_to_model.py').read()
i=s.find('  min_depth, max_depth = min(nodes_by_depth.keys())')
print(s[i:])
s=open(base+'/transformer/model.py').read()
i=s.find('class MultiHeadAttention')
print(s[i:i+6000])
```