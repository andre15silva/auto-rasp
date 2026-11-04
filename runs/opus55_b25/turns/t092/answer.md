```python
import json
G = json.load(open('/work/pass_15/games.json'))
g = G[17]
for m in g['moves'][-14:]:
    print(m['ply'], m['by'], m['move'], divmod(m['move'],9) if m['move']<81 else 'P', m.get('top5'))
```