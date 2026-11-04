```python
import json, numpy as np
from collections import Counter
G = json.load(open('/work/pass_7/games.json'))
gb = [g for g in G if g['net_color']=='black']
print(sorted(round(g['margin'],1) for g in gb))
gw = [g for g in G if g['net_color']=='white']
print(sorted(round(g['margin'],1) for g in gw))
print(Counter((g['end'],g['result'],g['net_color']) for g in G))
```