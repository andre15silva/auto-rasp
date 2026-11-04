Confirmed: BFS without a visited set, so `sources` has one entry per tip→leaf path, and the depth DFS cost is ≈ Σ_leaf (#tip→leaf paths) × (#paths out of the leaf). Let me compute these quantities for v3 (compiles fast) and v4 stages to see what budget I have and which nodes create the path explosion.

```python
import sys, importlib, collections
sys.path.insert(0, '/work')
import networkx as nx
from tracr.compiler import rasp_to_graph, nodes
def path_cost(prog):
    ext = rasp_to_graph.extract_rasp_graph(prog)
    G = ext.graph
    src = collections.Counter(s[nodes.ID] for s in ext.sources)
    order = list(nx.topological_sort(G))
    # simple-graph paths out of each node (to all nodes): pout[n] = 1 + sum pout[succ]
    pout = {}
    for n in reversed(order):
        pout[n] = 1 + sum(pout[m] for m in G.successors(n))
    cost = sum(cnt * pout[leaf] for leaf, cnt in src.items())
    return src, {l: pout[l] for l in src}, cost, G
import gonet, gonet4
importlib.reload(gonet); importlib.reload(gonet4)
for nm, fn in [('v3', lambda: gonet.build()), ('v4 nbinfo', lambda: gonet4.build(stop='nbinfo')), ('v4 feat', lambda: gonet4.build(stop='feat')), ('v4 t1', lambda: gonet4.build(stop='t1'))]:
    src, po, cost, G = path_cost(fn())
    print(nm, 'source entries', dict(src), 'pout', po, 'cost %.3g' % cost)
```