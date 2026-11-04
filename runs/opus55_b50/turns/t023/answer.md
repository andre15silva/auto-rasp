The timing (296 s/1000 positions) is far too slow. I need to understand what drives their forward-pass cost. My predicates return −5 for unselected pairs, making every QK matrix dense; let me test whether non-zero count drives the timing.

```python
toy = r'''
from tracr.rasp import rasp
MLP_EXACTNESS = 1000
UNSEL = {unsel}
def program():
    t = rasp.tokens
    idx = rasp.indices
    def nb(k, q):
        if k >= 81 or q >= 81: return UNSEL
        kr, kc = divmod(k, 9); qr, qc = divmod(q, 9)
        return 5.0 if abs(kr-qr) + abs(kc-qc) <= 1 else UNSEL
    sel = rasp.Select(idx, idx, nb)
    flags = [rasp.numerical(rasp.Map(lambda v, j=j: 1 if (v == '.' and j%2==0) else 0, t)) for j in range(14)]
    for step in range(8):
        new = []
        for j, f in enumerate(flags):
            a = rasp.numerical(rasp.Aggregate(sel, f, default=0))
            b = rasp.numerical(rasp.Map(lambda x: 1 if x > 0.001 else 0, a))
            new.append(b)
        flags = new
    out = flags[0]
    lv = flags
    while len(lv) > 1:
        lv = [rasp.numerical(rasp.LinearSequenceMap(lv[i], lv[i+1], 1, 1)) for i in range(0, len(lv)-1, 2)] + ([lv[-1]] if len(lv)%2 else [])
    return lv[0]
'''
for unsel in ['0', '-5.0']:
    open('/work/program.py','w').write(toy.replace('{unsel}', unsel))
    r = compile_program()
```