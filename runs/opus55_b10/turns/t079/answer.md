Black's losses are now mostly very close (9 of them by ≤2.5 points), so endgame efficiency matters. Let me inspect some early 2nd-line moves we chose with high probability to judge whether they are tactically justified or slack.

```python
import json, numpy as np, sys
sys.path.insert(0,'/work')
import go
g = json.load(open('/work/pass_5/games.json'))
boards = np.load('/work/pass_5/boards.npy')
def rows(b, mark=None):
    ch = {1:'X', -1:'O', 0:'.'}
    out = []
    for r in range(9):
        out.append(''.join(('*' if mark == r*9+c else ch[int(b[r*9+c])]) for c in range(9)))
    return out
shown = 0
for i, x in enumerate(g):
    if x['opponent'] != 'strong': continue
    for m in x['moves']:
        if m['by']=='net' and 8 <= m['ply'] < 30 and m['move'] < 81 and go.line_of(m['move']) == 1:
            p = dict((a,b) for a,b in m['top5']).get(m['move'], 0.0)
            if p > 0.4 and shown < 6:
                prev = boards[i][m['ply']-1]
                print('game', i, 'net', x['net_color'], 'ply', m['ply'], 'move', m['move'], 'top5', m['top5'])
                for r in rows(prev, m['move']): print('   ', r)
                shown += 1
```