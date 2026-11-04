```python
import json, numpy as np
from collections import Counter
for pss in [14, 15, 16]:
    G = json.load(open(f'/work/pass_{pss}/games.json'))
    print(pss, Counter((g['end'], g['result']) for g in G), 'close losses', sum(1 for g in G if g['result']==-1 and g['margin']>-5))
```