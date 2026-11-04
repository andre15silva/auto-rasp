```python
import numpy as np, json, sys, re
sys.path.insert(0,'/work/tools')
from gorules import NB, group
d = np.load('/work/pass_2/compiled.npz', allow_pickle=True)
inp = json.load(open('/work/pass_2/inputs.json'))
K = {re.sub(r'_\d+$', '', k): k for k in d.keys()}
def A(name): return d[K[name]]
print(A('cr')[0][:10], A('cc3')[0][:10], A('nbinfo')[0][:10], A('region')[0][:10], A('hrun')[0][:10])
def ref(pos):
    b = np.zeros(81, int)
    for r, row in enumerate(pos['board']):
        for c, ch in enumerate(row):
            b[r*9+c] = {'.':0,'X':1,'O':-1}[ch]
    me = 1 if pos['to_move']=='black' else -1
    rel = b * me   # 1 = own (x), -1 = opp (o)
    nr = np.zeros(81,int); ncl = np.zeros(81,int); reg = ['']*81
    for i in range(81):
        if rel[i] != 0:
            g, L = group(rel, i)
            nr[i] = len({x//9 for x in L}); ncl[i] = len({x%9 for x in L})
        else:
            st=[i]; seen={i}; tx=to=False
            while st:
                j=st.pop()
                for k in NB[j]:
                    if rel[k]==0 and k not in seen: seen.add(k); st.append(k)
                    elif rel[k]==1: tx=True
                    elif rel[k]==-1: to=True
            reg[i] = 'own' if tx and not to else 'opp' if to and not tx else 'both' if tx else 'none'
    return rel, nr, ncl, reg
bad = {'cr':0, 'cc3':0, 'region':0}
tot = 0
for n, pos in enumerate(inp):
    rel, nr, ncl, reg = ref(pos)
    cr = A('cr')[n]; cc = A('cc3')[n]; rg = A('region')[n]
    for i in range(81):
        if rel[i] != 0:
            tot += 1
            exp_cr = str(('X' if rel[i]==1 else 'O', min(nr[i],3)))
            if str(cr[i]) != exp_cr:
                bad['cr'] += 1
                if bad['cr'] < 6: print('cr mismatch pos', n, 'pt', i, cr[i], exp_cr)
            if str(cc[i]) != str(min(ncl[i],3)):
                bad['cc3'] += 1
        else:
            if str(rg[i]) != reg[i]:
                bad['region'] += 1
                if bad['region'] < 6: print('region mismatch', n, i, rg[i], reg[i])
print(bad, tot)
```