```python
import os, tracr
base = os.path.dirname(tracr.__file__)
for f in ['compiler/assemble.py','compiler/craft_model_to_transformer.py','compiler/craft_graph_to_model.py']:
    s=open(base+'/'+f).read()
    i=s.find('"""')
    print('=====',f); print(s[i:])
```