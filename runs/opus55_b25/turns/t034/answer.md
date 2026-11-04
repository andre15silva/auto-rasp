```python
import json, numpy as np
G = json.load(open('/work/pass_3/games.json'))
B = np.load('/work/pass_3/boards.npy')
def show_boards(arrs):
    ch = {1:'X',-1:'O',0:'.'}
    lines=[]
    for r in range(9):
        lines.append('   '.join(' '.join(ch[int(v)] for v in a[r*9:(r+1)*9]) for a in arrs))
    return '\n'.join(lines)
gi = [i for i,g in enumerate(G) if g['opponent']=='strong' and g['result']==-1]
for i in gi[5:8]:
    g = G[i]; last = max(m['ply'] for m in g['moves'])
    fp = next((m['ply'] for m in g['moves'] if m['move']==81), None)
    print('game', i, 'net', g['net_color'], 'margin', g['margin'], 'end', g['end'], 'len', last, 'first pass', fp)
    print(show_boards([B[i,15], B[i,30], B[i,45], B[i,last]]))
```