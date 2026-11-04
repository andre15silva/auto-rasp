```python
code = r'''
import numpy as np
from tracr.compiler import compiling
def metrics(prog_fn, exact=1000):
    m = compiling.compile_rasp_to_model(prog_fn(), vocab={".", "x", "o", "B", "W"}, max_seq_len=82, compiler_bos="BOS", mlp_exactness=exact)
    P = m.params
    dense = rc = rows = cols = 0
    per = []
    for k, v in P.items():
        if 'transformer' not in k: continue
        w = np.asarray(v['w']); nz = np.abs(w) > 0
        r = nz.any(1).sum(); c = nz.any(0).sum()
        dense += w.size; rc += r * c; rows += r * w.shape[1]; cols += w.shape[0] * c
        per.append((k, w.shape, int(r), int(c)))
    return dict(dense=dense/1e6, rc=rc/1e6, rows=rows/1e6, cols=cols/1e6, L=m.model_config.num_layers), per, m
def load_prog(src):
    ns = {}
    exec(src, ns)
    return ns['program']
'''
open('/work/tools/met.py','w').write(code)
import sys, importlib, time
sys.path.insert(0,'/work/tools'); sys.path.insert(0,'/work')
import met; importlib.reload(met)
base_toy = r'''
from tracr.rasp import rasp
def program():
    t = rasp.tokens
    idx = rasp.indices
    def nb(k, q):
        if k >= 81 or q >= 81: return 0
        kr, kc = divmod(k, 9); qr, qc = divmod(q, 9)
        return 5.0 if abs(kr-qr) + abs(kc-qc) <= 1 else 0
    sel = rasp.Select(idx, idx, nb)
    flags = [rasp.numerical(rasp.Map(lambda v, j=j: 1 if (v == '.' and j%2==0) else 0, t)) for j in range(14)]
    cats = [rasp.categorical(rasp.Map(lambda v, j=j: (v + j) % 82, idx)) for j in range(NCAT)]
    for step in range(8):
        new = []
        for j, f in enumerate(flags):
            a = rasp.numerical(rasp.Aggregate(sel, f, default=0))
            b = rasp.numerical(rasp.Map(lambda x: 0 if x < 1e-9 else (1 if abs(x-0.2)<1e-9 else None), a))
            new.append(b)
        flags = new
        cats = [rasp.categorical(rasp.Aggregate(sel, c)) for c in cats]
    lv = flags + [rasp.numerical(rasp.Map(lambda v: 1 if v == 3 else 0, c)) for c in cats]
    while len(lv) > 1:
        lv = [rasp.numerical(rasp.LinearSequenceMap(lv[i], lv[i+1], 1, 1)) for i in range(0, len(lv)-1, 2)] + ([lv[-1]] if len(lv)%2 else [])
    return lv[0]
'''
for ncat in [0, 2]:
    print('toy ncat', ncat, met.metrics(met.load_prog(base_toy.replace('NCAT', str(ncat))))[0])
import gonet; importlib.reload(gonet)
gonet.UNSEL = 0.0
t0=time.time()
res = met.metrics(lambda: gonet.build())
print('full', res[0], time.time()-t0)
```