```python
prog = r'''
from tracr.rasp import rasp

def program():
    a = rasp.indices
    b = rasp.categorical(rasp.Map(lambda i: (i * 7) % 82, rasp.indices))
    for it in range(6):
        c = rasp.categorical(rasp.SequenceMap(lambda x, y: min(x, y), a, b))
        sel = rasp.Select(rasp.indices, rasp.indices, lambda k, q: k == (q + 1) % 82)
        d = rasp.categorical(rasp.Aggregate(sel, c))
        a, b = c, d
    out = rasp.numerical(rasp.Map(lambda v: v / 82, b))
    return out
'''
open('/work/program.py','w').write(prog)
res = compile_program()
```