```python
s = open('/work/prog_v2.py').read()
s = s.replace("from gotmpl import *", "from gotmpl import *\nfrom gowin import *")
s = s.replace("    for k in range(2):", "    for k in range(3):")
s = s.replace("""    Pn = rasp.numerical(rasp.Map(lambda i: (prior(i) + 2.0) * SCALE, idx))""",
"""    histw = rasp.Aggregate(rasp.Select(idx, idx, P_win), tok)
    tcW = rasp.Map(tlevelW, idx)
    TW = rasp.Aggregate(rasp.Select(idx, histw, P_tW), tcW)
    Pn = rasp.numerical(rasp.Map(lambda c: (c + OFF) * SCALE, TW))""")
open('/work/prog_v3.py','w').write(s)
res = compile_program('/work/prog_v3.py')
print({k: v for k, v in res.items() if k != 'residual_labels'})
```