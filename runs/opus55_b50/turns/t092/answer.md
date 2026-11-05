Let me verify v4's features against a reference implementation (neighbour classes with size flag, tactical score, eyes, influence bins, Tromp-Taylor class, pass term).

```python
import sys, json, re, numpy as np, importlib
sys.path.insert(0,'/work/tools'); sys.path.insert(0,'/work')
import refv3, gonet4; importlib.reload(gonet4); importlib.reload(refv3)
from gorules import NB, group
d = np.load('/work/pass_5/compiled.npz', allow_pickle=True)
inp = json.load(open('/work/pass_5/inputs.json'))
K = {re.sub(r'_\d+$', '', k): k for k in d.keys()}
A = lambda n: d[K[n]]
def nbt(q, dd): return gonet4.nb_target(q, gonet4.ORTH[dd])
bad = {'nb':0, 't1':0, 'eye':0, 'bX':0, 'tt':0, 'neu':0}
for n, pos in enumerate(inp):
    rel = refv3.board_rel(pos)
    cnt_i, reg = refv3.ideal(rel)
    nbr = []
    for i in range(81):
        if rel[i] == 0: nbr.append('E'); continue
        col = 'X' if rel[i] == 1 else 'O'
        ml = any(rel[k] == rel[i] for k in NB[i])
        c = min(cnt_i[i], 3)
        nbr.append(gonet4.nbcls if False else None)
        nbr[-1] = (lambda col, c, ml: ('X1m' if ml else 'X1s') if (col=='X' and c==1) else ('X2' if (col=='X' and c==2) else ('X3' if col=='X' else (('O1m' if ml else 'O1s') if c==1 else ('O2' if c==2 else 'B')))))(col, c if c>0 else 3, ml)
    nbr.append('B')
    NBI = A('nbinfo')[n]
    for i in range(81):
        if rel[i] != 0 and str(NBI[i]) != nbr[i]: bad['nb'] += 1
    t1 = A('t1')[n]; eye = A('eye')[n]; bXa = A('bX')[n]; bOa = A('bO')[n]
    for i in range(81):
        if rel[i] != 0: continue
        l = [nbr[nbt(i, dd)] for dd in 'NSWE']
        v = gonet4.tactical(l)
        if abs(float(t1[i]) - v) > 1e-3:
            bad['t1'] += 1
            if bad['t1'] < 4: print('t1', n, i, float(t1[i]), v, l)
        # eye
        orth = [rel[nbt(i, dd)] if nbt(i, dd) < 81 else 2 for dd in 'NSWE']
        if all(o in (1, 2) for o in orth):
            onedge = 2 in orth
            diag = []
            for dd in gonet4.DIAG.values():
                t = gonet4.nb_target(i, dd); diag.append(rel[t] if t < 81 else 2)
            nO = diag.count(-1)
            e = 'eye' if (nO < (1 if onedge else 2)) else 'feye'
        else: e = 'no'
        if str(eye[i]) != e: bad['eye'] += 1
        # influence window r2
        win = [k for k in range(81) if gonet4.mdist(k, i) <= 2]
        fx = sum(rel[k] == 1 for k in win) / len(win); fo = sum(rel[k] == -1 for k in win) / len(win)
        bf = lambda f: 0 if f < 0.04 else 1 if f < 0.13 else 2 if f < 0.25 else 3
        if int(bXa[i]) != bf(fx) or int(bOa[i]) != bf(fo): bad['bX'] += 1
    # TT
    own = sum(1 for i in range(81) if rel[i] == 1 or (rel[i] == 0 and reg[i] == 'own'))
    opp = sum(1 for i in range(81) if rel[i] == -1 or (rel[i] == 0 and reg[i] == 'opp'))
    dd_ = own - opp
    tc = 0 if dd_ <= -16 else 1 if dd_ <= -8 else 2 if dd_ <= -1 else 3 if dd_ == 0 else 4 if dd_ <= 7 else 5 if dd_ <= 15 else 6
    neu = sum(1 for i in range(81) if rel[i] == 0 and reg[i] not in ('own', 'opp'))
    nc = 0 if neu == 0 else 1 if neu <= 2 else 2 if neu <= 5 else 3
    if int(A('ttcls')[n][81]) != tc: bad['tt'] += 1; print('tt', n, A('ttcls')[n][81], tc, dd_)
    if int(A('neucls')[n][81]) != nc: bad['neu'] += 1; print('neu', n, A('neucls')[n][81], nc, neu)
print(bad)
lg = np.load('/work/pass_5/logits.npy'); print('pass logits sample', lg[:10, 81])
```