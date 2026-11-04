```python
import json, numpy as np
G = json.load(open('/work/pass_15/games.json'))
B = np.load('/work/pass_15/boards.npy')
def show_boards(arrs):
    ch = {1:'X',-1:'O',0:'.'}
    return '\n'.join('   '.join(' '.join(ch[int(v)] for v in a[r*9:(r+1)*9]) for a in arrs) for r in range(9))
close = [i for i,g in enumerate(G) if g['result']==-1 and g['margin'] > -5]
for i in close[:4]:
    g = G[i]; last = g['moves'][-1]['ply']
    print('game', i, g['net_color'], g['margin'], 'len', last, 'last moves', [(m['ply'], m['by'][0], m['move']) for m in g['moves'][-6:]])
    print(show_boards([B[i,last-20], B[i,last-10], B[i,last]]))
```