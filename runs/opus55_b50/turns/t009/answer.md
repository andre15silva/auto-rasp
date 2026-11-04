```python
import os, tracr
base = os.path.dirname(tracr.__file__)
print(os.listdir(base+'/transformer'))
s=open(base+'/transformer/attention.py').read()
i=s.find('def __call__')
print(s[i:i+4000])
s=open(base+'/transformer/model.py').read()
i=s.find('class Transformer')
print(s[i:i+3500])
```