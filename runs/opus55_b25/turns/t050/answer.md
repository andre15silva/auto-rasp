```python
import json, numpy as np
G = json.load(open('/work/pass_7/games.json'))
B = np.load('/work/pass_7/boards.npy')
def show_boards(arrs):
    ch = {1:'X',-1:'O',0:'.'}
    return '\n'.join('   '.join(' '.join(ch[int(v)] for v in a[r*9:(r+1)*9]) for a in arrs) for r in range(9))
gi = [i for i,g in enumerate(G) if g['net_color']=='black' and -13 < g['margin'] < -5]
for i in gi[:3]:
    g = G[i]; last = max(m['ply'] for m in g['moves'])
    print('game', i, 'margin', g['margin'], 'len', last)
    print(show_boards([B[i,10], B[i,20], B[i,30], B[i,45], B[i,last]]))
```