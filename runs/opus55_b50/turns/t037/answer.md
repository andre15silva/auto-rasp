The timing noise is large (±2×), but my programs remain much slower per dense parameter than toys. Their implementation likely prunes zero rows/columns. Let me compute candidate "effective size" metrics from the compiled weights (inspection only, no forward pass) for models I've timed, to find which metric predicts time.

```python
import numpy as np, time, sys, importlib
sys.path.insert(0,'/work')
from tracr.compiler import compiling
def metrics(prog_fn):
    m = compiling.compile_rasp_to_model(prog_fn(), vocab={".", "x", "o", "B", "W"}, max_seq_len=82, compiler_bos="BOS", mlp_exactness=1000)
    P = m.params
    dense = rc = rows = cols = 0
    for k, v in P.items():
        if 'transformer' not in k: continue
        w = np.asarray(v['w']); nz = np.abs(w) > 0
        r = nz.any(1).sum(); c = nz.any(0).sum()
        dense += w.size; rc += r * c; rows += r * w.shape[1]; cols += w.shape[0] * c
    return dict(dense=dense/1e6, rc=rc/1e6, rows=rows/1e6, cols=cols/1e6, L=m.model_config.num_layers)
import gonet; importlib.reload(gonet)
gonet.UNSEL = 0.0
print('prop', metrics(lambda: gonet.build(stop='prop')))
gonet.FIXSEL = True
print('prop_fix', metrics(lambda: gonet.build(stop='prop')))
gonet.FIXSEL = False
```