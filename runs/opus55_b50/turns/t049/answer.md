The network runs without NaNs. Now let me verify the compiled features against my own Go-rule computations (liberty row/col counts, neighbour classes, regions, eyes).

```python
import numpy as np, json, sys
sys.path.insert(0,'/work/tools'); sys.path.insert(0,'/work')
from gorules import NB, group
import importlib, gonet; importlib.reload(gonet)
d = np.load('/work/pass_2/compiled.npz', allow_pickle=True)
inp = json.load(open('/work/pass_2/inputs.json'))
print(list(d.keys())[:10], len(d.keys()))
print(d['nbinfo'].shape, d['nbinfo'][0][:12])
def ref_feats(pos):
    toks = pos['tokens'] if 'tokens' in pos else None
    return toks
print(inp[0].keys())
print(inp[0]['tokens'][:20] if 'tokens' in inp[0] else inp[0])
```