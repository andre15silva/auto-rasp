```python
import json, numpy as np
from collections import Counter
G = [g for g in json.load(open('/work/pass_11/games.json'))]
B = np.load('/work/pass_11/boards.npy')
def nb4(i):
    r,c=divmod(i,9); return [(r+dr)*9+c+dc for dr,dc in ((-1,0),(1,0),(0,-1),(0,1)) if 0<=r+dr<9 and 0<=c+dc<9]
def diag(i):
    r,c=divmod(i,9); return [(r+dr)*9+c+dc for dr,dc in ((-1,-1),(1,1),(1,-1),(-1,1)) if 0<=r+dr<9 and 0<=c+dc<9]
def two(i):
    r,c=divmod(i,9); return [(r+dr)*9+c+dc for dr,dc in ((-2,0),(2,0),(0,-2),(0,2)) if 0<=r+dr<9 and 0<=c+dc<9]
stats = {'net': Counter(), 'opponent': Counter()}
for gi, g in enumerate(G):
    netc = 1 if g['net_color']=='black' else -1
    for m in g['moves']:
        p = m['ply']
        if p >= 40 or m['move'] >= 81: continue
        who = 'net' if m['by']=='net' else 'opponent'
        me = netc if who=='net' else -netc
        prev = B[gi, p-1] if p > 0 else np.zeros(81)
        mv = m['move']
        s = stats[who]; s['n'] += 1
        own_adj = any(prev[j]==me for j in nb4(mv)); opp_adj = any(prev[j]==-me for j in nb4(mv))
        s['own_adj'] += own_adj; s['opp_adj'] += opp_adj
        s['contact_any'] += own_adj or opp_adj
        s['diag_own'] += (not own_adj) and any(prev[j]==me for j in diag(mv))
        s['jump_own'] += (not own_adj) and any(prev[j]==me for j in two(mv))
        r,c = divmod(mv,9); e=min(r,c,8-r,8-c); s[f'line{e}'] += 1
for who, s in stats.items():
    n = s['n']; print(who, {k: round(v/n,3) for k,v in sorted(s.items()) if k!='n'})
```