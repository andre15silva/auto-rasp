Let me verify v3 against both the ideal (full-group) features and an exact simulation of the 6-step bundle algorithm.

```python
code = r'''
import numpy as np, collections, sys
sys.path.insert(0, '/work'); sys.path.insert(0, '/work/tools')
from gorules import NB, group
import gonet
def board_rel(pos):
    b = np.zeros(81, int)
    for r, row in enumerate(pos['board']):
        for c, ch in enumerate(row):
            b[r*9+c] = {'.':0,'X':1,'O':-1}[ch]
    me = 1 if pos['to_move'] == 'black' else -1
    return b * me
def runs(board):
    h=[None]*81; v=[None]*81
    for r in range(9):
        for c in range(9):
            i=r*9+c
            h[i]= h[i-1] if c>0 and board[i-1]==board[i] else i
            v[i]= v[i-9] if r>0 and board[i-9]==board[i] else i
    return h,v
def bundle_sim(rel, N):
    X = np.zeros((81, 10))
    for i in range(81):
        nb = NB[i]
        for k in nb:
            vv = gonet.bucket(k) if rel[k] == 0 else (8 if rel[k] == 1 else 9)
            X[i, vv] += 1.0 / len(nb)
    h, v = runs(rel)
    for s in range(N):
        ids = h if s % 2 == 0 else v
        groups = collections.defaultdict(list)
        for i in range(81): groups[ids[i]].append(i)
        Y = np.zeros_like(X)
        for gid, mem in groups.items(): Y[mem] = X[mem].mean(0)
        X = Y
    return X
def ideal(rel):
    """per point: (bucket count over full group libs) for stones; region (tx,to) for empty"""
    cnt = np.zeros(81, int); reg = [None]*81
    for i in range(81):
        if rel[i] != 0:
            g, L = group(rel, i); cnt[i] = len({gonet.bucket(x) for x in L})
        else:
            st=[i]; seen={i}; tx=to=False
            while st:
                j=st.pop()
                for k in NB[j]:
                    if rel[k]==0 and k not in seen: seen.add(k); st.append(k)
                    elif rel[k]==1: tx=True
                    elif rel[k]==-1: to=True
            reg[i] = 'own' if tx and not to else 'opp' if to and not tx else 'both' if tx else 'none'
    return cnt, reg
'''
open('/work/tools/refv3.py','w').write(code)
import sys, json, re, numpy as np, importlib
sys.path.insert(0,'/work/tools'); sys.path.insert(0,'/work')
import refv3, gonet; importlib.reload(gonet); importlib.reload(refv3)
d = np.load('/work/pass_3/compiled.npz', allow_pickle=True)
inp = json.load(open('/work/pass_3/inputs.json'))
K = {re.sub(r'_\d+$', '', k): k for k in d.keys()}
A = lambda n: d[K[n]]
mis_sim = mis_ideal = mis_reg = tot = 0; minpos = 1.0
for n, pos in enumerate(inp):
    rel = refv3.board_rel(pos)
    X = refv3.bundle_sim(rel, gonet.N_PROP)
    cnt_i, reg = refv3.ideal(rel)
    c3 = A('cnt3')[n]; rg = A('region')[n]
    for i in range(81):
        if rel[i] != 0:
            tot += 1
            sim = min(int((X[i, :8] > 0).sum()), 3)
            if int(c3[i]) != sim: mis_sim += 1
            if int(c3[i]) != min(cnt_i[i], 3): mis_ideal += 1
        else:
            if str(rg[i]) != reg[i]: mis_reg += 1
        nzv = X[i][X[i] > 0]
        if len(nzv): minpos = min(minpos, nzv.min())
print('cnt3 mismatch vs bundle-sim', mis_sim, 'vs ideal', mis_ideal, 'of', tot, ' region mismatch', mis_reg, ' min bundle value', minpos)
res = d['residual']; a = np.abs(res); print('tiny residual values:', ((a > 0) & (a < 1e-20)).sum())
# check the numeric bundle values in the residual against the simulation for one position
labs = list(d['residual_labels'])
b6 = [j for j, l in enumerate(labs) if l.startswith('bund6')]
print([labs[j] for j in b6])
```