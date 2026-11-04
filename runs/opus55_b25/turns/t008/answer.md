```python
prog = r'''
from tracr.rasp import rasp

def nbr_sel(dr, dc):
    def pred(k, q):
        if q >= 81: return False
        r, c = divmod(q, 9)
        r2, c2 = r + dr, c + dc
        if not (0 <= r2 < 9 and 0 <= c2 < 9): return False
        return k == r2 * 9 + c2
    return rasp.Select(rasp.indices, rasp.indices, pred)

def program():
    toks = rasp.tokens
    nb = [rasp.categorical(rasp.Aggregate(nbr_sel(dr, dc), toks)) for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]]
    vals = [rasp.numerical(rasp.Map(lambda t: 1.0 if t == '.' else 0.0, n)) for n in nb]
    s = rasp.numerical(rasp.LinearSequenceMap(vals[0], vals[1], 1.0, 1.0))
    s2 = rasp.numerical(rasp.LinearSequenceMap(vals[2], vals[3], 1.0, 1.0))
    out = rasp.numerical(rasp.LinearSequenceMap(s, s2, 1.0, 1.0))
    return out
'''
open('/work/program.py','w').write(prog)
res = compile_program()
print(type(res))
print({k: (v if not isinstance(v, (list,tuple)) or len(v) < 20 else str(v[:20])+'...') for k, v in (res.items() if isinstance(res, dict) else [])})
```