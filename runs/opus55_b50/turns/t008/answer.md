```python
import os, tracr
base = os.path.dirname(tracr.__file__)
s=open(base+'/rasp/rasp.py').read()
import re
for kw in ['class Comparison','class Select(','class Map(','class SequenceMap','class LinearSequenceMap','def numerical','def categorical','class Aggregate','def annotate','class Full','def evaluate']:
    i=s.find(kw); print('=====',kw); print(s[i:i+2500] if kw in ['class Comparison','class Select('] else s[i:i+1300])
```