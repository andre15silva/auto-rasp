Let me write some Go-rule code to study how many alternating horizontal/vertical "run" propagation steps are needed to spread information across groups in realistic-ish positions.

```python
import numpy as np, random, os
os.makedirs('/work/tools', exist_ok=True)
code = r'''
import numpy as np, random
N=9
NB=[[] for _ in range(81)]
for i in range(81):
    r,c=divmod(i,9)
    for dr,dc in((-1,0),(1,0),(0,-1),(0,1)):
        rr,cc=r+dr,c+dc
        if 0<=rr<9 and 0<=cc<9: NB[i].append(rr*9+cc)
def group(board,i):
    col=board[i]; st=[i]; seen={i}; libs=set()
    while st:
        j=st.pop()
        for k in NB[j]:
            if board[k]==0: libs.add(k)
            elif board[k]==col and k not in seen: seen.add(k); st.append(k)
    return seen,libs
def play(board,i,col,ko=None):
    """returns new board, captured count, new ko point, or None if illegal"""
    if board[i]!=0 or i==ko: return None
    b=board.copy(); b[i]=col; cap=[]
    for k in NB[i]:
        if b[k]==-col:
            g,l=group(b,k)
            if not l: cap+=list(g)
    for k in set(cap): b[k]=0
    g,l=group(b,i)
    if not l: return None
    nko=None
    if len(set(cap))==1 and len(g)==1 and len(l)==1: nko=cap[0]
    return b,len(set(cap)),nko
def is_eye(board,i,col):
    if board[i]!=0: return False
    return all(board[k]==col for k in NB[i])
def random_game(nmoves, seed=None):
    rng=random.Random(seed)
    b=np.zeros(81,int); col=1; ko=None
    for m in range(nmoves):
        cands=[i for i in range(81) if b[i]==0 and not is_eye(b,i,col)]
        rng.shuffle(cands)
        done=False
        for i in cands:
            r=play(b,i,col,ko)
            if r is not None:
                b,_,ko=r; done=True; break
        if not done: ko=None
        col=-col
    return b,col
'''
open('/work/tools/gorules.py','w').write(code)
import sys; sys.path.insert(0,'/work/tools')
import importlib, gorules; importlib.reload(gorules)
from gorules import *

def runs(board):
    # horizontal and vertical run ids for each point (same color incl empty)
    h=[None]*81; v=[None]*81
    for r in range(9):
        for c in range(9):
            i=r*9+c
            h[i]= h[i-1] if c>0 and board[i-1]==board[i] else i
            v[i]= v[i-9] if r>0 and board[i-9]==board[i] else i
    return h,v
def steps_needed(board, start='H'):
    h,v=runs(board)
    worst=0
    res=[]
    for col in (1,-1,0):
        seen=set()
        for i in range(81):
            if board[i]!=col or i in seen: continue
            g,_=group(board,i) if col!=0 else (None,None)
            if col==0:
                # empty region
                st=[i]; g={i}
                while st:
                    j=st.pop()
                    for k in NB[j]:
                        if board[k]==0 and k not in g: g.add(k); st.append(k)
            seen|=g
            # BFS from each node in alternating metric
            gl=list(g); mx=0
            for s in gl:
                know={s}; k=0; typ=start
                while len(know)<len(g):
                    k+=1
                    ids = h if typ=='H' else v
                    know = {j for j in g if ids[j] in {ids[x] for x in know}}
                    typ = 'V' if typ=='H' else 'H'
                    if k>40: break
                mx=max(mx,k)
            res.append((col,len(g),mx))
    return res
allres=[]
for seed in range(60):
    for nm in (30,60,90,120):
        b,_=random_game(nm,seed*1000+nm)
        allres+= [(nm,)+x for x in steps_needed(b)]
import collections
for col in (1,0):
    for nm in (30,60,90,120):
        d=collections.Counter(min(x[3],12) for x in allres if x[0]==nm and (x[1]!=0)==(col!=0))
        print('stones' if col else 'empty', nm, sorted(d.items()))
```