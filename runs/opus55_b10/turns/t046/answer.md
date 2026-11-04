Layer 1 has two 410-wide SequenceMaps (rowE/colE built from the 82-valued index) — easy to shrink. Also many layers are half-empty (e.g., diffusion rounds spread over 9 layers): Tracr assigns layers by longest-path depth and only condenses a depth level into the preceding attention layer when the whole level is MLP-only, so parallel branches with mismatched parity waste layers. Let me analyze depth levels to find where attention and MLP nodes mix.

```python
import sys; sys.path.insert(0,'/work'); sys.setrecursionlimit(10000)
import importlib, go; importlib.reload(go)
from tracr.compiler import rasp_to_graph, basis_inference, expr_to_craft_graph, craft_graph_to_model, nodes
from tracr.craft import bases, transformers
from tracr.rasp import rasp
prog = go.program()
ex = rasp_to_graph.extract_rasp_graph(prog)
graph, sources, sink = ex.graph, ex.sources, ex.sink
# longest-path depth (SOp nodes count +1), computed by DP instead of DFS
import networkx as nx
depth = {}
for nid in nx.topological_sort(graph):
    preds = list(graph.predecessors(nid))
    e = graph.nodes[nid][nodes.EXPR]
    base = max([depth[p] for p in preds], default=0)
    # depth increments only for SOp nodes
    depth[nid] = (base + 1) if (isinstance(e, rasp.SOp) and preds) else base
def kind(e):
    if isinstance(e, (rasp.Aggregate,)): return 'A'
    if isinstance(e, rasp.SelectorWidth): return 'S'
    if isinstance(e, (rasp.Map, rasp.SequenceMap, rasp.LinearSequenceMap)): return 'M'
    return None
levels = {}
for nid, dd in depth.items():
    k = kind(graph.nodes[nid][nodes.EXPR])
    if k: levels.setdefault(dd, []).append((k, nid))
for dd in sorted(levels):
    ks = ''.join(sorted(k for k,_ in levels[dd]))
    print(dd, ks[:60], [n for k,n in levels[dd]][:6])
```