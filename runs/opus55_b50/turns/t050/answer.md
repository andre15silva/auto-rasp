```python
import numpy as np, json, sys, re
sys.path.insert(0,'/work/tools')
from gorules import NB, group
d = np.load('/work/pass_2/compiled.npz', allow_pickle=True)
inp = json.load(open('/work/pass_2/inputs.json'))
keys = {re.sub(r'_\d+$', '', k): k for k in d.keys()}
print(sorted(keys)[:400])
print(inp[0].keys())
```