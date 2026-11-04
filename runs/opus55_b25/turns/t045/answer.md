```python
import json, numpy as np
G = json.load(open('/work/pass_6/games.json'))
B = np.load('/work/pass_6/boards.npy')
def show_boards(arrs):
    ch = {1:'X',-1:'O',0:'.'}
    return '\n'.join('   '.join(' '.join(ch[int(v)] for v in a[r*9:(r+1)*9]) for a in arrs) for r in range(9))
gi = [i for i,g in enumerate(G) if g['opponent']=='strong' and g['result']==-1 and g['net_color']=='black']
for i in gi[:4]:
    g = G[i]; last = max(m['ply'] for m in g['moves'])
    print('game', i, 'margin', g['margin'], 'len', last, 'moves', [m['move'] for m in g['moves'][:16]])
    print(show_boards([B[i,9], B[i,19], B[i,35], B[i,last]]))
```