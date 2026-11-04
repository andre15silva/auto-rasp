Calibration done: dense params are cheap (81M params → 2.6 s/1000 positions), but large categorical SequenceMaps are very slow to compile. Let me build a quick local-features baseline (v0) to observe the opponents.

```python
prog = r'''
from tracr.rasp import rasp
MLP_EXACTNESS = 100
SEL, UNSEL = 5.0, -5.0

def rc(i): return divmod(i, 9)
DIRS = {'N': (-1, 0), 'S': (1, 0), 'W': (0, -1), 'E': (0, 1)}
def nb_index(q, d):
    if q >= 81: return None
    r, c = rc(q); dr, dc = DIRS[d]
    rr, cc = r + dr, c + dc
    if 0 <= rr < 9 and 0 <= cc < 9: return rr * 9 + cc
    return 81   # edge sentinel = side token position

def shift_selector(d):
    def pred(k, q):
        t = nb_index(q, d)
        return SEL if (t is not None and k == t) else UNSEL
    return rasp.Select(rasp.indices, rasp.indices, pred)

PRIOR = [-2.0, -0.6, 0.8, 1.0, 0.7]
def prior(i):
    if i >= 81: return 0.0
    r, c = rc(i)
    line = min(r, c, 8 - r, 8 - c)
    return PRIOR[line]

def program():
    color = rasp.categorical(rasp.Map(lambda t: {'.': 'E', 'x': 'X', 'o': 'O'}.get(t, 'S'), rasp.tokens)).named('color')
    nc = {}
    for d in 'NSWE':
        nc[d] = rasp.categorical(rasp.Aggregate(shift_selector(d), color)).named('nc' + d)
    ns = rasp.categorical(rasp.SequenceMap(lambda a, b: tuple(sorted((a, b))), nc['N'], nc['S'])).named('pairNS')
    we = rasp.categorical(rasp.SequenceMap(lambda a, b: tuple(sorted((a, b))), nc['W'], nc['E'])).named('pairWE')
    def summ(p1, p2):
        l = p1 + p2
        return (l.count('E'), l.count('X'), l.count('O'), l.count('S'))
    summary = rasp.categorical(rasp.SequenceMap(summ, ns, we)).named('summary')
    def score(s, col):
        if col == 'S':
            return -3.0   # pass
        if col != 'E':
            return -20.0
        e, x, o, sd = s
        v = 0.0
        if x + sd == 4:     # own eye
            return -10.0
        if e == 0 and x == 0:   # likely suicide/self-atari single
            v -= 4.0
        if e == 1 and x == 0:
            v -= 1.5
        v += 0.3 * x * (1 if o > 0 else 0)
        v += 0.4 * min(o, 2) * (1 if e >= 1 else 0)
        return v
    loc = rasp.numerical(rasp.SequenceMap(score, summary, color)).named('loc')
    loc = rasp.numerical(rasp.Map(lambda v: v, rasp.categorical(rasp.SequenceMap(score, summary, color))))
    pri = rasp.numerical(rasp.Map(prior, rasp.indices)).named('prior')
    out = rasp.numerical(rasp.LinearSequenceMap(loc, pri, 1.0, 1.0)).named('logits')
    return out
'''
open('/work/program.py','w').write(prog)
r = compile_program()
```