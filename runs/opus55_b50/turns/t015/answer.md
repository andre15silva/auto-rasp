```python
import time
from tracr.rasp import rasp
from tracr.compiler import compiling
idx = rasp.indices
t = rasp.tokens
col = rasp.categorical(rasp.Map(lambda v: {'.':0,'x':1,'o':2}.get(v,0), t))
cur = rasp.categorical(rasp.Map(lambda v: v, idx))
for n in [20, 40, 82]:
    cur2 = rasp.categorical(rasp.Map(lambda v, n=n: v % n, idx))
    sm = rasp.categorical(rasp.SequenceMap(lambda x, y: (x + y) % 30, cur2, rasp.categorical(rasp.Map(lambda v,n=n: (v*7)%n, idx))))
    sm2 = rasp.categorical(rasp.SequenceMap(lambda x, y: (x + y) % 30, sm, col))
    out = rasp.numerical(rasp.Map(lambda v: v/100, sm2))
    t0=time.time()
    m = compiling.compile_rasp_to_model(out, vocab={".", "x", "o", "B", "W"}, max_seq_len=82, compiler_bos="BOS", mlp_exactness=100)
    print(n, time.time()-t0, m.model_config.mlp_hidden_size)
```