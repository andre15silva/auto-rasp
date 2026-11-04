```python
import json, numpy as np
G = json.load(open('/work/pass_12/games.json'))
B = np.load('/work/pass_12/boards.npy')
def show_boards(arrs):
    ch = {1:'X',-1:'O',0:'.'}
    return '\n'.join('   '.join(' '.join(ch[int(v)] for v in a[r*9:(r+1)*9]) for a in arrs) for r in range(9))
for i, s0, last in [(91, 78, 81), (66, 86, 89), (19, 77, 80)]:
    print('game', i, G[i]['net_color'])
    print(show_boards([B[i,p] for p in range(s0, last+1)]))
```