```python
import os, tracr
base = os.path.dirname(tracr.__file__)
s=open(base+'/craft/chamber/numerical_mlp.py').read()
i=s.find('def map_numerical_to_categorical_mlp')
print(s[i:])
s=open(base+'/compiler/basis_inference.py').read()
i=s.find('"""')
print(s[i:])
```