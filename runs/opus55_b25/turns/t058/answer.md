```python
import json, numpy as np
G = json.load(open('/work/pass_8/games.json'))
B = np.load('/work/pass_8/boards.npy')
def show_boards(arrs):
    ch = {1:'X',-1:'O',0:'.'}
    return '\n'.join('   '.join(' '.join(ch[int(v)] for v in a[r*9:(r+1)*9]) for a in arrs) for r in range(9))
found = 0
for i, g in enumerate(G):
    if g['result'] != -1 or g['margin'] > 60: continue
    netc = 1 if g['net_color']=='black' else -1
    last = g['moves'][-1]['ply']
    for p in range(1, last+1):
        lost = int(((B[i,p-1]==netc) & (B[i,p]==0)).sum())
        if lost >= 5:
            print('game', i, 'net', g['net_color'], 'ply', p, 'lost', lost)
            mv = {m['ply']: m for m in g['moves']}
            print(' moves', [(q, mv[q]['by'][0], divmod(mv[q]['move'],9) if mv[q]['move']<81 else 'pass') for q in range(p-11, p+1)])
            print(show_boards([B[i,p-12], B[i,p-8], B[i,p-4], B[i,p-1], B[i,p]]))
            found += 1
            break
    if found >= 3: break
```