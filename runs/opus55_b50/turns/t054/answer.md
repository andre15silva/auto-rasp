106.6 s on the evaluation machine — far over. The pass-2 file includes the full residual stream, so I can directly look for tiny-but-nonzero values (denormal suspects) to see which SOps carry them.

```python
import numpy as np, json, re
d = np.load('/work/pass_2/compiled.npz', allow_pickle=True)
res = d['residual']; labels = d['residual_labels']
print(res.shape, res.dtype)
a = np.abs(res)
for th in [1e-38, 1e-30, 1e-20, 1e-10, 1e-6]:
    print(th, ((a > 0) & (a < th)).sum())
tiny = (a > 0) & (a < 1e-20)
cnt = tiny.sum(axis=(0,1))
order = np.argsort(-cnt)
for j in order[:30]:
    if cnt[j] == 0: break
    print(labels[j], cnt[j], a[:,:,j][tiny[:,:,j]].min())
# also BOS row vs others
print('tiny in BOS row:', tiny[:,0,:].sum(), 'others:', tiny[:,1:,:].sum())
```