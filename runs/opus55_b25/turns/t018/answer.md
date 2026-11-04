```python
import numpy as np, math
def K(q,k,s=1.5):
    r1,c1=divmod(q,9); r2,c2=divmod(k,9); d2=(r1-r2)**2+(c1-c2)**2
    return math.exp(-d2/(2*s*s))
for s in [1.2,1.5]:
    W=[sum(K(q,k,s) for k in range(81)) for q in range(81)]
    S=max(W)+0.01
    print('sigma',s,'S',S,'min W',min(W))
    def infl(board):
        b=[ch for row in board for ch in row]
        m=np.zeros((81,2))
        for q in range(81):
            for k in range(81):
                if b[k]=='X': m[q,0]+=K(q,k,s)/S
                if b[k]=='O': m[q,1]+=K(q,k,s)/S
        return m
    board=["........." ,
           "........." ,
           "..X...O.." ,
           "..X...O.." ,
           "..X...O.." ,
           "..X...O.." ,
           "..XX..O.." ,
           ".........",
           "........."]
    m=infl(board)
    for r in [0,4,7]:
        print(r,' '.join(f"{m[r*9+c,0]-2*m[r*9+c,1]:+.2f}/{m[r*9+c,1]-2*m[r*9+c,0]:+.2f}" for c in range(9)))
```