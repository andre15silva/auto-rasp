Two problems: the tactical term `t1` reads 0 where the reference expects values, and pass logits are 0. Let me inspect the raw residual values of those SOps.

```python
import numpy as np, re
d = np.load('/work/pass_5/compiled.npz', allow_pickle=True)
K = {re.sub(r'_\d+$', '', k): k for k in d.keys()}
labs = [str(l) for l in d['residual_labels']]; res = d['residual']
def dims(prefix): return [j for j, l in enumerate(labs) if l.split(':')[0] == K[prefix]]
for nm in ['t1c', 't1', 'pNS', 't6c', 't6', 'pstate', 'side', 't4', 't5', 'logits']:
    js = dims(nm)
    v = res[0, 1 + 1, js]   # position 1 (index 1) of pos 0
    print(nm, len(js), 'nonzero dims at pt1:', [(labs[j], round(float(res[0, 2, j]), 3)) for j in js if abs(res[0, 2, j]) > 1e-6][:6])
print('pass position 81:', [(labs[j], round(float(res[0, 82, j]), 3)) for j in dims('t6c') + dims('t6') + dims('pstate') + dims('side') if abs(res[0, 82, j]) > 1e-6])
```