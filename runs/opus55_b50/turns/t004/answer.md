```python
import os, tracr
base = os.path.dirname(tracr.__file__)
for f in ['craft/chamber/categorical_attn.py','craft/chamber/categorical_mlp.py','craft/chamber/numerical_mlp.py']:
    s=open(base+'/'+f).read()
    # strip license
    i=s.find('"""')
    print('=====',f); print(s[i:])
```