Hashing liberties into 8 buckets with h = (r + 3c) mod 8 misclassifies only 1.3% of 2-liberty groups as 1 and 3% of 3+ as 2 — better than my 18-flag row/col scheme for 2-vs-3. That cuts the propagation heads from 20 to 10. Let me also check how many H/V propagation steps realistic groups need (pass-1 game positions).

```python
import numpy as np, sys, collections
sys.path.insert(0,'/work/tools')
from gorules import NB, group
from ana import load
g, B, V = load(1)
def runs(board):
    h=[None]*81; v=[None]*81
    for r in range(9):
        for c in range(9):
            i=r*9+c
            h[i]= h[i-1] if c>0 and board[i-1]==board[i] else i
            v[i]= v[i-9] if r>0 and board[i-9]==board[i] else i
    return h,v
def need(board, gset, h, v):
    # steps (starting H) until every stone knows every other stone's info
    mx = 0
    for s in gset:
        know={s}; k=0; typ='H'
        while len(know)<len(gset):
            k+=1; ids = h if typ=='H' else v
            S = {ids[x] for x in know}
            know = {j for j in gset if ids[j] in S}
            typ = 'V' if typ=='H' else 'H'
        mx=max(mx,k)
    return mx
cnt = collections.Counter(); cnt_small = collections.Counter()
for gi in range(0,128,2):
    n = int(V[gi].sum())
    for p in range(20, n, 10):
        b = B[gi,p]; h, v = runs(b); seen=set()
        for i in range(81):
            if b[i]!=0 and i not in seen:
                gr, L = group(b,i); seen|=gr
                k = need(b, gr, h, v)
                cnt[min(k,12)] += 1
                if len(L) <= 3: cnt_small[min(k,12)] += 1
print('all groups', sorted(cnt.items()))
print('groups with <=3 libs', sorted(cnt_small.items()))
tot = sum(cnt_small.values())
for K in (4,5,6,7,8):
    print(K, 'covers', sum(v for k,v in cnt_small.items() if k<=K)/tot)
```