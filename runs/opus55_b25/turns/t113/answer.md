```python
import json, numpy as np
from collections import deque
G = json.load(open('/work/pass_19/games.json'))
B = np.load('/work/pass_19/boards.npy')
def show(arr):
    ch = {1:'X',-1:'O',0:'.'}
    return '\n'.join(' '.join(ch[int(v)] for v in arr[r*9:(r+1)*9]) for r in range(9))
def nb(i):
    r,c=divmod(i,9); return [(r+dr)*9+c+dc for dr,dc in ((-1,0),(1,0),(0,-1),(0,1)) if 0<=r+dr<9 and 0<=c+dc<9]
def analyze(board, s):
    col = board[s]; dist = {s:0}; dq = deque([s])
    while dq:
        u = dq.popleft()
        for v in nb(u):
            if board[v]==col and v not in dist: dist[v]=dist[u]+1; dq.append(v)
    libs = {}
    for u,dd in dist.items():
        for v in nb(u):
            if board[v]==0: libs[v] = min(libs.get(v,99), dd)
    return len(dist), sorted(libs.values())
for i in [57, 68, 89]:
    g = G[i]; mv = g['moves']; last = mv[-1]['ply']; fin = B[i,last]
    s0 = [p for p in range(last) if (B[i,p]==fin).all()][0]
    m = mv[s0+1]; p = m['move']
    print('game', i, 'net', g['net_color'], 'move', divmod(p,9), m['top5'][:3])
    bd = B[i, s0]
    print(show(bd))
    for q in nb(p):
        if bd[q] != 0: print('  nbr', divmod(q,9), 'color', bd[q], analyze(bd, q))
```