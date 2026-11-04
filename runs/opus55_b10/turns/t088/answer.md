67.7% vs strong (Black now 66.7%, White 68.8%). But there were 4 repetition endings and 4 games with an early pass. Let me inspect those.

```python
import json, numpy as np
g = json.load(open('/work/pass_7/games.json'))
boards = np.load('/work/pass_7/boards.npy'); valid = np.load('/work/pass_7/valid.npy')
def rows(b):
    ch = {1:'X', -1:'O', 0:'.'}
    return [''.join(ch[int(b[r*9+c])] for c in range(9)) for r in range(9)]
for i, x in enumerate(g):
    if x['end'] == 'repetition':
        n = int(valid[i].sum())
        last = x['moves'][-1]
        print('REP game', i, x['opponent'], 'net', x['net_color'], 'result', x['result'], 'margin', x['margin'], 'last by', last['by'], last['move'], 'top5', last.get('top5'))
        print('   tail', [(m['by'][0], m['move']) for m in x['moves'][-10:]])
for i, x in enumerate(g):
    early = [m for m in x['moves'] if m['by']=='net' and m['move']==81 and m['ply'] < 60]
    if early:
        m = early[0]
        print('EARLY PASS game', i, x['opponent'], 'net', x['net_color'], 'result', x['result'], 'ply', m['ply'], 'top5', m['top5'])
        b = boards[i][m['ply']-1]
        for r in rows(b): print('    ', r)
        break
```