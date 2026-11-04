```python
t = open('/work/gotmpl6.py').read()
t = t.replace('''  "C": {"e": "e", "o1s": "o", "o1b": "o", "o3": "o", "x1s": "x", "x1b": "x", "x2": "x", "x3": "x", "edge": "edge"},''',
              '''  "C": {"e": "e", "o1s": "o", "o1b": "o", "o3": "o", "x1s": "xa", "x1b": "xa", "x2": "xn", "x3": "xn", "edge": "edge"},''')
t = t.replace('''"C": ["e", "o", "x", "edge"]}''', '''"C": ["e", "o", "xa", "xn", "edge"]}''')
i = t.index('def scoreC'); j = t.index('SCOREF =')
t = t[:i] + '''def scoreC(c):
    e, o, xa, xn, ed = c["e"], c["o"], c["xa"], c["xn"], c["edge"]
    if ed == 4: return 7.0   # pass: total = A0 + B(-12) + 7 = -5
    if o == 0 and e == 0 and xa == 0: return -40.0
    if o == 0 and e == 1 and xa == 0: return -7.0
    return 1.0 if (o >= 1 and e >= 2) else 0.0

''' + t[j:]
open('/work/gotmpl6.py','w').write(t)
import sys; sys.path.insert(0,'/work')
import importlib, gotmpl6; importlib.reload(gotmpl6)
g = gotmpl6
print({h: len(g.CFG[h]) for h in "ABC"})
print(g.scoreC(dict(e=0,o=0,xa=0,xn=4,edge=0)), g.scoreC(dict(e=0,o=0,xa=1,xn=3,edge=0)), g.scoreC(dict(e=0,o=0,xa=0,xn=0,edge=4)), g.scoreC(dict(e=2,o=1,xa=0,xn=1,edge=0)))
```