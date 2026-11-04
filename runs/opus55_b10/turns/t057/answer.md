Two clear problems: (1) the policy is far too flat — half of our chosen moves weren't even in our top 5, and ~49% of our first-30-ply moves were on the 1st/2nd line; (2) in lost games we lose ~22 stones. Let me look at the largest captures against us in lost games to see what we missed.

```python
import json, numpy as np
g = json.load(open('/work/pass_3/games.json'))
boards = np.load('/work/pass_3/boards.npy'); valid = np.load('/work/pass_3/valid.npy')
def rows(b):
    ch = {1:'X', -1:'O', 0:'.'}
    return [''.join(ch[int(b[r*9+c])] for c in range(9)) for r in range(9)]
events = []
for i, gm in enumerate(g):
    if gm['opponent'] != 'strong' or gm['result'] > 0: continue
    netv = 1 if gm['net_color']=='black' else -1
    for p in range(1, int(valid[i].sum())):
        lost = int(((boards[i][p-1] == netv) & (boards[i][p] == 0)).sum())
        if lost >= 3: events.append((lost, i, p))
events.sort(reverse=True)
print(len(events), events[:12])
for lost, i, p in events[:4]:
    gm = g[i]
    print('game', i, 'net', gm['net_color'], 'ply', p, 'lost', lost)
    a = rows(boards[i][p-3]); b = rows(boards[i][p-2]); c = rows(boards[i][p-1]); d = rows(boards[i][p])
    for r in range(9): print('  ', a[r], b[r], c[r], d[r])
    mv = gm['moves']
    print('  moves', [(mv[k]['by'][0], mv[k]['move'], mv[k].get('top5')) for k in (p-2, p-1, p)])
```