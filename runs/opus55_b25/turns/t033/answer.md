```python
import json, numpy as np
G = json.load(open('/work/pass_3/games.json'))
B = np.load('/work/pass_3/boards.npy')
def show_board(arr):
    ch = {1:'X',-1:'O',0:'.'}
    return '\n'.join(' '.join(ch[int(v)] for v in arr[r*9:(r+1)*9]) for r in range(9))
gi = [i for i,g in enumerate(G) if g['end']=='repetition']
for i in gi[:4]:
    g = G[i]; mv = g['moves']; last = mv[-1]['ply']
    print('game', i, g['opponent'], 'net', g['net_color'], 'result', g['result'], 'len', last)
    print(' last moves', [(m['ply'], m['by'][0], m['move']) for m in mv[-8:]])
    # find earlier identical board to final
    fin = B[i, last]
    same = [p for p in range(last) if (B[i,p]==fin).all()]
    print(' same as plies', same)
    print(show_board(B[i,last-1]))
```