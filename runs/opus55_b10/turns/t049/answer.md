The mass spread is small (0.9765–0.9824), so with a modest offset the error is ~0.1–0.2 logits — acceptable. Let me implement (a), (b), (c), and clip tactical scores at −20 so the offset can be 20.

```python
s = open('/work/go.py').read()
# (a) cheaper delayed query
s = s.replace("""    qC = smap(lambda i, s: Q(i, 'C'), idx, srow)               # delayed query (spreads heads over layers)""",
              """    qC = cmap(lambda q: Q(q.i, 'C'), qA)                         # delayed query (spreads heads over layers)""")
# (b) fold colour into the row-count tree
s = s.replace('''def decode_distinct(state, nvals):
    """state: soft categorical over 0..nvals-1, 'D' (real filler) and 'Z' (never produced).
    -> categorical count (0..3) of values with mass above EPS_DEC/2"""
    bits = []
    for c in range(nvals):
        m = nmap(lambda v, c=c: 1.0 if v == c else (EPS_DEC if v == 'Z' else 0.0), state)
        bits.append(nmap(lambda x: UNIT if x > EPS_DEC / 2 else 0.0, m))
    tot = sum_tree(bits)
    return cmap(lambda x: min(3, int(round(x / UNIT))), tot)''',
'''def decode_bits(state, nvals):
    bits = []
    for c in range(nvals):
        m = nmap(lambda v, c=c: 1.0 if v == c else (EPS_DEC if v == 'Z' else 0.0), state)
        bits.append(nmap(lambda x: UNIT if x > EPS_DEC / 2 else 0.0, m))
    return bits
def decode_distinct(state, nvals):
    """state: soft categorical over 0..nvals-1, 'D' (real filler) and 'Z' (never produced).
    -> categorical count (0..3) of values with mass above EPS_DEC/2"""
    tot = sum_tree(decode_bits(state, nvals))
    return cmap(lambda x: min(3, int(round(x / UNIT))), tot)
COLCODE = {'.': 0, 'x': 16, 'o': 32, 'B': 48, 'W': 48}''')
s = s.replace("""    nr = decode_distinct(sr, 9).named('nr')
    nc = decode_distinct(sc, 9).named('nc')
    def lclass(a, b):
        if a == 0 or b == 0: return 0
        if a == 1 and b == 1: return 1
        if a >= 3 or b >= 3: return 3
        return 2
    lcls = smap(lclass, nr, nc).named('lcls')
    def catf(l, t):
        if t == '.': return 'E'
        if t in ('x', 'o'): return ('X' if t == 'x' else 'O') + str(max(l, 1))
        return 'N'
    cst = smap(catf, lcls, tok).named('cst')""",
"""    colnum = nmap(lambda t: COLCODE[t] * UNIT, tok)
    nrc = cmap(lambda x: (int(round(x / UNIT)) // 16, min(3, int(round(x / UNIT)) % 16)),
               sum_tree(decode_bits(sr, 9) + [colnum])).named('nrc')
    nc = decode_distinct(sc, 9).named('nc')
    def lclass(a, b):
        if a == 0 or b == 0: return 0
        if a == 1 and b == 1: return 1
        if a >= 3 or b >= 3: return 3
        return 2
    def catf(cr, b):
        col, a = cr
        if col == 0: return 'E'
        if col in (1, 2): return ('X' if col == 1 else 'O') + str(max(lclass(a, b), 1))
        return 'N'
    cst = smap(catf, nrc, nc).named('cst')""")
# (c) no fetch cleaning
s = s.replace("""    cN, cS, cW, cE = clean_cat(cN), clean_cat(cS), clean_cat(cW), clean_cat(cE)\n""", "")
s = s.replace("T_OFF = 30.0", "T_OFF = 20.0")
s = s.replace("""    tcat = smap(lambda t, e: tactic_score(msum(TRIPLE_REP[t], (e,))), tW, cE).named('tcat')""",
              """    tcat = smap(lambda t, e: max(-20.0, tactic_score(msum(TRIPLE_REP[t], (e,)))), tW, cE).named('tcat')""")
open('/work/go.py','w').write(s)
import sys; sys.path.insert(0,'/work'); sys.setrecursionlimit(10000)
import importlib, go, estimate
importlib.reload(go)
print(estimate.estimate(go.program()))
r = compile_program()
print({k:v for k,v in r.items() if k!='residual_labels'})
```