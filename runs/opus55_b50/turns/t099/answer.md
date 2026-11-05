As Black, with d=1 we should not pass (need d ≥ 8), yet the pass probability was 0.998. All six cases are games where we were Black, which suggests the side-to-move token is being misinterpreted. Let me check the actual tokens at index 81 in the positions-pass inputs.

```python
import json
inp = json.load(open('/work/pass_5/inputs.json'))
for p in inp[:6]:
    print(p['to_move'], p['tokens'][81], p['tokens'][:5])
import sys; sys.path.insert(0,'/work'); import gonet4
print([gonet4.PASSTAB(tc, 0, 'B') for tc in range(7)], [gonet4.PASSTAB(tc, 0, 'W') for tc in range(7)])
```