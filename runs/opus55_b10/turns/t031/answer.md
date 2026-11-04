Found the main bug: SelectorWidth-based run ids were wrong because the start-flag keys came from a soft fetch (magnitude ≈0.994), which shifts attention scores against BOS — so runs got merged and diffusion mixed unrelated stones. The diffusion seeds themselves were correct. Let me also check why the positional class is empty at the pass index (pcat sum 0 at index 81), by dumping all categorical SOps at position 81.

```python
import numpy as np
d = np.load('/work/pass_1/compiled.npz', allow_pickle=True)
labels = [str(l) for l in d['residual_labels']]
res = d['residual']
groups = {}
for i,l in enumerate(labels):
    groups.setdefault(l.split(':')[0], []).append(i)
n = 72
for k, ix in groups.items():
    if len(ix) < 2 or len(ix) > 40: continue
    v = res[n][1+81][ix]
    nz = [(labels[ix[j]].split(':',1)[1], round(float(v[j]),3)) for j in np.nonzero(np.abs(v) > 1e-3)[0]]
    print(k, len(ix), nz[:6])
```