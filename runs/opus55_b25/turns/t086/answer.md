```python
import json, numpy as np
G = json.load(open('/work/pass_14/games.json'))
B = np.load('/work/pass_14/boards.npy')
def nb(i):
    r,c=divmod(i,9); return [(r+dr)*9+c+dc for dr,dc in ((-1,0),(1,0),(0,-1),(0,1)) if 0<=r+dr<9 and 0<=c+dc<9]
def chain(board, s):
    col=board[s]; seen={s}; st=[s]
    while st:
        u=st.pop()
        for v in nb(u):
            if board[v]==col and v not in seen: seen.add(v); st.append(v)
    libs={v for u in seen for v in nb(u) if board[v]==0}
    return seen, libs
gi = [i for i,g in enumerate(G) if g['end']=='repetition']
for i in gi:
    g = G[i]; mv = g['moves']; last = mv[-1]['ply']
    fin = B[i,last]; same = [p for p in range(last) if (B[i,p]==fin).all()][0]
    out=[]
    for m in mv[same+1:]:
        p = m['ply']; mvv = m['move']
        if mvv >= 81: out.append((m['by'][0], 'P')); continue
        before, after = B[i,p-1], B[i,p]
        capt = int(((before!=0)&(after==0)).sum())
        ch, libs = chain(after, mvv)
        out.append((m['by'][0], divmod(mvv,9), 'cap', capt, 'sz', len(ch), 'libs', len(libs)))
    print(i, g['result'], out)
```