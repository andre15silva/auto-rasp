```python
import json, numpy as np
G = json.load(open('/work/pass_17/games.json'))
B = np.load('/work/pass_17/boards.npy')
def nb(i):
    r,c=divmod(i,9); return [(r+dr)*9+c+dc for dr,dc in ((-1,0),(1,0),(0,-1),(0,1)) if 0<=r+dr<9 and 0<=c+dc<9]
def chain(board, s):
    col=board[s]; seen={s}; st=[s]
    while st:
        u=st.pop()
        for v in nb(u):
            if board[v]==col and v not in seen: seen.add(v); st.append(v)
    libs={v for u in seen for v in nb(u) if board[v]==0}
    return seen, libs
# for each loss: find the biggest capture of our stones; trace that chain's liberty count over the preceding 12 plies, and our moves
for i, g in enumerate(G):
    if g['result'] != -1: continue
    netc = 1 if g['net_color']=='black' else -1
    last = g['moves'][-1]['ply']; best=(0,None)
    for p in range(1,last+1):
        lost = int(((B[i,p-1]==netc)&(B[i,p]==0)).sum())
        if lost > best[0]: best=(lost,p)
    lost, p = best
    if lost < 5: continue
    dead = [s for s in range(81) if B[i,p-1][s]==netc and B[i,p][s]==0]
    s0 = dead[0]; hist=[]
    mv = {m['ply']: m for m in g['moves']}
    for q in range(p-12, p):
        if B[i,q][s0] != netc: hist.append((q,'-')); continue
        ch, libs = chain(B[i,q], s0)
        who = mv[q+1]['by'][0] if q+1 in mv else '?'
        nxt = mv[q+1]['move'] if q+1 in mv else None
        hist.append((q, len(ch), len(libs), who, nxt in libs if nxt is not None else None))
    print('game', i, g['net_color'], 'margin', g['margin'], 'lost', lost, 'at', p, hist)
```