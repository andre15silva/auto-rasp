
from tracr.rasp import rasp
MLP_EXACTNESS = 1000
NCAT = 0
VALSZ = 82
def program():
    t = rasp.tokens
    idx = rasp.indices
    def nb(k, q):
        if k >= 81 or q >= 81: return 0
        kr, kc = divmod(k, 9); qr, qc = divmod(q, 9)
        return 5.0 if abs(kr-qr) + abs(kc-qc) <= 1 else 0
    sel = rasp.Select(idx, idx, nb)
    flags = [rasp.numerical(rasp.Map(lambda v, j=j: 1 if (v == '.' and j%2==0) else 0, t)) for j in range(14)]
    cats = [rasp.categorical(rasp.Map(lambda v, j=j: (v + j) % VALSZ, idx)) for j in range(NCAT)]
    for step in range(8):
        new = []
        for j, f in enumerate(flags):
            a = rasp.numerical(rasp.Aggregate(sel, f, default=0))
            b = rasp.numerical(rasp.Map(lambda x: 0 if x < 1e-9 else (1 if abs(x-0.2)<1e-9 else None), a))
            new.append(b)
        flags = new
        cats = [rasp.categorical(rasp.Aggregate(sel, c)) for c in cats]
    lv = flags + [rasp.numerical(rasp.Map(lambda v: 1 if v == 3 else 0, c)) for c in cats]
    while len(lv) > 1:
        lv = [rasp.numerical(rasp.LinearSequenceMap(lv[i], lv[i+1], 1, 1)) for i in range(0, len(lv)-1, 2)] + ([lv[-1]] if len(lv)%2 else [])
    return lv[0]
