```python
import numpy as np
d = np.load('/work/pass_1/compiled.npz', allow_pickle=True)
for k in d.keys():
    v = d[k]
    if v.dtype.kind == 'f' and v.ndim == 2:
        row = v[72]
        if row.max() > 5:
            print(k, row[[0,1,10,40,81]])
labels = list(d['residual_labels'])
res = d['residual']
print(res.shape)
# find dims
for name in ['map_2','map_3']:
    print([ (i,l) for i,l in enumerate(labels) if l.startswith(name)])
```