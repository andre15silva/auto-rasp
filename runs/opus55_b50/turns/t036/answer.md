Toys with 188M dense params run in ~8 s, so their implementation clearly exploits structure; my programs are anomalous per parameter. Let me isolate the run-id (graded argmax) head on its own.

```python
toy3 = r'''
from tracr.rasp import rasp
MLP_EXACTNESS = 1000
MODE = {mode!r}
SEL = 10.6
def program():
    tok, idx = rasp.tokens, rasp.indices
    COL = {{'.': 'E', 'x': 'X', 'o': 'O', 'B': 'S', 'W': 'S'}}
    color = rasp.categorical(rasp.Map(lambda t: COL[t], tok))
    def sh(k, q):
        if q == 81: return SEL if k == 81 else 0
        r, c = divmod(q, 9)
        t = q - 1 if c > 0 else 81
        return SEL if k == t else 0
    ncW = rasp.categorical(rasp.Aggregate(rasp.Select(idx, idx, sh), color))
    hsb = rasp.categorical(rasp.SequenceMap(lambda w, c: True if c == 'S' else (w != c), ncW, color))
    hkey = rasp.categorical(rasp.SequenceMap(lambda b, i: i if b else 'no', hsb, idx))
    if MODE == 'graded':
        def ph(k, q):
            if k == 'no': return 0
            if q == 81 or k == 81: return 92.2 if (q == 81 and k == 81) else 0
            if k // 9 == q // 9 and k <= q: return 92.2 - 10.2 * (q - k)
            return 0
    else:
        def ph(k, q):
            return SEL if k == q else 0
    hrun = rasp.categorical(rasp.Aggregate(rasp.Select(hkey, idx, ph), idx))
    out = rasp.numerical(rasp.Map(lambda v: 1 if v == 3 else 0, hrun))
    for i in range(10):
        out = rasp.numerical(rasp.LinearSequenceMap(out, out, 1, 0))
    return out
'''
for mode in ['graded', 'fixed', 'graded', 'fixed']:
    open('/work/program.py','w').write(toy3.format(mode=mode))
    print(mode, end=' '); r = compile_program()
```