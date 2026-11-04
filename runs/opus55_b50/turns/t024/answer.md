The non-zero count doesn't matter. Let me run controlled experiments varying residual width D, MLP width M and heads H to learn what drives their timing.

```python
base_toy = r'''
from tracr.rasp import rasp
MLP_EXACTNESS = 1000
EXTRA_D = {extra_d}
EXTRA_M = {extra_m}
NFLAGS = {nflags}
NSTEPS = {nsteps}
def program():
    t = rasp.tokens
    idx = rasp.indices
    def nb(k, q):
        if k >= 81 or q >= 81: return 0
        kr, kc = divmod(k, 9); qr, qc = divmod(q, 9)
        return 5.0 if abs(kr-qr) + abs(kc-qc) <= 1 else -5.0
    sel = rasp.Select(idx, idx, nb)
    flags = [rasp.numerical(rasp.Map(lambda v, j=j: 1 if (v == '.' and j%2==0) else 0, t)) for j in range(NFLAGS)]
    for step in range(NSTEPS):
        new = []
        for j, f in enumerate(flags):
            a = rasp.numerical(rasp.Aggregate(sel, f, default=0))
            b = rasp.numerical(rasp.Map(lambda x: 0 if x < 1e-9 else (1 if abs(x-0.5)<1e-9 else None), a))
            new.append(b)
        flags = new
    lv = flags
    if EXTRA_D:
        big = rasp.categorical(rasp.Map(lambda v: v % EXTRA_D, rasp.categorical(rasp.SequenceMap(lambda a, b: a*100+b, idx, rasp.categorical(rasp.Map(lambda v: v % 50, idx))))))
        lv = lv + [rasp.numerical(rasp.Map(lambda v: 0, big))]
    if EXTRA_M:
        a1 = rasp.categorical(rasp.Map(lambda v: v % EXTRA_M, idx)); a2 = rasp.categorical(rasp.Map(lambda v: (v*7) % 40, idx))
        sm = rasp.categorical(rasp.SequenceMap(lambda a, b: (a+b) % 3, a1, a2))
        lv = lv + [rasp.numerical(rasp.Map(lambda v: 0, sm))]
    while len(lv) > 1:
        lv = [rasp.numerical(rasp.LinearSequenceMap(lv[i], lv[i+1], 1, 1)) for i in range(0, len(lv)-1, 2)] + ([lv[-1]] if len(lv)%2 else [])
    return lv[0]
'''
configs = [dict(extra_d=0, extra_m=0, nflags=14, nsteps=8),
           dict(extra_d=800, extra_m=0, nflags=14, nsteps=8),
           dict(extra_d=0, extra_m=80, nflags=14, nsteps=8),
           dict(extra_d=0, extra_m=0, nflags=28, nsteps=8),
           dict(extra_d=0, extra_m=0, nflags=14, nsteps=16)]
for cfg in configs:
    s = base_toy
    for k, v in cfg.items(): s = s.replace('{'+k+'}', str(v))
    open('/work/program.py','w').write(s)
    print(cfg)
    r = compile_program()
```