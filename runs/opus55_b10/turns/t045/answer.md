The MLP width is still 991, so another MLP is that wide, and there are still 32 layers. Let me inspect the compiled block structure (per layer: heads and MLPs with their hidden widths) to see where width and depth come from.

```python
import sys, time; sys.path.insert(0,'/work'); sys.setrecursionlimit(10000)
import importlib, go; importlib.reload(go)
from tracr.compiler import rasp_to_graph, basis_inference, expr_to_craft_graph, craft_graph_to_model
from tracr.craft import bases, transformers
prog = go.program()
ex = rasp_to_graph.extract_rasp_graph(prog)
graph, sources, sink = ex.graph, ex.sources, ex.sink
basis_inference.infer_bases(graph, sink, {".","x","o","B","W"}, 82)
expr_to_craft_graph.add_craft_components_to_rasp_graph(graph, bos_dir=bases.BasisDirection("tokens","BOS"), mlp_exactness=1000000)
# instead of full model, replicate layer allocation
alloc = craft_graph_to_model._allocate_modules_to_layers(graph, list({id(s): s for s in sources}.values()))
by_layer = {}
for nid, layer in alloc.items():
    node = graph.nodes[nid]
    blk = node.get('MODEL_BLOCK')
    if blk is None: continue
    if isinstance(blk, transformers.MLP):
        w = blk.fst.output_space.num_dims; kind = 'mlp'
    elif isinstance(blk, transformers.SeriesWithResiduals):
        w = [ (type(b).__name__, b.fst.output_space.num_dims if isinstance(b, transformers.MLP) else '') for b in blk.blocks]; kind='series'
    else:
        w = ''; kind = 'attn'
    by_layer.setdefault(layer, []).append((kind, nid, w))
for layer in sorted(by_layer):
    items = by_layer[layer]
    tot = sum(x[2] for x in items if x[0]=='mlp')
    print(layer, 'tot_mlp', tot, [(k, n, w) for k, n, w in items if k!='mlp' or (isinstance(w,int) and w>40)][:8], 'n_items', len(items))
```