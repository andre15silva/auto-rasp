```python
import json, numpy as np
from collections import Counter
for pss in [7, 8]:
    G = json.load(open(f'/work/pass_{pss}/games.json'))
    blow = sum(1 for g in G if g['margin'] > 60)
    nb = [g for g in G if g['margin'] < 60]
    print('pass', pss, 'blowouts', blow, 'nonblow wins', sum(g['result']==1 for g in nb), '/', len(nb),
          'B', sum(g['result']==1 for g in nb if g['net_color']=='black'), '/', sum(1 for g in nb if g['net_color']=='black'),
          'mean nb margin', np.mean([g['margin'] for g in nb]))
    # opponent passes followed by our non-pass moves
    cnt = Counter()
    for g in G:
        mv = g['moves']
        for a, b in zip(mv, mv[1:]):
            if a['by'] != 'net' and a['move'] == 81:
                cnt['opp_pass'] += 1
                cnt['net_reply_pass' if b['move']==81 else 'net_reply_move'] += 1
    print(cnt)
```