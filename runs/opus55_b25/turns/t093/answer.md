```python
import json, numpy as np
G = json.load(open('/work/pass_15/games.json'))
B = np.load('/work/pass_15/boards.npy')
def show_boards(arrs):
    ch = {1:'X',-1:'O',0:'.'}
    return '\n'.join('   '.join(' '.join(ch[int(v)] for v in a[r*9:(r+1)*9]) for a in arrs) for r in range(9))
print(show_boards([B[17,p] for p in [83,85,87,89,91]]))
```