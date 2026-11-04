```python
import numpy as np
d = np.load('/work/pass_1/compiled.npz', allow_pickle=True)
labels = [str(l) for l in d['residual_labels']]
res = d['residual']
def dims(prefix):
    return [i for i,l in enumerate(labels) if l.split(':')[0] == prefix]
for name in ['tcat_4','pcat_5','cst_13','lcls_22','nr_29','cN_18','tokens','one','indices']:
    ix = dims(name)
    v = res[72][1+40][ix]   # position (4,4) -> model position 41
    v81 = res[72][1+81][ix]
    print(name, len(ix), 'sum', v.sum().round(4), 'max', v.max().round(4), 'nonzero', [(labels[ix[j]], round(float(v[j]),4)) for j in np.nonzero(np.abs(v)>1e-3)[0]][:8])
    print('   @81 sum', v81.sum().round(4), [(labels[ix[j]], round(float(v81[j]),4)) for j in np.nonzero(np.abs(v81)>1e-3)[0]][:8])
```