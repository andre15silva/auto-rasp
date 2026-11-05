The pass logit is correctly 49 (−8 relative), but every alternative scored even lower (≈ −15 relative). Let me decompose the score terms of the remaining empty points.

```python
import numpy as np, re, json, sys
sys.path.insert(0,'/work/tools')
from ana import show2
d = np.load('/work/pass_7/compiled.npz', allow_pickle=True)
K = {re.sub(r'_\d+$', '', k): k for k in d.keys()}
A = lambda n: d[K[n]]
inp = json.load(open('/work/pass_7/inputs.json'))
lg = np.load('/work/pass_7/logits.npy')
for n in [0, 1]:
    print('\n'.join(inp[n]['board']))
    toks = inp[n]['tokens']
    for i in range(81):
        if toks[i] == '.':
            print(i, divmod(i, 9), 'logit', round(float(lg[n, i]), 1), 't1', round(float(A('t1')[n][i]) - 25, 1), 't4', round(float(A('t4')[n][i]) - 20, 1),
                  't5', round(float(A('t5')[n][i]) - 2, 1), 'pNS', A('pNS')[n][i], 'pWE', A('pWE')[n][i], 'eye', A('eye')[n][i], 'reg', A('region')[n][i], 'infl', A('infl')[n][i])
```