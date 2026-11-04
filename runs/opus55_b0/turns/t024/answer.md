```python
s = open('/work/gotmpl.py').read()
s = s.replace('''  "A": {"o1": "o1", "o2": "o2", "o3": "o3"},
  "B": {"e": "e", "x1": "x1", "x2": "x2", "x3": "x3"},
  "C": {"e": "e", "o1": "o", "o2": "o", "o3": "o", "x1": "x", "x2": "x", "x3": "x", "edge": "edge"},''',
'''  "A": {"o1s": "o1s", "o1b": "o1b", "o2": "o2", "x1b": "x1b"},
  "B": {"e": "e", "x1s": "x1", "x1b": "x1", "x2": "x2", "x3": "x3"},
  "C": {"e": "e", "o1s": "o", "o1b": "o", "o2": "o", "o3": "o", "x1s": "x", "x1b": "x", "x2": "x", "x3": "x", "edge": "edge"},''')
s = s.replace('''GNAMES = {"A": ["o1", "o2", "o3", "r"],''', '''GNAMES = {"A": ["o1s", "o1b", "o2", "x1b", "r"],''')
s = s.replace('''def scoreA(c):
    if c["o1"] >= 1: return 25.0 + 4.0 * (c["o1"] - 1)
    if c["o2"] >= 1: return 3.0 + 1.0 * (c["o2"] - 1)
    return 0.0''', '''def scoreA(c):
    s = 0.0
    if c["o1b"] >= 1: s += 40.0 + 4.0 * (c["o1b"] + c["o1s"] - 1)
    elif c["o1s"] >= 1: s += 25.0 + 4.0 * (c["o1s"] - 1)
    elif c["o2"] >= 1: s += 3.0 + 1.0 * (c["o2"] - 1)
    if c["x1b"] >= 1: s += 20.0
    return s''')
open('/work/gotmpl.py','w').write(s)
import sys; sys.path.insert(0,'/work')
import importlib, gotmpl; importlib.reload(gotmpl)
print({h: len(gotmpl.CFG[h]) for h in "ABC"})
print(gotmpl.scoreA({"o1s":1,"o1b":0,"o2":0,"x1b":1,"r":2}), gotmpl.scoreA({"o1s":0,"o1b":0,"o2":0,"x1b":0,"r":4}))
```