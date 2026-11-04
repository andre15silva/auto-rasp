```python
import sys; sys.path.insert(0,'/work'); sys.setrecursionlimit(10000)
import importlib, go; importlib.reload(go)
from tracr.compiler import rasp_to_graph, nodes
from tracr.rasp import rasp
import networkx as nx
prog = go.program()
ex = rasp_to_graph.extract_rasp_graph(prog)
graph = ex.graph
depth = {}
for nid in nx.topological_sort(graph):
    preds = list(graph.predecessors(nid)); e = graph.nodes[nid][nodes.EXPR]
    base = max([depth[p] for p in preds], default=0)
    depth[nid] = (base + 1) if (isinstance(e, rasp.SOp) and preds) else base
def kind(e):
    if isinstance(e, rasp.Aggregate): return 'A'
    if isinstance(e, rasp.SelectorWidth): return 'S'
    if isinstance(e, (rasp.Map, rasp.SequenceMap, rasp.LinearSequenceMap)): return 'M'
levels = {}
for nid, dd in depth.items():
    k = kind(graph.nodes[nid][nodes.EXPR])
    if k: levels.setdefault(dd, []).append((k, nid))
for dd in sorted(levels):
    ks = ''.join(sorted(k for k,_ in levels[dd]))
    print(dd, ks[:40], [n for k,n in levels[dd] if k != 'M'][:6])
```