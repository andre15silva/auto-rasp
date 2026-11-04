Almost all liberty-row counts are wrong (nr=1 nearly everywhere), and "leak" masses are huge — so this isn't just attention softness. Let me trace the seed and each diffusion round for a single isolated stone.

```python
import numpy as np, json
d = np.load('/work/pass_1/compiled.npz', allow_pickle=True)
labels = [str(l) for l in d['residual_labels']]
res = d['residual']
groups = {}
for i,l in enumerate(labels):
    groups.setdefault(l.split(':')[0], []).append(i)
cands = [k for k,v in groups.items() if len(v)==10 and k.startswith(('aggregate','sr_','sequence_map','sc_'))]
print(cands)
n, i = 0, 11
for k in cands:
    v = res[n][1+i][groups[k]]
    print(k, [labels[j].split(':')[1] for j in groups[k]], np.round(v,4))
print('tokens at 11, nbrs', [ (j, json.load(open('/work/pass_1/inputs.json'))[0]['tokens'][j]) for j in [2,10,11,12,20]])
```