Same config gave 35.9% then 45.3% — pure noise; everything sits at ~40%. A more promising, rule-based lever: under Tromp-Taylor scoring with no dead-stone removal, an invading stone left uncaptured neutralizes the opponent's whole region, and our dead stones cost nothing. So when we're *losing in a settled position*, invading the opponent's territory is a free lottery ticket (the bot may pass or misplay). I'll add that: broadcast the side-to-move token to all points (cheap positional head), and give opponent-region moves a bonus when the TT estimate says we're losing and ≤2 neutral points remain.

```python
s = open('/work/gonet4.py').read()
s = s.replace("""    s14 = lsm(t1, t4, 's14')
    s56 = lsm(t5, t6, 's56')
    return lsm(s14, s56, 'logits')""", """    def pside(k, q):
        return SEL if k == 81 else UNSEL
    sideall = cat(rasp.Aggregate(rasp.Select(idx, idx, pside), side), 'sideall')
    def lsf(ps, sd):
        tc, nc = ps
        win = (tc >= 5) if sd == 'B' else (tc >= 2)
        return (not win) and nc <= 1
    losing = cat(SM(lsf, pstate, sideall), 'losing')
    t7c = cat(SM(lambda rg, l: round(OFF7 + (INV if (rg == 'opp' and l) else 0.0), 2), region, losing), 't7c')
    t7 = num(M(lambda v: v, t7c), 't7')
    s14 = lsm(t1, t4, 's14')
    s56 = lsm(t5, t6, 's56')
    s567 = lsm(s56, t7, 's567')
    return lsm(s14, s567, 'logits')""")
s = s.replace("OFF1, OFF4, OFF5, OFF6 = 25.0, 20.0, 5.0, 10.0", "OFF1, OFF4, OFF5, OFF6 = 25.0, 20.0, 5.0, 10.0\nOFF7, INV = 1.0, 6.0")
open('/work/gonet4.py','w').write(s)
import importlib, sys, collections
sys.path.insert(0, '/work'); import gonet4; importlib.reload(gonet4)
import networkx as nx
from tracr.compiler import rasp_to_graph, nodes
ext = rasp_to_graph.extract_rasp_graph(gonet4.build())
G = ext.graph; src_ = collections.Counter(x[nodes.ID] for x in ext.sources)
order = list(nx.topological_sort(G)); pout = {}
for n in reversed(order): pout[n] = 1 + sum(pout[m] for m in G.successors(n))
print('path cost %.3g' % sum(c * pout[l] for l, c in src_.items()))
r = compile_program()
```