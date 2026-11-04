Tracr's `combine_in_parallel` calls `add_directions` (which re-sorts Python basis objects) for every (input direction × MLP) pair — so compile cost scales with how many MLPs share a layer and their total hidden size. Let me instrument the compile stages for `stop='t1'` to find the bottleneck.

```python
import time, sys, importlib, collections
sys.path.insert(0, '/work')
import gonet4; importlib.reload(gonet4)
from tracr.compiler import rasp_to_graph, basis_inference, expr_to_craft_graph, craft_graph_to_model, nodes
from tracr.craft import bases
from tracr.rasp import rasp
t0 = time.time()
prog = gonet4.build(stop='t1')
ext = rasp_to_graph.extract_rasp_graph(prog)
graph, sources, sink = ext.graph, ext.sources, ext.sink
basis_inference.infer_bases(graph, sink, {".", "x", "o", "B", "W"}, 82)
print('infer', round(time.time()-t0, 1), flush=True)
# report big value sets
vs = sorted(((len(graph.nodes[n][nodes.VALUE_SET]), n) for n in graph.nodes if nodes.VALUE_SET in graph.nodes[n]), reverse=True)[:12]
print(vs)
t0 = time.time()
slow = []
import tracr.compiler.expr_to_craft_graph as e2c
# time per-node craft construction by calling add_craft_components on the full graph but wrapping
orig = e2c.add_craft_components_to_rasp_graph
expr_to_craft_graph.add_craft_components_to_rasp_graph(graph, bos_dir=bases.BasisDirection(rasp.tokens.label, "BOS"), mlp_exactness=500000)
print('craft', round(time.time()-t0, 1), flush=True)
la = craft_graph_to_model._allocate_modules_to_layers(graph, sources)
per = collections.defaultdict(lambda: [0, 0, 0])
for nid, l in la.items():
    blk = graph.nodes[nid].get(nodes.MODEL_BLOCK)
    if blk is None: continue
    from tracr.craft import transformers
    if isinstance(blk, transformers.MLP):
        per[l][0] += 1; per[l][1] += blk.fst.output_space.num_dims; per[l][2] += blk.fst.input_space.num_dims
print('layer: nMLP, hidden_tot, input_tot')
for l in sorted(per):
    if per[l][0]: print(l, per[l])
```