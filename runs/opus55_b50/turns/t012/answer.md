```python
toy = r'''
from tracr.rasp import rasp
MLP_EXACTNESS = 100
def program():
    t = rasp.tokens
    idx = rasp.indices
    a = idx
    outs = []
    cur = rasp.categorical(rasp.Map(lambda v: v, idx))
    for i in range(4):
        cur = rasp.categorical(rasp.SequenceMap(lambda x, y: (x + y) % 82, cur, idx))
        sel = rasp.Select(idx, idx, rasp.Comparison.EQ)
        cur = rasp.categorical(rasp.Aggregate(sel, cur))
    out = rasp.numerical(rasp.Map(lambda v: v/100, cur))
    return out
'''
open('/work/program.py','w').write(toy)
r = compile_program()
```