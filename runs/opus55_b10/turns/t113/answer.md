Final pass: 65.6% vs strong — consistent with the ~62–75% range of all recent versions (the added features show no clear, significant gains), but the pass machine measured 54 s/1000 positions for this 79M model, uncomfortably close to the 60 s limit. Since exceeding it would be catastrophic (uniform random play), I'll trade the two features with no demonstrated benefit (cut patterns and the region diffusion state) for speed: that allows ≤2 heads per layer, cutting attention parameters by a third. Let me restructure and check the schedule.

```python
s = open('/work/go.py').read()
# --- remove region diffusion (sg) and its constants
s = s.replace("""    nq2 = cmap(lambda q: NEAR_N2, qA)
    constc_d = cmap(lambda c: c, cmap(lambda c: c, cmap(lambda c: c, constc)))      # delay to depth 4
    nearone2 = rasp.Aggregate(rasp.Select(idx, nq2, LT), constc_d).named('nearone2')
    def clean2(x): return smap(cleanf, x, nearone2)
    def gEf(v, t):
        if v == 'P': return 'D' if t in ('B', 'W') else 'Z'
        return 'X' if t == 'x' else ('O' if t == 'o' else None)
    gE = cmap(lambda v: v, cmap(lambda v: v, smap(gEf, rowv, tok)))              # delay to depth 4
    emonly = lambda v, t: v if t == '.' else 'D'
    sg = clean2(smap(emonly, rasp.Aggregate(seedsel, gE), tok)).named('seed_g')
""", "")
s = s.replace("""        sg = clean2(rasp.Aggregate(sel, sg)).named('sg%d' % k)\n""", "")
# --- seeds one level later (values delayed), so that layer 3 holds only near-one + tadj
s = s.replace("""    sr = clean(smap(stonly, rasp.Aggregate(seedsel, rowE), tok)).named('seed_r')
    sc = clean(smap(stonly, rasp.Aggregate(seedsel, colE), tok)).named('seed_c')""",
"""    rowE_d = cmap(lambda v: v, rowE); colE_d = cmap(lambda v: v, colE)
    sr = clean(smap(stonly, rasp.Aggregate(seedsel, rowE_d), tok)).named('seed_r')
    sc = clean(smap(stonly, rasp.Aggregate(seedsel, colE_d), tok)).named('seed_c')""")
# --- positional: drop cut patterns; tadj at depth 3, t2 at depth 5
old = s[s.index("    # ---- positional (token based)"):s.index("    def dens(col):")]
new = r'''    # ---- positional (token based)
    tok_d2 = cmap(lambda t: t, cmap(lambda t: t, tok))                  # delay chain (depth 2)
    tadj = rasp.Aggregate(rasp.Select(idx, qA, GEQ), tok_d2)           # depth 3: soft token mix of neighbours
    tok_d4 = cmap(lambda t: t, cmap(lambda t: t, tok_d2))
    t2 = rasp.Aggregate(rasp.Select(idx, qB, GEQ), tok_d4)             # depth 5: soft token mix within distance 2
    def pres(col):
        return lambda v: 1.0 if v == col else (0.05 if v == 'W' else 0.0)
    thr = lambda x: int(x > 0.025)
    adj = smap(lambda a, b: (a, b), cmap(thr, nmap(pres('x'), tadj)), cmap(thr, nmap(pres('o'), tadj)))
'''
s = s.replace(old, new)
old2 = s[s.index("    def gbit(col):"):s.index("    extra = add(")]
s = s.replace(old2, "")
s = s.replace("""    cutcat = smap(lambda c, r: c + r, smap(lambda c, cont: CUT_VAL(c, cont), cuts, contested), regcat)\n""", "")
s = s.replace("""    extra = add(nmap(lambda v: v + 6.0, adjcat), nmap(lambda v: v + 12.0, cutcat))""",
              """    extra = nmap(lambda v: v + 6.0, adjcat)""")
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
        heads.setdefault(layer, []).append(nid)
    else: heads.setdefault(layer, []).append(nid)
print('layers', max(alloc.values())//2 + 1, 'max mlp', max(by_layer.values()), 'max heads', max(len(v) for v in heads.values()))
print(sorted((l, v) for l, v in heads.items() if len(v) > 2))
print(sorted((l, len(v)) for l, v in heads.items()))
```