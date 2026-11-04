```python
import shutil, json, numpy as np
from collections import Counter
shutil.copy('/work/program.py', '/work/program_best_p15.py')
G = json.load(open('/work/pass_15/games.json'))
print(Counter((g['end'], g['result'], g['net_color']) for g in G))
print('loss margins', sorted(round(g['margin'],1) for g in G if g['result']==-1))
nb = [g for g in G if g['margin'] < 60]
print('blow', 128-len(nb), 'nb wins', sum(g['result']==1 for g in nb), '/', len(nb))
L = [g for g in G if g['result']==-1]
print('losses lost/capt', np.mean([g['lost'] for g in L]).round(1), np.mean([g['captured'] for g in L]).round(1), 'len', np.mean([len(g['moves']) for g in L]).round(1))
```