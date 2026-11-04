Now I understand the cost model: positional heads are nearly free; each data-dependent head costs ~1 s per 1000 positions. My 48 EQ propagation heads are the problem. New idea: **bundle all flags into one categorical SOp** (multi-hot over 8 liberty buckets + X/O region markers) and propagate it with ONE head per step (categorical aggregation averages vectors, so the support = OR-union is preserved), thresholding only once at the end. The risk is decay of values (divided by run length each step). Let me simulate the exact mean-propagation on realistic positions to see the minimum surviving value.

```python
import numpy as np, sys, collections
sys.path.insert(0,'/work/tools')
from gorules import NB, group
from ana import load
g, B, V = load(1)
def bucket(i): return (i // 9 + 3 * (i % 9)) % 8
def runs(board):
    h=[None]*81; v=[None]*81
    for r in range(9):
        for c in range(9):
            i=r*9+c
            h[i]= h[i-1] if c>0 and board[i-1]==board[i] else i
            v[i]= v[i-9] if r>0 and board[i-9]==board[i] else i
    return h,v
def simulate(b, N):
    # bundle: dims 0..7 buckets, 8 = X(own=+1), 9 = O
    X = np.zeros((81, 10))
    for i in range(81):
        nb = NB[i]; vals = []
        for k in nb:
            if b[k] == 0: vals.append(bucket(k))
            elif b[k] == 1: vals.append(8)
            else: vals.append(9)
        for vv in vals: X[i, vv] += 1.0 / len(nb)
    h, v = runs(b)
    for s in range(N):
        ids = h if s % 2 == 0 else v
        Y = np.zeros_like(X)
        groups = collections.defaultdict(list)
        for i in range(81): groups[ids[i]].append(i)
        for gid, mem in groups.items():
            m = X[mem].mean(0)
            Y[mem] = m
        X = Y
    return X
mins = {6: [], 8: []}
miss = {6: 0, 8: 0}; total = 0
for gi in range(0, 128, 2):
    n = int(V[gi].sum())
    for p in range(20, n, 10):
        b = B[gi, p]
        for N in (6, 8):
            X = simulate(b, N)
            nz = X[X > 0]
            mins[N].append(nz.min())
for N in (6, 8):
    a = np.array(mins[N])
    print(N, 'min over positions:', a.min(), 'percentiles 1/5/50:', np.percentile(a, [1, 5, 50]))
```