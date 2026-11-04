Too heavy (30 layers, 605-wide MLP layer, 122M params). Let me inspect the per-layer allocation of the new branch to re-schedule it.

```python
import sys; sys.path.insert(0,'/work'); sys.setrecursionlimit(10000)
import importlib, go; importlib.reload(go)
from tracr.compiler import rasp_to_graph, basis_inference, expr_to_craft_graph, craft_graph_to_model, nodes
from tracr.craft import bases, transformers
from tracr.rasp import rasp
prog = go.program()
ex = rasp_to_graph.extract_rasp_graph(prog)
graph, sources, sink = ex.graph, ex.sources, ex.sink
basis_inference.infer_bases(graph, sink, {".","x","o","B","W"}, 82)
expr_to_craft_graph.add_craft_components_to_rasp_graph(graph, bos_dir=bases.BasisDirection("tokens","BOS"), mlp_exactness=1000000)
alloc = craft_graph_to_model._allocate_modules_to_layers(graph, list({id(s): s for s in sources}.values()))
by_layer = {}
for nid, layer in alloc.items():
    blk = graph.nodes[nid].get('MODEL_BLOCK')
    if blk is None: continue
    if isinstance(blk, transformers.MLP): by_layer.setdefault(layer, []).append((nid, blk.fst.output_space.num_dims))
    elif isinstance(blk, transformers.SeriesWithResiduals): by_layer.setdefault(layer, []).append((nid, 'SW'))
    else: by_layer.setdefault(layer, []).append((nid, 'A'))
for layer in sorted(by_layer):
    if layer >= 40:
        print(layer, [(n, w) for n, w in by_layer[layer]][:8])
```