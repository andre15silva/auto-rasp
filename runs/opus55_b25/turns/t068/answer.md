```python
import json, numpy as np
G = json.load(open('/work/pass_7/games.json'))
B = np.load('/work/pass_7/boards.npy')
def show_boards(arrs):
    ch = {1:'X',-1:'O',0:'.'}
    return '\n'.join('   '.join(' '.join(ch[int(v)] for v in a[r*9:(r+1)*9]) for a in arrs) for r in range(9))
blow = [i for i,g in enumerate(G) if g['margin'] > 60]
for i in blow[:3]:
    g = G[i]; netc = 1 if g['net_color']=='black' else -1; last = g['moves'][-1]['ply']
    caps = []
    for p in range(1, last+1):
        k = int(((B[i,p-1]==-netc) & (B[i,p]==0)).sum())
        if k >= 4: caps.append((p, k))
    print('game', i, g['net_color'], 'len', last, 'big captures', caps)
    p = caps[0][0] if caps else last
    print(show_boards([B[i,p-10], B[i,p-5], B[i,p-1], B[i,p]]))
```