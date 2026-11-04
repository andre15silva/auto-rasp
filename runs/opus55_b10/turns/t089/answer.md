We lost 2 games by superko (while well ahead) in multi-ko capture cycles; we can't see history, but we can make ko-shaped captures (our capturing stone left with a single liberty, no friendly/empty neighbors) much less attractive. Let me look at the loss profile in this pass before deciding further changes.

```python
import json, numpy as np
g = json.load(open('/work/pass_7/games.json'))
st = [x for x in g if x['opponent']=='strong']
for res in [1, -1]:
    sel = [x for x in st if x['result']==res]
    print(res, len(sel), 'cap', np.mean([x['captured'] for x in sel]).round(1), 'lost', np.mean([x['lost'] for x in sel]).round(1),
          'margin', np.mean([x['margin'] for x in sel]).round(1))
loss_m = sorted([(x['margin'], x['net_color'], x['lost'], x['end']) for x in st if x['result'] < 0])
print(loss_m)
# how much do we lose by in close games, and big-loss games
print('close (>-5):', sum(1 for m in loss_m if m[0] > -5), ' big (<-15):', sum(1 for m in loss_m if m[0] < -15))
```