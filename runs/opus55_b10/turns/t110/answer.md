MLP width is still 457, so another layer sums to that. Let me find it.

```python
import sys; sys.path.insert(0,'/work'); sys.setrecursionlimit(10000)
import importlib, go; importlib.reload(go)
from tracr.compiler import rasp_to_graph, basis_inference, expr_to_craft_graph, craft_graph_to_model
from tracr.craft import bases, transformers
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
    elif isinstance(blk, transformers.SeriesWithResiduals):
        for b in blk.blocks:
            if isinstance(b, transformers.MLP): by_layer.setdefault(layer+1, []).append((nid+'*', b.fst.output_space.num_dims))
for layer in sorted(by_layer):
    tot = sum(w for _, w in by_layer[layer])
    if tot > 250: print(layer, tot, sorted(by_layer[layer], key=lambda x: -x[1])[:6])
```