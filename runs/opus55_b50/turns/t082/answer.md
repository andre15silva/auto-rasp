Compile time explodes in the tail even for small additions. Let me read Tracr's MLP `combine_in_parallel` and `Linear.from_action` to find the quadratic cost.

```python
import os, tracr, inspect
base = os.path.dirname(tracr.__file__)
s = open(base+'/craft/vectorspace_fns.py').read()
i = s.find('class Linear'); print(s[i:i+3500])
s2 = open(base+'/craft/transformers.py').read()
i = s2.find('def combine_in_parallel'); print(s2[i-200:i+2500])
s3 = open(base+'/craft/bases.py').read()
for kw in ['def join_vector_spaces', 'def __contains__', 'def project', 'def vector_from_basis_direction', 'def direct_sum']:
    i = s3.find(kw); print('-----', kw); print(s3[i:i+700])
```