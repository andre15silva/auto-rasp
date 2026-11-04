The repetition loss was a ko-like recapture cycle (rare; our network can't see history). The other losses are territorial: the opponent ends with more area, and we sometimes pass while it keeps playing. Let me look at our openings and mid-game boards in a few lost vs. won games.

```python
import json, numpy as np
g = json.load(open('/work/pass_3/games.json'))
boards = np.load('/work/pass_3/boards.npy'); valid = np.load('/work/pass_3/valid.npy')
def show_rows(b):
    ch = {1:'X', -1:'O', 0:'.'}
    return [''.join(ch[int(b[r*9+c])] for c in range(9)) for r in range(9)]
for i in [0, 13, 35, 2]:
    gm = g[i]
    rows = [show_rows(boards[i][p]) for p in (9, 19, 39)]
    print('game', i, 'net', gm['net_color'], 'result', gm['result'], 'margin', gm['margin'])
    for r in range(9): print('   '.join(rows[k][r] for k in range(3)))
    print('net moves:', [m['move'] for m in gm['moves'][:30] if m['by']=='net'])
    print('opp moves:', [m['move'] for m in gm['moves'][:30] if m['by']=='opponent'])
```