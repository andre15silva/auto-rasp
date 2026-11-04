
import json, numpy as np
def load(k):
    g = json.load(open(f'/work/pass_{k}/games.json'))
    B = np.load(f'/work/pass_{k}/boards.npy'); V = np.load(f'/work/pass_{k}/valid.npy')
    return g, B, V
def show2(b, mark=None):
    rows=[]
    for r in range(9):
        s=''
        for c in range(9):
            i=r*9+c
            ch={0:'.',1:'X',-1:'O'}[int(b[i])]
            if mark is not None and i==mark: ch=ch.lower() if ch!='.' else '*'
            s+=ch
        rows.append(s)
    return rows
def side_by_side(boards, titles=None, marks=None):
    out=[]
    R=[show2(b, marks[i] if marks else None) for i,b in enumerate(boards)]
    if titles: out.append('   '.join(t.ljust(9) for t in titles))
    for r in range(9):
        out.append('   '.join(R[i][r] for i in range(len(R))))
    return '\n'.join(out)
