
from tracr.rasp import rasp
def nb(i, d):
    if i >= 81: return 81
    r, c = divmod(i, 9)
    dr, dc = [(-1,0),(1,0),(0,-1),(0,1)][d]
    r2, c2 = r+dr, c+dc
    if 0 <= r2 < 9 and 0 <= c2 < 9: return r2*9+c2
    return 81
def program():
    t = rasp.tokens; idx = rasp.indices
    cur = t
    outs = []
    for layer in range(4):
        nxt = []
        for d in range(4):
            q = rasp.Map(lambda i, d=d: nb(i, d), idx)
            sel = rasp.Select(idx, q, rasp.Comparison.EQ)
            a = rasp.Aggregate(sel, cur)
            nxt.append(a)
        # combine
        m = rasp.SequenceMap(lambda a, b: a if a == b else ".", nxt[0], nxt[1])
        m2 = rasp.SequenceMap(lambda a, b: a if a == b else ".", nxt[2], nxt[3])
        cur = rasp.SequenceMap(lambda a, b: a if a == b else "x", m, m2)
    out = rasp.numerical(rasp.Map(lambda x: 1.0 if x == "x" else 0.0, cur))
    return out
