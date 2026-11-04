```python
import numpy as np
pts=[(r,c) for r in range(9) for c in range(9)]
D=np.array([[abs(a[0]-b[0])+abs(a[1]-b[1]) for b in pts] for a in pts])
def sc(col):
    col=np.array(col); same=(col[:,None]==col[None,:]); np.fill_diagonal(same,False)
    d=np.where(same,D,99); m=d.min(); return int(m), int((d==m).sum()//2)
for m in [12,13]:
    res=[]
    for a in range(m):
        for b in range(1,m):
            res.append((sc([(a*r+b*c)%m for r,c in pts]),a,b))
    res.sort(key=lambda x:(-x[0][0],x[0][1]))
    print(m,res[:3])
import random
random.seed(1); best=None
for trial in range(15):
    col=[random.randrange(12) for _ in range(81)]; s=sc(col)
    for it in range(2500):
        i=random.randrange(81); old=col[i]; col[i]=random.randrange(12); s2=sc(col)
        if s2[0]>s[0] or (s2[0]==s[0] and s2[1]<=s[1]): s=s2
        else: col[i]=old
    if best is None or s[0]>best[0][0] or (s[0]==best[0][0] and s[1]<best[0][1]): best=(s,list(col))
print(best[0]); print(np.array(best[1]).reshape(9,9))
```