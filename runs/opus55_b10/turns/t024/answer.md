The logits are off from what the tables should give (e.g., pass should be 48, got 39.05). Let me inspect the activations to find where values diverge.

```python
import numpy as np, json, sys
sys.path.insert(0,'/work')
d = np.load('/work/pass_1/compiled.npz', allow_pickle=True)
keys = list(d.keys())
print(len(keys))
named = [k for k in keys if not any(k.startswith(p) for p in ('map_','sequence_map_','aggregate_','linear_sequence_map_','selector_width_'))]
print(named)
inp = json.load(open('/work/pass_1/inputs.json'))
print(type(inp), len(inp), inp[0].keys() if isinstance(inp, list) else inp.keys())
logits = np.load('/work/pass_1/logits.npy')
for k in ['tcat','pcat','logit','cst','lcls','nr','nc','cN']:
    kk = [x for x in keys if x.startswith(k)]
    for x in kk:
        print(x, d[x].shape, d[x].dtype, d[x][72][:12] if d[x].ndim>1 else d[x][:5])
```