```python
import json, numpy as np
G = json.load(open('/work/pass_3/games.json'))
B = np.load('/work/pass_3/boards.npy')
def show_board(arr, net_color):
    ch = {1:'X',-1:'O',0:'.'}
    return '\n'.join(' '.join(ch[int(v)] for v in arr[r*9:(r+1)*9]) for r in range(9))
gi = [i for i,g in enumerate(G) if g['opponent']=='strong' and g['result']==-1 and g['end']=='two_passes']
for i in gi[:3]:
    g = G[i]
    fp = next(m for m in g['moves'] if m['move']==81)
    ply = fp['ply']
    print('game', i, 'net', g['net_color'], 'margin', g['margin'], 'first pass ply', ply, 'by', fp['by'], 'top5', fp.get('top5'))
    print(show_board(B[i, ply-1], g['net_color']))
    last = max(m['ply'] for m in g['moves'])
    print('final ply', last); print(show_board(B[i, last], g['net_color']))
```