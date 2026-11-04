Still ~33% of our early moves are on the 1st/2nd line. Let me classify early moves by the positional situation (open/own/opponent/contested and adjacency) at the time they were played, to see which table entries produce them.

```python
import json, numpy as np, sys
sys.path.insert(0,'/work')
import go
g = json.load(open('/work/pass_4/games.json'))
boards = np.load('/work/pass_4/boards.npy')
from collections import Counter
cnt = Counter(); cnt_all = Counter()
def situ(b, p, me):
    xs = [j for j in range(81) if 1 <= go.man(p, j) <= 2]
    fx = sum(1 for j in xs if b[j] == me)/len(xs); fo = sum(1 for j in xs if b[j] == -me)/len(xs)
    lev = lambda x: 0 if x < 0.05 else (1 if x < 0.25 else (2 if x < 0.7 else 3))
    ax = any(b[j] == me for j in go.NB[p]); ao = any(b[j] == -me for j in go.NB[p])
    return (lev(fx), lev(fo), int(ax), int(ao))
for i, x in enumerate(g):
    me = 1 if x['net_color']=='black' else -1
    for m in x['moves']:
        if m['by']=='net' and m['ply'] < 30 and m['move'] < 81:
            prev = boards[i][m['ply']-1] if m['ply'] > 0 else np.zeros(81)
            s = situ(prev, m['move'], me)
            ln = go.line_of(m['move'])
            cnt_all[ln] += 1
            if ln <= 1: cnt[(ln,) + s] += 1
print(cnt.most_common(15))
```