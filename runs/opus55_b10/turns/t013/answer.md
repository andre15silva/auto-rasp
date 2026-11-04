```python
import sys, time, cProfile, pstats, io
sys.path.insert(0,'/work')
import go
go_src = open('/work/go.py').read()
# smaller variant: decode only 20 coordinates
small = go_src.replace("for c in range(81):", "for c in range(20):")
open('/work/go_small.py','w').write(small)
import go_small
from tracr.compiler import compiling, rasp_to_graph, basis_inference, craft_graph_to_model, expr_to_craft_graph, craft_model_to_transformer
from tracr.compiler import nodes as cnodes
prog = go_small.program()
t0=time.time()
extracted = rasp_to_graph.extract_rasp_graph(prog)
graph, sources, sink = extracted.graph, extracted.sources, extracted.sink
print('nodes', graph.number_of_nodes(), 'extract', time.time()-t0); t0=time.time()
basis_inference.infer_bases(graph, sink, {".","x","o","B","W"}, 82)
print('basis', time.time()-t0); t0=time.time()
expr_to_craft_graph.add_craft_components_to_rasp_graph(graph, bos_dir=__import__('tracr').craft.bases.BasisDirection("tokens","BOS"), mlp_exactness=1e7)
print('craft comps', time.time()-t0); t0=time.time()
pr = cProfile.Profile(); pr.enable()
craft_model = craft_graph_to_model.craft_graph_to_model(graph, sources)
pr.disable()
print('craft model', time.time()-t0); t0=time.time()
s = io.StringIO(); pstats.Stats(pr, stream=s).sort_stats('tottime').print_stats(12); print(s.getvalue()[:3000])
```