```python
import json, numpy as np
from collections import Counter
G = json.load(open('/work/pass_14/games.json'))
B = np.load('/work/pass_14/boards.npy')
print(Counter((g['end'], g['result']) for g in G))
print('loss margins', sorted(round(g['margin'],1) for g in G if g['result']==-1))
def nb(i):
    r,c=divmod(i,9); return [(r+dr)*9+c+dc for dr,dc in ((-1,0),(1,0),(0,-1),(0,1)) if 0<=r+dr<9 and 0<=c+dc<9]
gi = [i for i,g in enumerate(G) if g['end']=='repetition' and g['result']==-1]
for i in gi:
    g = G[i]; mv = g['moves']; last = mv[-1]['ply']
    fin = B[i,last]; same = [p for p in range(last) if (B[i,p]==fin).all()]
    seq = [(m['ply'], m['by'][0], divmod(m['move'],9) if m['move']<81 else 'P', (m.get('top5') or [[0,0]])[0][1]) for m in mv[same[0]+1:]]
    print('game', i, g['net_color'], 'margin', g['margin'], 'len', last, 'cycle', len(seq), seq)
```