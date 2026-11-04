Two of the remaining misses are striking: we passed (p≈0.99) while a capture saving 9 stones existed. That suggests the opponent group in atari was misclassified (liberty overcount or coverage). Let me look at these positions.

```python
import json, numpy as np, sys
sys.path.insert(0,'/work')
import goref
g = json.load(open('/work/pass_8/games.json'))
boards = np.load('/work/pass_8/boards.npy')
def rows(b, marks={}):
    ch = {1:'X', 2:'O', 0:'.'}
    return [''.join(marks.get(r*9+c, ch[b[r*9+c]]) for c in range(9)) for r in range(9)]
for (gi, p, cap) in [(11, 87, 72), (83, 96, 1), (60, 90, 52)]:
    x = g[gi]; me = 1 if x['net_color']=='black' else -1
    b = [0 if v == 0 else (1 if v == me else 2) for v in boards[gi][p-2]]
    print('game', gi, 'our move ply', p-1, 'capture at', cap, 'X = us')
    for r in rows(b, {cap: '*'}): print('   ', r)
    k = [n for n in goref.NBR[cap] if b[n] == 2][0]
    og, ol = goref.group(b, k)
    print('   O group size', len(og), 'libs', sorted(ol), 'rows', sorted({s//9 for s in og}), 'cols', sorted({s%9 for s in og}))
    # liberties of all groups near
    print('   prev opponent move', x['moves'][p-2]['move'])
```