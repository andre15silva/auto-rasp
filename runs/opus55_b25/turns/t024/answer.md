```python
import numpy as np
d = np.load('/work/pass_1/compiled.npz', allow_pickle=True)
R = d['residual']; labels = list(d['residual_labels'])
print(R.shape, len(labels))
def vec(pos, i, prefix):
    out = {}
    for j, l in enumerate(labels):
        if l.startswith(prefix + ':') or l == prefix:
            v = R[pos, i+1, j]
            if abs(v) > 1e-12: out[l.split(':',1)[1] if ':' in l else l] = float(v)
    return out
pref = {k.rsplit('_',1)[0]: k for k in d.files if '_' in k}
for name in ['M0','T0','A1','T1','T5','A6','W','tab2']:
    print(name, vec(1, 0, pref[name]))
print('tab2 at 39', vec(1, 39, pref['tab2']))
print('tacP', vec(1,39,pref['tacP']))
```