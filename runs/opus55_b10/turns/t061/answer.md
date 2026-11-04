```python
s = open('/work/go.py').read()
first_end = 6773
tail_start = s.index("TRIPLE_CLASS, TRIPLE_REP = build_triple_classes()")
print(repr(s[8220:tail_start][-200:]))
s2 = s[:first_end] + s[tail_start:]
open('/work/go.py','w').write(s2)
import re
for m in re.finditer(r'^(def |[A-Z_]+ =|TRIPLE)', s2, flags=re.M):
    print(m.start(), s2[m.start():m.start()+40].split('\n')[0])
import sys, importlib; sys.path.insert(0,'/work')
import go; importlib.reload(go)
print(go.pos_score(1,0,1,0,2), go.pos_score(0,0,0,0,4), go.pos_score(0,0,0,0,0), len(go.TRIPLE_REP))
```