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

DIRS = [(-1,0),(1,0),(0,-1),(0,1)]
def program():
    x = rasp.categorical(rasp.Map(lambda t: {'.':0,'x':1,'o':2}.get(t, 3), rasp.tokens))
    acc = None
    for it in range(10):
        nb = [rasp.categorical(rasp.Aggregate(nbr_sel(dr, dc), x)) for dr, dc in DIRS]
        a = rasp.categorical(rasp.SequenceMap(lambda u, v: (u * 5 + v) % 30, nb[0], nb[1]))
        b = rasp.categorical(rasp.SequenceMap(lambda u, v: (u * 3 + v) % 30, nb[2], nb[3]))
        x = rasp.categorical(rasp.SequenceMap(lambda u, v: (u + 2 * v) % 30, a, b))
    out = rasp.numerical(rasp.Map(lambda v: v / 30, x))
    return out
'''
open('/work/program.py','w').write(prog)
res = compile_program()
```