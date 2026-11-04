Two failure modes vs random: an early/unlucky pass ending the game while behind (game 104), and a massive collapse (game 97, lost 112 stones). Let me find where big captures against us happened and what the network's choices were.

```python
import sys, json, numpy as np
sys.path.insert(0,'/work/tools')
from ana import *
g, B, V = load(4)
def net_sign(gm): return 1 if gm['net_color'] == 'black' else -1
gi = 97; gm = g[gi]; s = net_sign(gm); mv = gm['moves']
prev = np.zeros(81, int)
for p in range(int(V[gi].sum())):
    b = B[gi, p]
    lostn = int(((prev == s) & (b != s)).sum())
    if lostn >= 3:
        m = mv[p]
        print('ply', p, 'by', m['by'], 'move', m['move'], 'we lost', lostn)
        # show the board before opponent's capturing move and our previous move
        pm = mv[p-1]
        print(' our previous move', pm['move'], 'top5', pm.get('top5'))
        print(side_by_side([B[gi,p-2], B[gi,p-1], b], ['before', 'after ours', 'after capture'], [mv[p-2]['move'], pm['move'], m['move']]))
    prev = b
for p in [22, 64]:
    print(p, g[104]['moves'][p])
```