Still over 900 s. Let me find which part of the tail is slow to compile by compiling truncated versions (without the speed measurement).

```python
s = open('/work/gonet4.py').read()
if "stop == 't1'" not in s:
    s = s.replace("    t1 = num(M(lambda v: v, t1c), 't1')\n", "    t1 = num(M(lambda v: v, t1c), 't1')\n    if stop == 't1': return t1\n")
    s = s.replace("    t5 = num(M(lambda v: v, t5c), 't5')\n", "    t5 = num(M(lambda v: v, t5c), 't5')\n    if stop == 't5': return lsm(t4, t5, 'dbg5')\n")
    s = s.replace("    t6 = num(M(lambda v: v, t6c), 't6')\n", "    t6 = num(M(lambda v: v, t6c), 't6')\n    if stop == 't6': return t6\n")
    open('/work/gonet4.py','w').write(s)
import time, sys, importlib
sys.path.insert(0, '/work')
import gonet4; importlib.reload(gonet4)
from tracr.compiler import compiling
for stop in ['t1', 't6']:
    t0 = time.time()
    m = compiling.compile_rasp_to_model(gonet4.build(stop=stop), vocab={".", "x", "o", "B", "W"}, max_seq_len=82, compiler_bos="BOS", mlp_exactness=500000)
    print(stop, 'compile', round(time.time()-t0), 'D', len(m.residual_labels), 'layers', m.model_config.num_layers, flush=True)
```