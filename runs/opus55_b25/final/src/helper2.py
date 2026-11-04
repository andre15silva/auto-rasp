
import sys, importlib, collections
sys.path.insert(0,'/work')
from tracr.compiler import rasp_to_graph, basis_inference, expr_to_craft_graph, craft_graph_to_model, nodes
from tracr.rasp import rasp
def layer_report(prog_fn):
    out = prog_fn()
    g = rasp_to_graph.extract_rasp_graph(out)
    basis_inference.infer_bases(g.graph, g.sink, {".", "x", "o", "B", "W"}, 82)
    expr_to_craft_graph.add_craft_components_to_rasp_graph(g.graph, bos_dir=__import__('tracr').craft.bases.BasisDirection('tokens','BOS'), mlp_exactness=100)
    alloc = craft_graph_to_model._allocate_modules_to_layers(g.graph, g.sources)
    bylayer = collections.defaultdict(list)
    for nid, l in alloc.items():
        node = g.graph.nodes[nid]
        blk = node.get(nodes.MODEL_BLOCK)
        w = ''
        if blk is not None and hasattr(blk, 'fst'): w = blk.fst.output_space.num_dims
        bylayer[l].append(f"{node[nodes.EXPR].label}{'('+str(w)+')' if w!='' else ''}")
    for l in sorted(bylayer): print(l//2, 'attn' if l%2==0 else 'mlp ', bylayer[l])
