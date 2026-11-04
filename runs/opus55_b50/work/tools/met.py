
import numpy as np
from tracr.compiler import compiling
def metrics(prog_fn, exact=1000):
    m = compiling.compile_rasp_to_model(prog_fn(), vocab={".", "x", "o", "B", "W"}, max_seq_len=82, compiler_bos="BOS", mlp_exactness=exact)
    P = m.params
    dense = rc = rows = cols = 0
    per = []
    for k, v in P.items():
        if 'transformer' not in k: continue
        w = np.asarray(v['w']); nz = np.abs(w) > 0
        r = nz.any(1).sum(); c = nz.any(0).sum()
        dense += w.size; rc += r * c; rows += r * w.shape[1]; cols += w.shape[0] * c
        per.append((k, w.shape, int(r), int(c)))
    return dict(dense=dense/1e6, rc=rc/1e6, rows=rows/1e6, cols=cols/1e6, L=m.model_config.num_layers), per, m
def load_prog(src):
    ns = {}
    exec(src, ns)
    return ns['program']
