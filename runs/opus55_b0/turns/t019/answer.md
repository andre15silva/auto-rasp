```python
s = open('/work/prog_v2.py').read()
s = s.replace("""    I1x = rasp.Aggregate(rasp.Select(M1x, idx, P_eqm), vYx)
    I1o = rasp.Aggregate(rasp.Select(M1o, idx, P_eqm), vYo)""",
"""    M1xc = rasp.SequenceMap(lambda m, b: m, M1x, ise)
    M1oc = rasp.SequenceMap(lambda m, b: m, M1o, ise)
    I1x = rasp.Aggregate(rasp.Select(M1xc, idx, P_eqm), vYx)
    I1o = rasp.Aggregate(rasp.Select(M1oc, idx, P_eqm), vYo)""")
open('/work/prog_v2.py','w').write(s)
res = compile_program('/work/prog_v2.py')
print({k: v for k, v in res.items() if k != 'residual_labels'})
```