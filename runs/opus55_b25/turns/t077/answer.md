```python
import json, numpy as np
G = json.load(open('/work/pass_12/games.json'))
B = np.load('/work/pass_12/boards.npy')
def show_boards(arrs):
    ch = {1:'X',-1:'O',0:'.'}
    return '\n'.join('   '.join(' '.join(ch[int(v)] for v in a[r*9:(r+1)*9]) for a in arrs) for r in range(9))
gi = [i for i,g in enumerate(G) if g['end']=='repetition']
for i in gi:
    g = G[i]; mv = g['moves']; last = mv[-1]['ply']
    fin = B[i,last]; same = [p for p in range(last) if (B[i,p]==fin).all()]
    seq = [(m['ply'], m['by'][0], divmod(m['move'],9) if m['move']<81 else 'P', (m.get('top5') or [[0,0]])[0][1]) for m in mv[same[0]+1:]]
    print('game', i, 'net', g['net_color'], 'res', g['result'], 'margin', g['margin'], 'len', last, 'same', same, seq)
i = gi[0]; g=G[i]; last=g['moves'][-1]['ply']; fin=B[i,last]; s0=[p for p in range(last) if (B[i,p]==fin).all()][0]
print(show_boards([B[i,p] for p in range(s0, last+1)]))
```