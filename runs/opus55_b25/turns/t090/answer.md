```python
import json, numpy as np
G = json.load(open('/work/pass_15/games.json'))
B = np.load('/work/pass_15/boards.npy')
def show_boards(arrs):
    ch = {1:'X',-1:'O',0:'.'}
    return '\n'.join('   '.join(' '.join(ch[int(v)] for v in a[r*9:(r+1)*9]) for a in arrs) for r in range(9))
found=0
for i, g in enumerate(G):
    if g['result'] != -1: continue
    netc = 1 if g['net_color']=='black' else -1
    last = g['moves'][-1]['ply']
    for p in range(1, last+1):
        lost = int(((B[i,p-1]==netc) & (B[i,p]==0)).sum())
        if lost >= 6:
            mv = {m['ply']: m for m in g['moves']}
            print('game', i, g['net_color'], 'ply', p, 'lost', lost, 'margin', g['margin'])
            print(' seq', [(q, mv[q]['by'][0], divmod(mv[q]['move'],9) if mv[q]['move']<81 else 'P', round(mv[q]['top5'][0][1],2) if mv[q]['by']=='net' else '') for q in range(p-9, p+1)])
            print(show_boards([B[i,p-10], B[i,p-6], B[i,p-3], B[i,p-1], B[i,p]]))
            found+=1; break
    if found>=3: break
```