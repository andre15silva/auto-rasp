"""A harness test program (NOT shown to the writer): a crude Go heuristic in RASP, used to measure Tracr model
sizes/speeds and to test the compile -> export -> forward pipeline. ROUNDS rounds of categorical propagation of
"this stone's group touches an empty point" along same-colour chains, then a numerical move score."""
from tracr.rasp import rasp

ROUNDS = 3
DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def nb(q, d):
    if q >= 81:
        return -1
    r, c = divmod(q, 9)
    r2, c2 = r + d[0], c + d[1]
    return r2 * 9 + c2 if 0 <= r2 < 9 and 0 <= c2 < 9 else -1


def program(rounds=ROUNDS):
    toks, idx = rasp.tokens, rasp.indices
    sels = [rasp.Select(idx, idx, (lambda d: lambda k, q: k == nb(q, d))(d)) for d in DIRS]
    nt = [rasp.Aggregate(s, toks, default=None) for s in sels]           # neighbour token (None off-board)
    cnt = lambda a, b: (a == ".") + (b == ".")
    ud = rasp.SequenceMap(cnt, nt[0], nt[1])
    lr = rasp.SequenceMap(cnt, nt[2], nt[3])
    n_emp = rasp.SequenceMap(lambda a, b: a + b, ud, lr)                    # categorical 0..4
    cell = rasp.SequenceMap(lambda t, n: (t, n > 0) if t in "xo" else (t, False), toks, n_emp)
    for _ in range(rounds):
        nbs = [rasp.Aggregate(s, cell, default=None) for s in sels]

        def upd(c, n):
            t, l = c
            if t not in "xo" or l or n is None:
                return c
            return (t, n[0] == t and n[1])
        for n in nbs:
            cell = rasp.SequenceMap(upd, cell, n)
    dead = rasp.numerical(rasp.Map(lambda c: 1 if (c[0] == "o" and not c[1]) else 0, cell))
    dead_nb = [rasp.numerical(rasp.Aggregate(s, dead, default=0)) for s in sels]
    libs = rasp.numerical(rasp.Map(lambda n: 0.5 * n, n_emp))
    empty = rasp.numerical(rasp.Map(lambda t: 1 if t == "." else 0, toks))
    score = rasp.numerical(rasp.LinearSequenceMap(libs, empty, 1, 1))
    for e in dead_nb:
        score = rasp.numerical(rasp.LinearSequenceMap(score, e, 1, 3))
    return score.named("logits")
