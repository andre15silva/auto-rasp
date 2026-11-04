Path counts are modest (~4e5), so the DFS shouldn't be the issue... yet the allocation step hung. Let me time `compute_computational_depth` and the allocation separately on the smaller `feat` graph.

```python
import sys, importlib, time
sys.path.insert(0, '/work')
import gonet4; importlib.reload(gonet4)
from tracr.compiler import rasp_to_graph, basis_inference, expr_to_craft_graph, craft_graph_to_model, nodes
from tracr.craft import bases
from tracr.rasp import rasp
prog = gonet4.build(stop='feat')
ext = rasp_to_graph.extract_rasp_graph(prog)
graph, sources, sink = ext.graph, ext.sources, ext.sink
basis_inference.infer_bases(graph, sink, {".", "x", "o", "B", "W"}, 82)
expr_to_craft_graph.add_craft_components_to_rasp_graph(graph, bos_dir=bases.BasisDirection(rasp.tokens.label, "BOS"), mlp_exactness=500000)
cnt = [0]
orig_succ = graph.successors
t0 = time.time()
d = craft_graph_to_model.compute_computational_depth(graph, [s[nodes.ID] for s in sources])
print('depth', round(time.time()-t0, 2))
t0 = time.time()
la = craft_graph_to_model._allocate_modules_to_layers(graph, sources)
print('alloc', round(time.time()-t0, 2))
t0 = time.time()
cm = craft_graph_to_model.craft_graph_to_model(graph, sources)
print('craft model', round(time.time()-t0, 2))
```