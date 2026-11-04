```python
import json
G = json.load(open('/work/pass_4/games.json'))
for gi_, ply in [(36,52),(41,72),(31,68),(40,70),(40,72),(40,74),(52,93),(52,97)]:
    g = G[gi_]
    m = next(m for m in g['moves'] if m['ply']==ply)
    print(gi_, ply, m['move'], divmod(m['move'],9), m.get('top5'))
```