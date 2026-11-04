```python
import time
from tracr.rasp import rasp
from tracr.compiler import compiling
idx = rasp.indices
cur = rasp.categorical(rasp.Map(lambda v: v, idx))
sm = rasp.categorical(rasp.SequenceMap(lambda x, y: (x + y) % 30, cur, idx))
out = rasp.numerical(rasp.Map(lambda v: v/100, sm))
t0=time.time()
m = compiling.compile_rasp_to_model(out, vocab={".", "x", "o", "B", "W"}, max_seq_len=82, compiler_bos="BOS", mlp_exactness=100)
print(time.time()-t0, m.model_config)
```