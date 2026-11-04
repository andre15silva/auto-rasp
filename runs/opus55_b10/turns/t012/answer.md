```python
s = open('/work/go.py').read()
s = s.replace("""    tact = num(smap(tfin, b1, b2))""", """    tcat = smap(lambda b, c: tfin(b, c) + T_OFF, b1, b2)
    tact = nmap(lambda v: v, tcat)""")
s = s.replace("""    pos = num(smap(pfin, e2, adjl))""", """    pcat = smap(lambda e, a: pfin(e, a) + P_OFF, e2, adjl)
    pos = nmap(lambda v: v, pcat)""")
s = s.replace("PASS_LOGIT = -2.0", "PASS_LOGIT = -2.0\nT_OFF = 40.0\nP_OFF = 10.0")
open('/work/go.py','w').write(s)
r = compile_program()
print({k:v for k,v in r.items() if k!='residual_labels'})
import collections
labs = r['residual_labels']
c = collections.Counter(l.split(':')[0] for l in labs)
print(len(c), c.most_common(40))
```