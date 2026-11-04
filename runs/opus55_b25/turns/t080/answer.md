```python
import json, numpy as np
from collections import deque
G = json.load(open('/work/pass_12/games.json'))
B = np.load('/work/pass_12/boards.npy')
def nb(i):
    r,c=divmod(i,9); return [(r+dr)*9+c+dc for dr,dc in ((-1,0),(1,0),(0,-1),(0,1)) if 0<=r+dr<9 and 0<=c+dc<9]
def analyze(board, s):
    col = board[s]
    dist = {s:0}; dq = deque([s])
    while dq:
        u = dq.popleft()
        for v in nb(u):
            if board[v]==col and v not in dist: dist[v]=dist[u]+1; dq.append(v)
    libs = {}
    for u,dd in dist.items():
        for v in nb(u):
            if board[v]==0: libs[v] = min(libs.get(v,99), dd)
    return len(dist), sorted(libs.values())
for gi_, ply, s in [(91, 78, 17), (19, 77, 2), (66, 86, 46)]:
    print(gi_, ply, divmod(s,9), analyze(B[gi_, ply], s))
# general stats: in pass 12 games, how often a chain adjacent to an empty point has its nearest 2nd liberty beyond 6+8 hops
```