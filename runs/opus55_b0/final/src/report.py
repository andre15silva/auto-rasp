
import sys, importlib, collections
from tracr.compiler import rasp_to_graph, basis_inference, expr_to_craft_graph, craft_graph_to_model, nodes
from tracr.craft import bases, transformers
from tracr.rasp import rasp

def layer_report(modname, verbose=True):
    for m in list(sys.modules):
        if m in ('gocore','gotmpl','gotmpl6','gowin') or m.startswith('prog_v'):
            del sys.modules[m]
    mod = importlib.import_module(modname)
    prog = mod.program()
    ex = rasp_to_graph.extract_rasp_graph(prog)
    g, sources, sink = ex.graph, ex.sources, ex.sink
    basis_inference.infer_bases(g, sink, {".", "x", "o", "B", "W"}, 82)
    expr_to_craft_graph.add_craft_components_to_rasp_graph(g, bos_dir=bases.BasisDirection(rasp.tokens.label, "BOS"), mlp_exactness=100)
    alloc = craft_graph_to_model._allocate_modules_to_layers(g, sources)
    per = collections.defaultdict(list)
    for nid, layer in alloc.items():
        node = g.nodes[nid]
        blk = node.get(nodes.MODEL_BLOCK)
        expr = node[nodes.EXPR]
        if isinstance(blk, transformers.SeriesWithResiduals):
            per[layer].append(("SW-attn", expr.label, 1))
            per[layer + 1].append(("SW-mlp", expr.label, blk.blocks[1].fst.output_space.num_dims))
        elif isinstance(blk, transformers.MLP):
            per[layer].append(("mlp", expr.label, blk.fst.output_space.num_dims))
        else:
            per[layer].append(("attn", expr.label, 1))
    out = []
    for L in sorted(per):
        items = per[L]
        tot = sum(h for t, _, h in items if 'mlp' in t)
        na = sum(1 for t, _, _ in items if 'attn' in t)
        out.append((L, na, tot, [n for _, n, _ in items]))
        if verbose:
            print(L, "attn" if L % 2 == 0 else "mlp ", "heads=%d" % na if L % 2 == 0 else "hid=%d" % tot, [n for _, n, _ in items][:12])
    return out
