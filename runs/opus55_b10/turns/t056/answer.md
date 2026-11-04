Our play is scattered in the opening (flat logits, corner/edge moves sampled), while the strong net builds solid connected shapes. Let me quantify captures/losses in won vs lost games and check how often our moves were low-probability samples or first/second-line moves early on.

```python
import json, numpy as np
g = json.load(open('/work/pass_3/games.json'))
for opp in ['strong','weak']:
    for res in [1,-1]:
        sel = [x for x in g if x['opponent']==opp and x['result']==res]
        if not sel: continue
        print(opp, res, len(sel), 'captured', np.mean([x['captured'] for x in sel]).round(1), 'lost', np.mean([x['lost'] for x in sel]).round(1), 'margin', np.mean([x['margin'] for x in sel]).round(1))
def line(m):
    r, c = divmod(m, 9); return min(r, c, 8-r, 8-c)
early = {0:0,1:0,2:0,3:0,4:0}; lowp = 0; tot = 0; probs=[]
for x in g:
    for m in x['moves']:
        if m['by']=='net' and m['ply'] < 30 and m['move'] < 81:
            early[line(m['move'])] += 1
            p = dict((a,b) for a,b in m['top5']).get(m['move'], 0.0)
            probs.append(p); tot += 1
print('early (ply<30) net moves by line:', early)
probs = np.array(probs)
print('prob of chosen move (ply<30): quantiles', np.quantile(probs,[0.1,0.25,0.5,0.75]), 'frac chosen not in top5', (probs==0).mean())
```