Losses are mostly close; one game was lost by repetition (we made the repeating move while +16.5). Let me look at final boards of some losses and the repetition game.

```python
import json, numpy as np
g = json.load(open('/work/pass_3/games.json'))
boards = np.load('/work/pass_3/boards.npy'); valid = np.load('/work/pass_3/valid.npy')
def show(b):
    ch = {1:'X', -1:'O', 0:'.'}
    for r in range(9): print(' ' + ''.join(ch[int(b[r*9+c])] for c in range(9)))
for i in [0, 13, 21, 44]:
    gm = g[i]; n = int(valid[i].sum())
    print('game', i, gm['net_color'], 'margin', gm['margin'], 'end', gm['end'], 'plies', n)
    show(boards[i][n-1])
    tail = gm['moves'][-12:]
    print([(m['by'][0], m['move'], (m.get('top5') or [[None,None]])[0]) for m in tail])
```