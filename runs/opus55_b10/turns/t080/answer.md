These 2nd-line moves are tactical (captures/ataris with high probability), so the opening is fine now. Let me examine Black's narrow losses at the end of the game: final board, who passed when, and whether neutral points or unresolved stones remained.

```python
import json, numpy as np
g = json.load(open('/work/pass_5/games.json'))
boards = np.load('/work/pass_5/boards.npy'); valid = np.load('/work/pass_5/valid.npy')
def rows(b):
    ch = {1:'X', -1:'O', 0:'.'}
    return [''.join(ch[int(b[r*9+c])] for c in range(9)) for r in range(9)]
close = [(i, x['margin']) for i, x in enumerate(g) if x['opponent']=='strong' and x['net_color']=='black' and -3 < x['margin'] < 0]
print(close)
for i, mg in close[:4]:
    x = g[i]; n = int(valid[i].sum())
    passes = [(m['ply'], m['by'][0]) for m in x['moves'] if m['move'] == 81]
    print('game', i, 'margin', mg, 'plies', n, 'passes', passes)
    a = rows(boards[i][n-21]); b = rows(boards[i][n-1])
    for r in range(9): print('   ', a[r], '  ', b[r])
    print('   last moves', [(m['by'][0], m['move'], m.get('top5', [[None]])[0][0] if m['by']=='net' else '') for m in x['moves'][-20:]])
```