Lost games are dominated by big group deaths (26.5 stones lost vs 8.3 in wins). Let me check whether we typically kept extending a doomed group (ladder-like) before it died, i.e., whether our recent moves were placed adjacent to/within the group that was eventually captured.

```python
import json, numpy as np, sys
sys.path.insert(0,'/work')
import goref
g = json.load(open('/work/pass_7/games.json'))
boards = np.load('/work/pass_7/boards.npy'); valid = np.load('/work/pass_7/valid.npy')
stats = []
for i, x in enumerate(g):
    if x['opponent'] != 'strong' or x['result'] > 0: continue
    me = 1 if x['net_color']=='black' else -1
    for p in range(1, int(valid[i].sum())):
        dead = np.nonzero((boards[i][p-1] == me) & (boards[i][p] == 0))[0]
        if len(dead) >= 5:
            deadset = set(dead.tolist())
            # our moves in the 12 plies before: were they part of the dead group?
            ours = [m['move'] for m in x['moves'][max(0,p-12):p] if m['by']=='net']
            inside = sum(1 for m in ours if m in deadset)
            # liberties of the group 2 plies earlier (before opponent's previous move)
            b2 = [0]*81
            for j in range(81):
                v = boards[i][p-2][j]; b2[j] = 0 if v == 0 else (1 if v == me else 2)
            d0 = next(iter(deadset))
            g0, l0 = goref.group(b2, d0) if b2[d0] == 1 else (set(), set())
            stats.append((i, p, len(dead), inside, len(ours), len(l0)))
print(len(stats))
for s in stats[:25]: print(s)
print('frac of our recent moves inside dying groups', sum(s[3] for s in stats)/max(1,sum(s[4] for s in stats)))
```