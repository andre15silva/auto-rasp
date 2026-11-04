Our big losses come from groups already dead before the capture (lost races / life-and-death), which is hard to fix; the clearer problem is the flat, edge-heavy positional play. Let me rewrite the positional evaluation: stone densities within distance 2 (0/low/mid/high via thresholded fractions), adjacency, line; sharper values; 1st/2nd-line moves strongly discouraged outside contested areas; own-area and deep-opponent-area moves below pass.

```python
s = open('/work/go.py').read()
start = s.index("def pos_score(")
end = s.index("def build_triple_classes")
new_pos = '''LINE_OPEN = {0: -1.5, 1: 0.0, 2: 2.5, 3: 2.8, 4: 3.5}
def pos_score(nx2, no2, ax, ao, line):
    """nx2/no2: density level (0 none, 1 low, 2 mid, 3 high) of own/opponent stones within
    Manhattan distance 2; ax/ao: adjacent own/opponent stone present; line: distance to edge."""
    edge = {0: -3.0, 1: -1.2}.get(line, 0.0)
    if nx2 == 0 and no2 == 0:                  # open area
        return LINE_OPEN[line]
    if no2 == 0:                               # own sphere only
        if ax: return -5.0
        return (0.5 if nx2 == 1 else -3.0) + edge
    if nx2 == 0:                               # opponent sphere only
        if ao: return (0.0 if no2 == 1 else -3.5) + edge
        return (1.5 if no2 == 1 else -2.5) + edge
    s = 3.0                                    # contested
    if ax and ao: s += 1.0
    elif ao: s += 0.8
    elif ax: s += 0.3
    if nx2 >= 2 and no2 <= 1: s -= 0.5         # mostly ours already
    if no2 >= 2 and nx2 <= 1: s += 0.3         # pushing into their side
    return s + {0: -1.5, 1: -0.5}.get(line, 0.0)

'''
s = s[:start] + new_pos + s[end:]
s = s.replace("PASS_LOGIT = -2.0\n", "PASS_LOGIT = -2.0\nP_OFF = 8.0\n", 1)
s = s.replace("P_OFF = 6.0\n", "")
old_pos_block = s[s.index("    tadj = rasp.Aggregate("):s.index("    pos = nmap(")]
new_pos_block = '''    tadj = rasp.Aggregate(rasp.Select(idx, qA, GEQ), tok)     # soft token mix of on-board neighbours
    t2 = rasp.Aggregate(rasp.Select(idx, qB, GEQ), tok)       # soft token mix within distance 2
    def pres(col):
        return lambda v: 1.0 if v == col else (0.05 if v == 'W' else 0.0)
    thr = lambda x: int(x > 0.025)
    hasx = cmap(thr, nmap(pres('x'), tadj)); haso = cmap(thr, nmap(pres('o'), tadj))
    def dens(col):
        return lambda v: 1.0 if v == col else ({'B': 0.1, 'W': 0.4}.get(v, 0.0))
    def lev(x):
        return 0 if x < 0.05 else (1 if x < 0.25 else (2 if x < 0.7 else 3))
    nx2 = cmap(lev, nmap(dens('x'), t2)); no2 = cmap(lev, nmap(dens('o'), t2))
    adj = smap(lambda a, b: (a, b), hasx, haso)
    e2 = smap(lambda a, b: (a, b), nx2, no2)
    lin = cmap(lambda i: 'P' if i >= 81 else line_of(i), idx)
    adjl = smap(lambda a, l: 'P' if l == 'P' else a + (l,), adj, lin)
    def pfin(e, a):
        if a == 'P': return PASS_LOGIT
        return pos_score(e[0], e[1], a[0], a[1], a[2])
    pcat = smap(pfin, e2, adjl).named('pcat')
'''
s = s.replace(old_pos_block, new_pos_block)
open('/work/go.py','w').write(s)
import sys; sys.path.insert(0,'/work'); sys.setrecursionlimit(10000)
import importlib, go
importlib.reload(go)
print(go.P_OFF, go.T_OFF, min(go.pos_score(a,b,c,d,l) for a in range(4) for b in range(4) for c in range(2) for d in range(2) for l in range(5)))
# check dummy thresholds: value set {0, 0.1, 0.4, 1}: midpoints 0.05, 0.25, 0.7
print([go.line_of(i) for i in range(9)])
```