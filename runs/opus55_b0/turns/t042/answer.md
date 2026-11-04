```python
import sys, importlib
sys.path.insert(0, '/work')
from tracr.compiler import rasp_to_graph, basis_inference, expr_to_craft_graph, craft_graph_to_model, nodes
from tracr.rasp import rasp as R
from tracr.compiler import compiling as C

def layer_report(modname):
    for m in list(sys.modules):
        if m in ('gocore','gotmpl','gotmpl6','gowin') or m.startswith('prog_v'):
            del sys.modules[m]
    mod = importlib.import_module(modname)
    prog = mod.program()
    extracted = rasp_to_graph.extract_rasp_graph(prog)
    graph, sources, sink = extracted.graph, extracted.sources, extracted.sink
    basis_inference.infer_bases(graph, sink, {".", "x", "o", "B", "W"}, 82)
    expr_to_craft_graph.add_craft_components_to_rasp_graph(graph, bos_dir=C.bases.BasisDirection("tokens", "BOS") if hasattr(C,'bases') else None, mlp_exactness=100) if False else None
    return graph, sources, sink

import tracr.compiler.compiling as CC
import inspect
print(inspect.getsource(CC.compile_rasp_to_model)[:2500])
```