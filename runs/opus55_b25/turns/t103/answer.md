```python
import json, numpy as np
G = json.load(open('/work/pass_17/games.json'))
B = np.load('/work/pass_17/boards.npy')
def show_boards(arrs, marks=None):
    ch = {1:'X',-1:'O',0:'.'}
    out=[]
    for r in range(9):
        row=[]
        for a,mk in zip(arrs, marks):
            s=[]
            for c in range(9):
                v=ch[int(a[r*9+c])]
                if mk is not None and r*9+c==mk: v = v.lower() if v!='.' else '*'
                s.append(v)
            row.append(' '.join(s))
        out.append('   '.join(row))
    return '\n'.join(out)
for i, plies in [(8, [56, 58, 60, 62, 64, 66]), (52, [48, 50, 52, 54, 56, 58])]:
    g = G[i]; mv = {m['ply']: m for m in g['moves']}
    print('game', i, g['net_color'], [(p+1, mv[p+1]['by'][0], divmod(mv[p+1]['move'],9) if mv[p+1]['move']<81 else 'P', mv[p+1].get('top5', [[None,None]])[:3]) for p in plies])
    print(show_boards([B[i,p] for p in plies], [mv[p]['move'] for p in plies]))
```