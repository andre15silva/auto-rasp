
from tracr.rasp import rasp
MLP_EXACTNESS = 100
def program():
    t = rasp.tokens
    idx = rasp.indices
    def nb(k, q):
        if k >= 81 or q >= 81: return False
        kr, kc = divmod(k, 9); qr, qc = divmod(q, 9)
        return abs(kr-qr) + abs(kc-qc) <= 1
    sel = rasp.Select(idx, idx, nb)
    flags = [rasp.numerical(rasp.Map(lambda v, j=j: 1 if (v == '.' and j%2==0) else 0, t)) for j in range(14)]
    extra = [rasp.categorical(rasp.Map(lambda v, j=j: (v*7+j) % 82, idx)) for j in range(10)]
    for step in range(8):
        new = []
        for j, f in enumerate(flags):
            a = rasp.numerical(rasp.Aggregate(sel, f, default=0))
            b = rasp.numerical(rasp.Map(lambda x: 1 if x > 0.001 else 0, a))
            new.append(b)
        flags = new
    out = flags[0]
    for f in flags[1:] + [rasp.numerical(rasp.Map(lambda v: v/100, e)) for e in extra]:
        out = rasp.numerical(rasp.LinearSequenceMap(out, f, 1, 1))
    return out
