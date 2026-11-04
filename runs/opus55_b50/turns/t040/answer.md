None of the structural metrics explain the timings, so the slowness must be numerical. One crucial possibility: if their softmax does not subtract the max, logits > 709 (float64) overflow to inf → NaN (and my current network would output NaN!). Let me test toys with huge vs moderate selector logits.

```python
toy4 = r'''
from tracr.rasp import rasp
MLP_EXACTNESS = 1000
SELV = {selv}
def program():
    t = rasp.tokens
    idx = rasp.indices
    def nb(k, q):
        if k >= 81 or q >= 81: return SELV if k == q else 0
        kr, kc = divmod(k, 9); qr, qc = divmod(q, 9)
        return SELV if abs(kr-qr) + abs(kc-qc) <= 1 else 0
    sel = rasp.Select(idx, idx, nb)
    flags = [rasp.numerical(rasp.Map(lambda v, j=j: 1 if (v == '.' and j%2==0) else 0, t)) for j in range(14)]
    for step in range(8):
        new = []
        for j, f in enumerate(flags):
            a = rasp.numerical(rasp.Aggregate(sel, f, default=0))
            b = rasp.numerical(rasp.Map(lambda x: 0 if x < 1e-9 else (1 if abs(x-0.2)<1e-9 else None), a))
            new.append(b)
        flags = new
    lv = flags
    while len(lv) > 1:
        lv = [rasp.numerical(rasp.LinearSequenceMap(lv[i], lv[i+1], 1, 1)) for i in range(0, len(lv)-1, 2)] + ([lv[-1]] if len(lv)%2 else [])
    return lv[0]
'''
for selv in [5.0, 100.0, 5.0, 100.0, 40.0]:
    open('/work/program.py','w').write(toy4.format(selv=selv))
    print(selv, end=' '); r = compile_program()
```