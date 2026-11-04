```python
import json, numpy as np, shutil
shutil.copy('/work/program.py', '/work/program_final_candidate.py')
G = json.load(open('/work/pass_19/games.json'))
B = np.load('/work/pass_19/boards.npy')
def nb(i):
    r,c=divmod(i,9); return [(r+dr)*9+c+dc for dr,dc in ((-1,0),(1,0),(0,-1),(0,1)) if 0<=r+dr<9 and 0<=c+dc<9]
def chain(board, s):
    col=board[s]; seen={s}; st=[s]
    while st:
        u=st.pop()
        for v in nb(u):
            if board[v]==col and v not in seen: seen.add(v); st.append(v)
    return seen, {v for u in seen for v in nb(u) if board[v]==0}
for i, g in enumerate(G):
    if g['end'] != 'repetition': continue
    mv = g['moves']; last = mv[-1]['ply']; fin = B[i,last]
    s0 = [p for p in range(last) if (B[i,p]==fin).all()][0]
    out = []
    for m in mv[s0+1:]:
        p = m['ply']; v = m['move']
        if v >= 81: out.append((m['by'][0], 'P')); continue
        capt = int(((B[i,p-1]!=0)&(B[i,p]==0)).sum()); ch, libs = chain(B[i,p], v)
        out.append((m['by'][0], divmod(v,9), 'cap', capt, 'libs', len(libs), round((m.get('top5') or [[0,0]])[0][1],2)))
    print(i, g['opponent'], g['result'], g['margin'], out)
```