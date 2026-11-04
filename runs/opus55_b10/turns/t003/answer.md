```python
import os, re, tracr
TR = os.path.dirname(tracr.__file__)
helper = r'''
import os, re, tracr
TR = os.path.dirname(tracr.__file__)
def show(path, pattern, before=5, after=40, maxn=3):
    src=open(os.path.join(TR,path)).read().split('\n')
    n=0
    for k,l in enumerate(src):
        if re.search(pattern,l):
            print(f'--- {path}:{k}'); print('\n'.join(src[max(0,k-before):k+after])); n+=1
            if n>=maxn: break
'''
open('/work/_show.py','w').write(helper)
import sys; sys.path.insert(0,'/work')
from _show import show
show('craft/chamber/categorical_attn.py', r'def categorical_attn', 0, 110, 1)
show('craft/chamber/numerical_mlp.py', r'def map_numerical_mlp|def linear_sequence_map_numerical_mlp|def map_numerical_to_categorical', 0, 40, 4)
```