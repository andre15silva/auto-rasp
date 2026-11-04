92M params. The region feature can make us pass prematurely if it's buggy, so let me verify it (and the cut/phase features and liberty accuracy after the run changes) with a positions pass on realistic positions taken from pass-5 games at various stages.

```python
import json, numpy as np, random
g = json.load(open('/work/pass_5/games.json'))
boards = np.load('/work/pass_5/boards.npy'); valid = np.load('/work/pass_5/valid.npy')
rng = random.Random(3)
def rows(b):
    ch = {1:'X', -1:'O', 0:'.'}
    return [''.join(ch[int(b[r*9+c])] for c in range(9)) for r in range(9)]
positions = []; meta = []
idxs = list(range(len(g))); rng.shuffle(idxs)
for k, i in enumerate(idxs[:50]):
    n = int(valid[i].sum())
    for ply in (rng.randrange(10, 40), rng.randrange(60, max(61, n-2))):
        if ply >= n: continue
        b = boards[i][ply]
        to_move = 'white' if ply % 2 == 0 else 'black'   # board after ply `ply`; ply 0 was black's move
        positions.append({"board": rows(b), "to_move": to_move}); meta.append((i, ply))
positions = positions[:100]
json.dump({'positions': positions, 'meta': meta[:100]}, open('/work/pass6_positions.json','w'))
print(len(positions))
print(json.dumps({"positions": positions, "activations": True, "rasp": False}, separators=(',',':')))
```