```python
s = open('/work/go.py').read()
s = s.replace("""    # exact zero / constant available only after the diffusion: used to schedule the positional tail late
    zr = nmap(lambda v: 0.0, sr).named('zr')
    dly = cmap(lambda x: 0, zr)
    isst_d = add(isst, zr, 1.0, 0.0)""", """    isst_d = add(isst, zr, 1.0, 0.0)""")
s = s.replace("""    colnum = nmap(lambda t: COLCODE[t] * UNIT, tok)""", """    # exact zero / constant available only after the diffusion: used to schedule the positional tail late
    zr = nmap(lambda v: 0.0, sr).named('zr')
    dly = cmap(lambda x: 0, zr)
    colnum = nmap(lambda t: COLCODE[t] * UNIT, tok)""")
open('/work/go.py','w').write(s)
import sys; sys.path.insert(0,'/work'); sys.setrecursionlimit(10000)
import importlib, go, estimate
importlib.reload(go)
print(estimate.estimate(go.program()))
from tracr.compiler import rasp_to_graph, basis_inference, expr_to_craft_graph, craft_graph_to_model
from tracr.craft import bases, transformers
prog = go.program()
ex = rasp_to_graph.extract_rasp_graph(prog)
graph, sources, sink = ex.graph, ex.sources, ex.sink
basis_inference.infer_bases(graph, sink, {".","x","o","B","W"}, 82)
expr_to_craft_graph.add_craft_components_to_rasp_graph(graph, bos_dir=bases.BasisDirection("tokens","BOS"), mlp_exactness=1000000)
alloc = craft_graph_to_model._allocate_modules_to_layers(graph, list({id(s): s for s in sources}.values()))
by_layer = {}; heads = {}
for nid, layer in alloc.items():
    blk = graph.nodes[nid].get('MODEL_BLOCK')
    if blk is None: continue
    if isinstance(blk, transformers.MLP): by_layer[layer] = by_layer.get(layer, 0) + blk.fst.output_space.num_dims
    elif isinstance(blk, transformers.SeriesWithResiduals):
        for b in blk.blocks:
            if isinstance(b, transformers.MLP): by_layer[layer+1] = by_layer.get(layer+1, 0) + b.fst.output_space.num_dims
        heads[layer] = heads.get(layer, 0) + 1
    else: heads[layer] = heads.get(layer, 0) + 1
print('layers', max(alloc.values())//2 + 1, 'max mlp', max(by_layer.values()), 'max heads', max(heads.values()))
print(sorted(heads.items()))
print(sorted(by_layer.items()))
```