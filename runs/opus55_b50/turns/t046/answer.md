Timing measurements in the sandbox are wildly noisy (a sub-model measured slower than the full model). The pass tools report timing on the evaluation machine, so I'll rely on those. First, a positions pass to verify correctness of the compiled features (and check for NaNs). Let me pick realistic positions from pass-1 games.

```python
import sys, json, numpy as np
sys.path.insert(0,'/work/tools')
from ana import *
g, B, V = load(1)
rng = np.random.default_rng(0)
sel = []
for gi in range(0, 128, 3):
    n = int(V[gi].sum())
    if n < 20: continue
    p = int(rng.integers(15, n - 2))
    sel.append((gi, p))
sel = sel[:40]
positions = []
for gi, p in sel:
    b = B[gi, p]
    rows = [''.join({0:'.',1:'X',-1:'O'}[int(v)] for v in b[r*9:(r+1)*9]) for r in range(9)]
    to_move = 'white' if p % 2 == 0 else 'black'   # board after ply p (ply 0 = black's move)
    positions.append({"board": rows, "to_move": to_move})
json.dump({"sel": sel, "positions": positions}, open('/work/tools/posset1.json', 'w'))
print(json.dumps({"positions": positions, "activations": True, "rasp": False}))
```