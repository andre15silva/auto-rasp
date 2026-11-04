Compile cost jumped (205 s) mainly from extra decode nodes and the split_num double route; also 6 heads in one layer. Fixes: clean each fetched neighbor category through a numeric round-trip (exact one-hot), so the tactical/positional tables can be read with a single offset map exactly; move the positional aggregates to a later layer via a delayed query SOp.

```python
s = open('/work/go.py').read()
s = s.replace("""RELS = {'A': (r_left, r_up, r_nb, r_cmle),
        'B': (r_right, r_down, r_r2, r_nb81)}""", """RELS = {'A': (r_left, r_up, r_nb, r_cmle),
        'B': (r_right, r_down, r_r2, r_nb81),
        'C': (r_nb, r_r2, r_nb, r_nb)}""")
s = s.replace("""def split_num(catsop):""", """CATS = ['E', 'X1', 'X2', 'X3', 'O1', 'O2', 'O3', 'N']
def clean_cat(c):
    x = nmap(lambda v: 0.1 * CATS.index(v), c)
    return cmap(lambda y: CATS[min(7, max(0, int(round(y / 0.1))))], x)
T_OFF = 20.0
P_OFF = 6.0
def split_num(catsop):""")
s = s.replace("""    pNS = smap(lambda a, b: msum((a,), (b,)), cN, cS)""", """    cN, cS, cW, cE = clean_cat(cN), clean_cat(cS), clean_cat(cW), clean_cat(cE)
    pNS = smap(lambda a, b: msum((a,), (b,)), cN, cS)""")
s = s.replace("""    tact = split_num(tcat).named('tact')""", """    tact = nmap(lambda v: v + T_OFF, tcat).named('tact')""")
s = s.replace("""    pos = split_num(pcat).named('pos')""", """    pos = nmap(lambda v: v + P_OFF, pcat).named('pos')""")
s = s.replace("""    tadj = rasp.Aggregate(rasp.Select(idx, qA, GEQ), tok)     # soft token mix of on-board neighbours
    t2 = rasp.Aggregate(rasp.Select(idx, qB, GEQ), tok)       # soft token mix within distance 2""",
"""    qC = smap(lambda i, s: Q(i, 'C'), idx, srow)               # delayed query (spreads heads over layers)
    tadj = rasp.Aggregate(rasp.Select(idx, qC, GT), tok)      # soft token mix of on-board neighbours
    t2 = rasp.Aggregate(rasp.Select(idx, qC, LT), tok)        # soft token mix within distance 2""")
open('/work/go.py','w').write(s)
open('/work/program.py','w').write("import sys\nsys.path.insert(0, '/work')\nfrom go import program\nMLP_EXACTNESS = 1000000\n")
import sys; sys.path.insert(0,'/work'); sys.setrecursionlimit(10000)
import importlib, go, estimate
importlib.reload(go)
print(estimate.estimate(go.program()))
r = compile_program()
print({k:v for k,v in r.items() if k!='residual_labels'})
```