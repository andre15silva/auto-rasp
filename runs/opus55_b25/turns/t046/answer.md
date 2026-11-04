```python
import json, numpy as np
G = json.load(open('/work/pass_6/games.json'))
B = np.load('/work/pass_6/boards.npy')
def show_boards(arrs, marks=None):
    ch = {1:'X',-1:'O',0:'.'}
    out=[]
    for r in range(9):
        row=[]
        for a,mk in zip(arrs, marks or [None]*len(arrs)):
            s=[]
            for c in range(9):
                v=ch[int(a[r*9+c])]
                if mk is not None and r*9+c==mk: v=v.lower() if v!='.' else '*'
                s.append(v)
            row.append(' '.join(s))
        out.append('   '.join(row))
    return '\n'.join(out)
i = 2; g = G[i]
mv = {m['ply']: m for m in g['moves']}
plies = list(range(0, 36))
for start in range(0, 36, 6):
    ps = plies[start:start+6]
    print('plies', ps, ['net' if mv[p]['by']=='net' else 'opp' for p in ps])
    print(show_boards([B[i,p] for p in ps], [mv[p]['move'] for p in ps]))
    print('top5:', [ (p, [t[0] for t in mv[p]['top5'][:3]], [t[1] for t in mv[p]['top5'][:3]]) for p in ps if mv[p]['by']=='net'])
```