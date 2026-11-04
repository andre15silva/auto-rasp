```python
s = open('/work/prog_v7n.py').read()
old = s[s.index('    BIGxo = rasp.SequenceMap'):s.index('    def f3(s, t):')]
new = '''    st3 = rasp.SequenceMap(lambda s, b: (("x1b" if b == "big" else "x1s") if s == "x1" else s), st2, BIGx)
    st4 = rasp.SequenceMap(lambda s, b: (("o1b" if b == "big" else "o1s") if s == "o1" else s), st3, BIGo)
'''
s = s.replace(old, new)
s = s.replace("st = rasp.SequenceMap(f3, st2b, T2x)", "st = rasp.SequenceMap(f3, st4, T2x)")
open('/work/prog_v8.py','w').write(s)
import sys; sys.path.insert(0,'/work')
import report, importlib; importlib.reload(report)
r = report.layer_report('prog_v8')
```