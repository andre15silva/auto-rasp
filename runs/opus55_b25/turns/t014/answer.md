```python
import time, signal, cProfile, pstats, io
from tracr.rasp import rasp
from tracr.compiler import compiling

def handler(signum, frame): raise TimeoutError()
signal.signal(signal.SIGALRM, handler)

def nbr_sel(dr, dc):
    def pred(k, q):
        if q >= 81: return False
        r, c = divmod(q, 9)
        r2, c2 = r + dr, c + dc
        if not (0 <= r2 < 9 and 0 <= c2 < 9): return False
        return k == r2 * 9 + c2
    return rasp.Select(rasp.indices, rasp.indices, pred)

DIRS = [(-1,0),(1,0),(0,-1),(0,1)]
def build(iters):
    x = rasp.categorical(rasp.Map(lambda t: {'.':0,'x':1,'o':2}.get(t, 3), rasp.tokens))
    for it in range(iters):
        nb = [rasp.categorical(rasp.Aggregate(nbr_sel(dr, dc), x)) for dr, dc in DIRS]
        a = rasp.categorical(rasp.SequenceMap(lambda u, v: (u * 5 + v) % 30, nb[0], nb[1]))
        b = rasp.categorical(rasp.SequenceMap(lambda u, v: (u * 3 + v) % 30, nb[2], nb[3]))
        x = rasp.categorical(rasp.SequenceMap(lambda u, v: (u + 2 * v) % 30, a, b))
    return rasp.numerical(rasp.Map(lambda v: v / 30, x))

for iters in [1, 2]:
    signal.alarm(300)
    t = time.time()
    pr = cProfile.Profile()
    pr.enable()
    try:
        m = compiling.compile_rasp_to_model(build(iters), vocab={".", "x", "o", "B", "W"}, max_seq_len=82, compiler_bos="BOS", mlp_exactness=100)
        print(iters, 'ok', time.time() - t, m.model_config, len(m.residual_labels))
    except TimeoutError:
        print(iters, 'timeout', time.time() - t)
    pr.disable()
    signal.alarm(0)
    s = io.StringIO()
    pstats.Stats(pr, stream=s).sort_stats('cumulative').print_stats(25)
    print(s.getvalue()[:5000])
```