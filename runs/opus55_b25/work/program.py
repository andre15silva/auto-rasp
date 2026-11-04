
from tracr.rasp import rasp

def nbr_sel(dr, dc):
    def pred(k, q):
        if q >= 81: return False
        r, c = divmod(q, 9)
        r2, c2 = r + dr, c + dc
        if not (0 <= r2 < 9 and 0 <= c2 < 9): return False
        return k == r2 * 9 + c2
    return rasp.Select(rasp.indices, rasp.indices, pred)

DIRS = [(-1,0),(1,0),(0,-1),(0,1)]
def program():
    x = rasp.numerical(rasp.Map(lambda t: 1.0 if t == '.' else 0.0, rasp.tokens))
    for it in range(12):
        nb = [rasp.numerical(rasp.Aggregate(nbr_sel(dr, dc), x, default=0)) for dr, dc in DIRS]
        s = rasp.numerical(rasp.LinearSequenceMap(nb[0], nb[1], 0.5, 0.5))
        s2 = rasp.numerical(rasp.LinearSequenceMap(nb[2], nb[3], 0.5, 0.5))
        x = rasp.numerical(rasp.LinearSequenceMap(s, s2, 0.5, 0.5))
    # a wide categorical
    c = rasp.categorical(rasp.Map(lambda v: int(v*1000) % 300, x))
    out = rasp.numerical(rasp.Map(lambda v: v/300, c))
    return out
