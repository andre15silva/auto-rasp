```python
toy = r'''
from tracr.rasp import rasp
MLP_EXACTNESS = 100
def program():
    t = rasp.tokens
    idx = rasp.indices
    emp = rasp.numerical(rasp.Map(lambda v: 1 if v == '.' else 0, t))
    def nb(k, q):
        if k >= 81 or q >= 81: return False
        kr, kc = divmod(k, 9); qr, qc = divmod(q, 9)
        return abs(kr-qr) + abs(kc-qc) == 1
    sel = rasp.Select(idx, idx, nb)
    libs = rasp.numerical(rasp.Aggregate(sel, emp, default=0))
    return libs
'''
open('/work/program.py','w').write(toy)
r = compile_program()
print(r if not isinstance(r, dict) else {k:(v if k!='residual_labels' else v[:20]) for k,v in r.items()})
```