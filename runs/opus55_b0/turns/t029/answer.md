```python
s = open('/work/gotmpl.py').read()
s = s.replace('''  "A": {"o1s": "o1s", "o1b": "o1b", "o2": "o2", "x1b": "x1b"},
  "B": {"e": "e", "x1s": "x1", "x1b": "x1", "x2": "x2", "x3": "x3"},''',
'''  "A": {"o1s": "o1s", "o1b": "o1b", "o2": "o2", "x1s": "x1s"},
  "B": {"e": "e", "x1b": "x1b", "x2": "x2", "x3": "x3"},''')
s = s.replace('''GNAMES = {"A": ["o1s", "o1b", "o2", "x1b", "r"], "B": ["e", "x1", "x2", "x3", "r"],''',
              '''GNAMES = {"A": ["o1s", "o1b", "o2", "x1s", "r"], "B": ["e", "x1b", "x2", "x3", "r"],''')
s = s.replace('''    if c["x1b"] >= 1: s += 20.0
    return s''', '''    if c["x1s"] >= 1: s += 8.0 + 2.0 * (c["x1s"] - 1)
    return s''')
i = s.index('def scoreB'); j = s.index('def scoreC')
s = s[:i] + '''def scoreB(c):
    e, xb, x2, x3 = c["e"], c["x1b"], c["x2"], c["x3"]
    if c["r"] == 4: return -12.0
    safe = x3 >= 1 or e >= 2
    if safe:
        s = 0.0
        if xb >= 1: s += 30.0 if (e >= 3 or x3 >= 1) else 24.0
        if x2 >= 1 and e >= 2: s += 2.0
        return s
    if xb >= 1: return -14.0
    if e == 1: return -6.0 if x2 >= 1 else -12.0
    return -6.0 if x2 >= 2 else -12.0

''' + s[j:]
open('/work/gotmpl.py','w').write(s)
import sys; sys.path.insert(0,'/work')
import importlib, gotmpl; importlib.reload(gotmpl)
g = gotmpl
print({h: len(g.CFG[h]) for h in "ABC"}, g.GNAMES)
for c in [dict(e=3,x1b=1,x2=0,x3=0,r=0), dict(e=1,x1b=1,x2=0,x3=0,r=2), dict(e=0,x1b=0,x2=1,x3=0,r=3), dict(e=0,x1b=0,x2=0,x3=0,r=4)]:
    print(c, g.scoreB(c))
print(g.scoreA(dict(o1s=1,o1b=0,o2=0,x1s=1,r=2)), g.scoreC(dict(e=0,o=0,x=4,edge=0)), g.scoreC(dict(e=0,o=0,x=0,edge=4)))
```