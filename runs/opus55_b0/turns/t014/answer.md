```python
prog = r'''
from tracr.rasp import rasp
MLP_EXACTNESS = 100

def program():
    tok = rasp.tokens
    idx = rasp.indices
    emp = rasp.numerical(rasp.Map(lambda t: 1 if t == "." else 0, tok))
    def adj(k, q):
        if q >= 81 or k >= 81: return -1.0
        r1, c1 = divmod(q, 9); r2, c2 = divmod(k, 9)
        return 1.0 if abs(r1-r2)+abs(c1-c2) == 1 else -1.0
    sel = rasp.Select(idx, idx, adj)
    ne = rasp.numerical(rasp.Aggregate(sel, emp, default=0))
    out = rasp.numerical(rasp.LinearSequenceMap(ne, emp, 1.0, 0.5))
    return out
'''
open('/work/program.py','w').write(prog)
res = compile_program()
print(type(res))
if isinstance(res, dict):
    for k, v in res.items():
        print(k, v if k != 'residual_labels' else (len(v), v[:30]))
else:
    print(res)
```