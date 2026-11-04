The time is going into Tracr's `compute_computational_depth`, a DFS without memoization: it visits every node once per *path* from the sources, and my diamond-shaped feature trees make the path count explode. Let me count paths per node to see which structures cause it.

```python
import sys, importlib, collections
sys.path.insert(0, '/work')
import gonet4; importlib.reload(gonet4)
from tracr.compiler import rasp_to_graph, nodes
import networkx as nx
from tracr.rasp import rasp
for stop in ['nbinfo', 'feat', 't1', None]:
    prog = gonet4.build(stop=stop)
    ext = rasp_to_graph.extract_rasp_graph(prog)
    G = ext.graph
    order = list(nx.topological_sort(G))
    paths = collections.defaultdict(int)
    for s in ext.sources: paths[s[nodes.ID]] = 1
    for n in order:
        for m in G.successors(n):
            paths[m] += paths[n]
    tot = sum(paths.values())
    top = sorted(paths.items(), key=lambda x: -x[1])[:5]
    print(stop, 'nodes', G.number_of_nodes(), 'total visits ~', f'{tot:.3g}', top[:3])
```