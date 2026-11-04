The dominant early 2nd-line moves are contested contact plays (hane/attach under the opponent), which the table scores above 3rd-line development. Let me look at a few lost games mid-game to see what else goes wrong before revising the table.

```python
import json, numpy as np
g = json.load(open('/work/pass_4/games.json'))
boards = np.load('/work/pass_4/boards.npy'); valid = np.load('/work/pass_4/valid.npy')
def rows(b):
    ch = {1:'X', -1:'O', 0:'.'}
    return [''.join(ch[int(b[r*9+c])] for c in range(9)) for r in range(9)]
for i in [5, 8, 12, 60]:
    gm = g[i]; n = int(valid[i].sum())
    rs = [rows(boards[i][p]) for p in (15, 31, 51, n-1)]
    print('game', i, 'net', gm['net_color'], 'margin', gm['margin'], 'lost', gm['lost'], 'cap', gm['captured'])
    for r in range(9): print('   ', '   '.join(rs[k][r] for k in range(4)))
```