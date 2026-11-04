
import numpy as np, random
N=9
NB=[[] for _ in range(81)]
for i in range(81):
    r,c=divmod(i,9)
    for dr,dc in((-1,0),(1,0),(0,-1),(0,1)):
        rr,cc=r+dr,c+dc
        if 0<=rr<9 and 0<=cc<9: NB[i].append(rr*9+cc)
def group(board,i):
    col=board[i]; st=[i]; seen={i}; libs=set()
    while st:
        j=st.pop()
        for k in NB[j]:
            if board[k]==0: libs.add(k)
            elif board[k]==col and k not in seen: seen.add(k); st.append(k)
    return seen,libs
def play(board,i,col,ko=None):
    """returns new board, captured count, new ko point, or None if illegal"""
    if board[i]!=0 or i==ko: return None
    b=board.copy(); b[i]=col; cap=[]
    for k in NB[i]:
        if b[k]==-col:
            g,l=group(b,k)
            if not l: cap+=list(g)
    for k in set(cap): b[k]=0
    g,l=group(b,i)
    if not l: return None
    nko=None
    if len(set(cap))==1 and len(g)==1 and len(l)==1: nko=cap[0]
    return b,len(set(cap)),nko
def is_eye(board,i,col):
    if board[i]!=0: return False
    return all(board[k]==col for k in NB[i])
def random_game(nmoves, seed=None):
    rng=random.Random(seed)
    b=np.zeros(81,int); col=1; ko=None
    for m in range(nmoves):
        cands=[i for i in range(81) if b[i]==0 and not is_eye(b,i,col)]
        rng.shuffle(cands)
        done=False
        for i in cands:
            r=play(b,i,col,ko)
            if r is not None:
                b,_,ko=r; done=True; break
        if not done: ko=None
        col=-col
    return b,col
