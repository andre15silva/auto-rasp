```python
import json, numpy as np
g = json.load(open('/work/pass_1/games.json'))
print(type(g), len(g)); print(g[0].keys())
B = np.load('/work/pass_1/boards.npy'); V = np.load('/work/pass_1/valid.npy')
def show(b):
    s=''
    for r in range(9):
        s+=''.join('.XO'[int(v)] if v>=0 else 'O' for v in b[r*9:(r+1)*9])+'\n'
    return s
def show2(b):
    return '\n'.join(''.join({0:'.',1:'X',-1:'O'}[int(v)] for v in b[r*9:(r+1)*9]) for r in range(9))
# who passes when
for gi in range(6):
    gm=g[gi]; mv=gm['moves']
    print(gi, gm['opponent'], gm['net_color'], gm['result'], gm['margin'], gm['end'], len(mv))
    ps=[(m['ply'],m['by']) for m in mv if m['move']==81]
    print('  passes:', ps)
print(json.dumps(g[0]['moves'][:6]))
```