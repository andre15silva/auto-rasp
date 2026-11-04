
import numpy as np, collections, sys
sys.path.insert(0, '/work'); sys.path.insert(0, '/work/tools')
from gorules import NB, group
import gonet
def board_rel(pos):
    b = np.zeros(81, int)
    for r, row in enumerate(pos['board']):
        for c, ch in enumerate(row):
            b[r*9+c] = {'.':0,'X':1,'O':-1}[ch]
    me = 1 if pos['to_move'] == 'black' else -1
    return b * me
def runs(board):
    h=[None]*81; v=[None]*81
    for r in range(9):
        for c in range(9):
            i=r*9+c
            h[i]= h[i-1] if c>0 and board[i-1]==board[i] else i
            v[i]= v[i-9] if r>0 and board[i-9]==board[i] else i
    return h,v
def bundle_sim(rel, N):
    X = np.zeros((81, 10))
    for i in range(81):
        nb = NB[i]
        for k in nb:
            vv = gonet.bucket(k) if rel[k] == 0 else (8 if rel[k] == 1 else 9)
            X[i, vv] += 1.0 / len(nb)
    h, v = runs(rel)
    for s in range(N):
        ids = h if s % 2 == 0 else v
        groups = collections.defaultdict(list)
        for i in range(81): groups[ids[i]].append(i)
        Y = np.zeros_like(X)
        for gid, mem in groups.items(): Y[mem] = X[mem].mean(0)
        X = Y
    return X
def ideal(rel):
    """per point: (bucket count over full group libs) for stones; region (tx,to) for empty"""
    cnt = np.zeros(81, int); reg = [None]*81
    for i in range(81):
        if rel[i] != 0:
            g, L = group(rel, i); cnt[i] = len({gonet.bucket(x) for x in L})
        else:
            st=[i]; seen={i}; tx=to=False
            while st:
                j=st.pop()
                for k in NB[j]:
                    if rel[k]==0 and k not in seen: seen.add(k); st.append(k)
                    elif rel[k]==1: tx=True
                    elif rel[k]==-1: to=True
            reg[i] = 'own' if tx and not to else 'opp' if to and not tx else 'both' if tx else 'none'
    return cnt, reg
