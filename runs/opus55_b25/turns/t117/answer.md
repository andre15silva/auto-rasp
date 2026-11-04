```python
import json, numpy as np
from collections import Counter
G = json.load(open('/work/pass_19/games.json'))
G = [g for g in G if g['opponent']=='strong' and g['net_color']=='black']
first = Counter(divmod(g['moves'][0]['move'],9) for g in G)
print(first.most_common(8))
print(G[0]['moves'][0]['top5'])
res_by_first = {}
for g in G:
    f = divmod(g['moves'][0]['move'],9)
    res_by_first.setdefault(f, []).append(g['result'])
print({k: (len(v), sum(1 for x in v if x==1)) for k,v in res_by_first.items()})
# opponent's first reply
rep = Counter(divmod(g['moves'][1]['move'],9) for g in G)
print(rep.most_common(8))
```