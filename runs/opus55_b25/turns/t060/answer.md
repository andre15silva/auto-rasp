```python
import json, numpy as np
G = json.load(open('/work/pass_8/games.json'))
B = np.load('/work/pass_8/boards.npy')
def board_str(arr):
    ch = {1:'X',-1:'O',0:'.'}
    return [''.join(ch[int(v)] for v in arr[r*9:(r+1)*9]) for r in range(9)]
pos = []
rng = np.random.default_rng(0)
for gi_ in rng.choice(len(G), 8, replace=False):
    g = G[gi_]; last = g['moves'][-1]['ply']
    ply = int(rng.integers(30, min(80, last)))
    to_move = 'black' if (ply + 1) % 2 == 0 else 'white'
    pos.append({"board": board_str(B[gi_, ply]), "to_move": to_move})
json.dump(pos, open('/work/test_positions2.json','w'))
print(json.dumps({"positions": pos, "activations": True, "rasp": False}))
```