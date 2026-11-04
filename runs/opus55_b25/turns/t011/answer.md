```python
import time, signal
from tracr.rasp import rasp
from tracr.compiler import compiling

def handler(signum, frame): raise TimeoutError()
signal.signal(signal.SIGALRM, handler)

def build(n_seq, valsize):
    a = rasp.categorical(rasp.Map(lambda i: i % valsize, rasp.indices))
    b = rasp.categorical(rasp.Map(lambda t: 0 if t == '.' else 1, rasp.tokens))
    for it in range(n_seq):
        c = rasp.categorical(rasp.SequenceMap(lambda x, y: min(x, y), a, b))
        a, b = b, c
    return rasp.numerical(rasp.Map(lambda v: v / 82, b))

for n_seq, vs in [(1, 20), (1, 40), (2, 40)]:
    signal.alarm(250)
    t = time.time()
    try:
        m = compiling.compile_rasp_to_model(build(n_seq, vs), vocab={".", "x", "o", "B", "W"}, max_seq_len=82, compiler_bos="BOS", mlp_exactness=100)
        print(n_seq, vs, 'ok', time.time() - t, m.model_config.mlp_hidden_size, len(m.residual_labels))
    except TimeoutError:
        print(n_seq, vs, 'timeout', time.time() - t)
    signal.alarm(0)
```