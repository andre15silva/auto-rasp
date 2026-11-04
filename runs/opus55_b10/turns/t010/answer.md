Key facts so far: BOS has no index embedding (zeros), numerical aggregates require 0/1-ish value sets, categorical MLPs have hidden width = output size, and compile time explodes with the number of graph paths. Let me test the core building blocks (custom relation objects as selector values, soft categorical diffusion) for compilability and cost.

```python
code = r'''
from tracr.rasp import rasp
MLP_EXACTNESS = 1000000
GT, LT, GEQ, LEQ, EQ = rasp.Comparison.GT, rasp.Comparison.LT, rasp.Comparison.GEQ, rasp.Comparison.LEQ, rasp.Comparison.EQ
def nbrs(i):
    if i >= 81: return []
    r, c = divmod(i, 9); out = []
    for dr, dc in ((-1,0),(0,-1),(0,1),(1,0)):
        rr, cc = r+dr, c+dc
        if 0 <= rr < 9 and 0 <= cc < 9: out.append(rr*9+cc)
    return out
def rel_left(k, i):
    if i >= 81: return k == 81
    return k == (i-1 if i % 9 else 81)
def rel_up(k, i):
    if i >= 81: return k == 81
    return k == (i-9 if i >= 9 else 81)
def rel_nb(k, i): return k in nbrs(i)
def rel_cmle(k, i):
    if k < 0: return False
    if k == 81 or i == 81: return k <= i
    return (k % 9, k // 9) <= (i % 9, i // 9)
class Q:
    __slots__ = ('i', 'k')
    def __init__(s, i, k): s.i = i; s.k = k
    def __hash__(s): return hash((s.i, s.k))
    def __eq__(s, o): return isinstance(o, Q) and s.i == o.i and s.k == o.k
    def __repr__(s): return f"Q{s.k}{s.i}"
    def __lt__(s, o):   # key > query
        if isinstance(o, Q): return (s.k, s.i) < (o.k, o.i)
        return RELS[s.k][0](o, s.i)
    def __gt__(s, o):   # key < query
        if isinstance(o, Q): return (s.k, s.i) > (o.k, o.i)
        return RELS[s.k][1](o, s.i)
    def __le__(s, o):   # key >= query
        if isinstance(o, Q): return (s.k, s.i) <= (o.k, o.i)
        return RELS[s.k][2](o, s.i)
    def __ge__(s, o):   # key <= query
        if isinstance(o, Q): return (s.k, s.i) >= (o.k, o.i)
        return RELS[s.k][3](o, s.i)
RELS = {'A': (rel_left, rel_up, rel_nb, rel_cmle)}

def program():
    tok = rasp.tokens; idx = rasp.indices
    qA = rasp.Map(lambda i: Q(i, 'A'), idx)
    ltok = rasp.Aggregate(rasp.Select(idx, qA, GT), tok)
    utok = rasp.Aggregate(rasp.Select(idx, qA, LT), tok)
    srow = rasp.SequenceMap(lambda t, l: (t not in 'xo') or (t != l), tok, ltok)
    scol = rasp.SequenceMap(lambda t, u: (t not in 'xo') or (t != u), tok, utok)
    ksr = rasp.SequenceMap(lambda i, s: i if s else 999, idx, srow)
    ksc = rasp.SequenceMap(lambda i, s: i if s else -1, idx, scol)
    ridr = rasp.SelectorWidth(rasp.Select(ksr, idx, LEQ))
    ridc = rasp.SelectorWidth(rasp.Select(ksc, qA, LEQ))
    kemp = rasp.SequenceMap(lambda i, t: i if t == '.' else -1, idx, tok)
    seed = rasp.Aggregate(rasp.Select(kemp, qA, GEQ), idx)
    s = seed
    for k in range(4):
        rid = ridr if k % 2 == 0 else ridc
        s = rasp.Aggregate(rasp.Select(rid, rid, EQ), s)
    ms = [rasp.numerical(rasp.Map(lambda v, c=c: 1.0 if v == c else (1e-5 if v == 81 else 0.0), s)) for c in range(81)]
    bs = [rasp.numerical(rasp.Map(lambda m: 1/128 if m > 5e-6 else 0.0, m)) for m in ms]
    while len(bs) > 1:
        nb = []
        for j in range(0, len(bs) - 1, 2):
            nb.append(rasp.numerical(rasp.LinearSequenceMap(bs[j], bs[j+1], 1.0, 1.0)))
        if len(bs) % 2: nb.append(bs[-1])
        bs = nb
    return bs[0]
'''
open('/work/program.py','w').write(code)
r = compile_program()
print({k:v for k,v in r.items() if k!='residual_labels'})
labs = r['residual_labels']
import collections
print(collections.Counter(l.split(':')[0] for l in labs).most_common(15))
```