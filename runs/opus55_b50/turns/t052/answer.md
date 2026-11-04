```python
import numpy as np, json, sys, re
sys.path.insert(0,'/work/tools'); sys.path.insert(0,'/work')
from gorules import NB, group
import importlib, gonet; importlib.reload(gonet)
d = np.load('/work/pass_2/compiled.npz', allow_pickle=True)
inp = json.load(open('/work/pass_2/inputs.json'))
K = {re.sub(r'_\d+$', '', k): k for k in d.keys()}
def A(name): return d[K[name]]
def ref(pos):
    b = np.zeros(81, int)
    for r, row in enumerate(pos['board']):
        for c, ch in enumerate(row):
            b[r*9+c] = {'.':0,'X':1,'O':-1}[ch]
    me = 1 if pos['to_move']=='black' else -1
    rel = b * me
    nr = np.zeros(81,int); ncl = np.zeros(81,int); nlib = np.zeros(81,int)
    for i in range(81):
        if rel[i] != 0:
            g, L = group(rel, i)
            nr[i] = len({x//9 for x in L}); ncl[i] = len({x%9 for x in L}); nlib[i] = len(L)
    return rel, nr, ncl, nlib
bad_cr = 0; bad_nb = 0; bad_t1 = 0; tot = 0
cls_conf = {}
for n, pos in enumerate(inp):
    rel, nr, ncl, nlib = ref(pos)
    cr = A('cr')[n]; nbi = A('nbinfo')[n]; t1c = A('t1c')[n]
    refnb = []
    for i in range(81):
        if rel[i] == 0: refnb.append('E'); continue
        col = 'X' if rel[i]==1 else 'O'
        exp_cr = str((col, int(min(nr[i],3))))
        if str(cr[i]) != exp_cr:
            bad_cr += 1
            if bad_cr < 8: print('cr mismatch pos', n, 'pt', i, cr[i], exp_cr)
        e = gonet.nbcls((col, min(nr[i],3)), min(ncl[i],3))
        refnb.append(e)
        if str(nbi[i]) != e: bad_nb += 1
        key = (e, min(nlib[i], 4)); cls_conf[key] = cls_conf.get(key, 0) + 1
    refnb.append('B')
    for i in range(81):
        if rel[i] != 0: continue
        nbs = []
        for dd in ('N','S','W','E'):
            t = gonet.nb_target(i, gonet.ORTH[dd]); nbs.append(refnb[t])
        v = gonet.tactical(tuple(sorted(nbs[:2])), tuple(sorted(nbs[2:])))
        tot += 1
        if abs(float(t1c[i]) - v) > 1e-6:
            bad_t1 += 1
            if bad_t1 < 5: print('t1 mismatch', n, i, t1c[i], v, nbs)
print('bad cr', bad_cr, 'bad nb', bad_nb, 'bad t1', bad_t1, 'of', tot)
print('class vs true libs:', sorted(cls_conf.items()))
lg = np.load('/work/pass_2/logits.npy')
print('nan logits:', np.isnan(lg).sum(), 'max', np.nanmax(lg), 'min', np.nanmin(lg))
```