```python
import json, numpy as np
G = json.load(open('/work/pass_8/games.json'))
B = np.load('/work/pass_8/boards.npy')
def show_boards(arrs):
    ch = {1:'X',-1:'O',0:'.'}
    return '\n'.join('   '.join(' '.join(ch[int(v)] for v in a[r*9:(r+1)*9]) for a in arrs) for r in range(9))
blow = [i for i,g in enumerate(G) if g['margin'] > 60]
i = blow[0]; g = G[i]; mv = g['moves']; last = mv[-1]['ply']
fp = next(m['ply'] for m in mv if m['move']==81 and m['by']!='net')
print('net', g['net_color'], 'len', last, 'first opp pass', fp)
print([(m['ply'], m['by'][0], m['move']) for m in mv if m['ply'] >= fp-4][:40])
print(show_boards([B[i,fp-6], B[i,fp-2], B[i,fp], B[i,min(fp+10,last)], B[i,last]]))
```