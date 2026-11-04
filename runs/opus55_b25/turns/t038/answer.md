```python
import json, numpy as np
G = json.load(open('/work/pass_4/games.json'))
B = np.load('/work/pass_4/boards.npy')
def show_boards(arrs):
    ch = {1:'X',-1:'O',0:'.'}
    return '\n'.join('   '.join(' '.join(ch[int(v)] for v in a[r*9:(r+1)*9]) for a in arrs) for r in range(9))
gi = [i for i,g in enumerate(G) if g['end']=='repetition']
for i in gi[:5]:
    g = G[i]; mv = g['moves']; last = mv[-1]['ply']
    fin = B[i,last]; same = [p for p in range(last) if (B[i,p]==fin).all()]
    print('game', i, 'net', g['net_color'], 'len', last, 'same as', same, 'last moves', [(m['ply'], m['by'][0], m['move']) for m in mv[-(last-same[0]+1):]])
    print(show_boards([B[i,p] for p in range(same[0], last+1)]))
```