Several real save opportunities were missed — e.g., capturing an adjacent attacker or extending to 4–7 liberties wasn't even in our top 3. Let me examine one such position (game 56, before ply 80) in detail with exact Go rules: the threatened group, its liberty, the opponent groups' liberties, and what our chosen move did.

```python
import json, numpy as np, sys
sys.path.insert(0,'/work')
import goref
g = json.load(open('/work/pass_7/games.json'))
boards = np.load('/work/pass_7/boards.npy')
def rows(b, marks={}):
    ch = {1:'X', 2:'O', 0:'.'}
    return [''.join(marks.get(r*9+c, ch[b[r*9+c]]) for c in range(9)) for r in range(9)]
for (gi, p) in [(56, 80), (49, 80), (87, 98)]:
    x = g[gi]; me = 1 if x['net_color']=='black' else -1
    b = [0 if v == 0 else (1 if v == me else 2) for v in boards[gi][p-2]]
    mv = x['moves'][p-1]
    print('game', gi, 'ply', p-1, 'we played', mv['move'], 'top5', mv['top5'], '(X = us)')
    for r in rows(b, {mv['move']: '*'}): print('   ', r)
    # list our groups in atari and opponent groups in atari
    seen = set()
    for i in range(81):
        if b[i] and i not in seen:
            gg, ll = goref.group(b, i); seen |= gg
            if len(ll) <= 2: print('    group', 'X' if b[i]==1 else 'O', 'size', len(gg), 'libs', sorted(ll))
```