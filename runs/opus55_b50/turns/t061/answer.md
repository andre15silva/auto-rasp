This is the actual timing harness. Key facts: heads whose query/key read only positional dims (indices) have their attention pattern **precomputed once** (nearly free), and all zero rows/columns are pruned. So the cost is dominated by **data-dependent heads** (my graded run-start heads and the 48 EQ propagation heads), each needing a per-position 83×83 softmax. Let me confirm with the FIXSEL variant (propagation via positional selectors).

```python
import time
for v in [dict(FIXSEL=True), dict()]:
    hdr = '\n'.join(f'gonet.{k} = {val}' for k, val in v.items())
    open('/work/program.py','w').write(f'''
import sys
sys.path.insert(0, '/work')
import importlib, gonet
importlib.reload(gonet)
{hdr}
MLP_EXACTNESS = 1000
def program():
    return gonet.build()
''')
    t0 = time.time()
    print(v, end=' '); r = compile_program(); print('  wall', round(time.time()-t0))
```