The saving-capture branch adds 3 levels. I can trim to +1 level: skip the final threshold (use the linear fraction of flagged neighbors × 28, i.e., ≈7–14 bonus) and add it last: logit = (tact + pos) + savecap.

```python
s = open('/work/go.py').read()
s = s.replace("""    fnum = nmap(lambda v: 1.0 if v == 'F' else (0.1 if v == 'Z' else 0.0), fsoft)
    savecap = nmap(lambda x: SAVECAP_BONUS if x > 0.05 else 0.0, fnum).named('savecap')""",
"""    savecap = nmap(lambda v: SAVECAP_SCALE if v == 'F' else 0.0, fsoft).named('savecap')""")
s = s.replace("""    return add(add(tact, savecap), pos).named('logit')""", """    return add(add(tact, pos), savecap).named('logit')""")
s = s.replace("SAVECAP_BONUS = 7.0", "SAVECAP_SCALE = 28.0")
open('/work/go.py','w').write(s)
import sys; sys.path.insert(0,'/work'); sys.setrecursionlimit(10000)
import importlib, go, estimate; importlib.reload(go)
from tracr.compiler import rasp_to_graph, basis_inference, expr_to_craft_graph, craft_graph_to_model
from tracr.craft import bases, transformers
prog = go.program()
print(estimate.estimate(prog))
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
print([(l, w) for l, w in sorted(by_layer.items()) if l >= 40], [(l, h) for l, h in sorted(heads.items()) if l >= 40])
```