Tokens and the table are correct, so something in the computed pass features differs in real games. Let me replay those exact pass moments in a positions pass (move-list format) with activations.

```python
import sys, json
sys.path.insert(0,'/work/tools')
from ana import *
g, B, V = load(6)
pos = []
for gi in [2, 3, 5, 12, 14, 16]:
    mv = g[gi]['moves']; n = len(mv)
    seq = [m['move'] if m['move'] != 81 else 'pass' for m in mv[:n-2]]
    pos.append({'moves': seq})
print(json.dumps({'positions': pos, 'activations': True, 'rasp': False}))
```