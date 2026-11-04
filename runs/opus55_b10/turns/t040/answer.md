The downstream pipeline is exact; the only logit mismatches come from the ReLU in categorical→numerical maps clipping very negative tactical scores (offset too small). Let me implement: T_OFF=30, per-round cleaning of diffusion states (and seeds) via a near-one constant, a lower decode threshold, and 8 diffusion rounds; then check compile cost.

```python
s = open('/work/go.py').read()
s = s.replace("R_ROUNDS = 6\nEPS_DEC = 6e-4      # decode threshold is EPS_DEC/2",
              "R_ROUNDS = 8\nEPS_DEC = 8e-5      # decode threshold is EPS_DEC/2\nNEAR_N = 30        # keys averaged for the near-one constant (theta = BOS share)")
s = s.replace("T_OFF = 20.0", "T_OFF = 30.0")
s = s.replace("""    seedsel = rasp.Select(idx, qB, LEQ)          # neighbours + index 81""",
"""    seedsel = rasp.Select(idx, qB, LEQ)          # neighbours + index 81
    # near-one constant: one-hot 'c' with magnitude 1 - theta (theta = BOS attention share)
    constc = cmap(lambda i: 'c', idx)
    nq = cmap(lambda i: NEAR_N, idx)
    nearone = rasp.Aggregate(rasp.Select(idx, nq, LT), constc).named('nearone')
    cleanf = lambda v, c: v
    def clean(x): return smap(cleanf, x, nearone)""")
s = s.replace("""    sr = smap(stonly, rasp.Aggregate(seedsel, rowE), tok).named('seed_r')
    sc = smap(stonly, rasp.Aggregate(seedsel, colE), tok).named('seed_c')
    for k in range(R_ROUNDS):
        sel = selr if k % 2 == 0 else selc
        sr = rasp.Aggregate(sel, sr).named('sr%d' % k)
        sc = rasp.Aggregate(sel, sc).named('sc%d' % k)""",
"""    sr = clean(smap(stonly, rasp.Aggregate(seedsel, rowE), tok)).named('seed_r')
    sc = clean(smap(stonly, rasp.Aggregate(seedsel, colE), tok)).named('seed_c')
    for k in range(R_ROUNDS):
        sel = selr if k % 2 == 0 else selc
        sr = clean(rasp.Aggregate(sel, sr)).named('sr%d' % k)
        sc = clean(rasp.Aggregate(sel, sc)).named('sc%d' % k)""")
open('/work/go.py','w').write(s)
import sys; sys.path.insert(0,'/work'); sys.setrecursionlimit(10000)
import importlib, go, estimate
importlib.reload(go)
print(estimate.estimate(go.program()))
```