Now 106M params / 32 layers; the speed measurements are noisy, so I want to get comfortably below ~80M. Plan: (a) cheaper delayed query (Map of qA), (b) fold the stone color into the row-count sum tree so one map yields (color, row-count) and one SequenceMap yields the category (−1 level), (c) drop the fetch cleaning (relu in the SequenceMaps removes leaks; the remaining mass deficit is a near-uniform scale). Let me first confirm from pass 1 (uncleaned fetches) that the tactical-class mass is uniform across board points.

```python
import numpy as np, json
d = np.load('/work/pass_1/compiled.npz', allow_pickle=True)
labels = [str(l) for l in d['residual_labels']]
res = d['residual']
ix = [i for i,l in enumerate(labels) if l.split(':')[0]=='tcat_4']
inp = json.load(open('/work/pass_1/inputs.json'))
m = []
for n in range(len(inp)):
    for i in range(81):
        if inp[n]['tokens'][i] == '.':
            m.append(res[n][1+i][ix].sum())
m = np.array(m)
print(len(m), m.min(), m.max(), np.quantile(m, [0.01, 0.5, 0.99]))
```