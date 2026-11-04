```python
import sys, collections, importlib
sys.path.insert(0,'/work')
def estimate(prog):
    order=[]; seen=set()
    def topo(e):
        if id(e) in seen: return
        seen.add(id(e))
        for c in e.children: topo(c)
        order.append(e)
    topo(prog)
    down = collections.defaultdict(int); down[id(prog)] = 1
    for e in reversed(order):
        for c in e.children: down[id(c)] += down[id(e)]
    parents = collections.defaultdict(list)
    for e in order:
        for c in e.children: parents[id(c)].append(e)
    leaves = [e for e in order if not e.children]
    tot = 0
    for L in leaves:
        cnt = collections.defaultdict(int); cnt[id(L)] = 1
        for e in order:
            if cnt[id(e)]:
                for p in parents[id(e)]: cnt[id(p)] += cnt[id(e)]
        tot += down[id(L)] * sum(cnt.values())
    return tot, len(order)
import prog_test; importlib.reload(prog_test)
print('prog_test (range 4) estimate', estimate(prog_test.program()), 'measured dfs calls 2650472')
# run 11 program
run11 = open('/work/program.py').read()
import re
src11 = r'''
from tracr.rasp import rasp
GT, LT, GEQ, LEQ, EQ = rasp.Comparison.GT, rasp.Comparison.LT, rasp.Comparison.GEQ, rasp.Comparison.LEQ, rasp.Comparison.EQ
import go
Q = go.Q
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
open('/work/prog11.py','w').write(src11)
import prog11
print('run11 estimate', estimate(prog11.program()), 'compile 40.8s')
```