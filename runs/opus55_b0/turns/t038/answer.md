```python
s = open('/work/prog_v4.py').read()
# drop o-side 2-lib chain
for line in ['    M1o = rasp.Aggregate(rasp.Select(idx, GLo, P_minlib), idx)\n',
             '    M1oc = rasp.SequenceMap(lambda m, b: m, M1o, ise)\n',
             '    I1o = rasp.Aggregate(rasp.Select(M1oc, idx, P_eqm), vYo)\n',
             '    Ie2o = rasp.SequenceMap(fe2, Ie, I1o)\n',
             '    E2o = rasp.Aggregate(sel_open, Ie2o)\n',
             '    GL2o = rasp.Aggregate(rasp.Select(Ko, Lo, P_group2), E2o)\n',
             '    T2o = rasp.Aggregate(rasp.Select(idx, GL2o, P_atari), tvo)\n',
             '    T2xo = rasp.SequenceMap(lambda a, b: "x2" if a == "x2" else ("o2" if b == "o2" else "n"), T2x, T2o)\n']:
    assert line in s, line
    s = s.replace(line, '')
s = s.replace('''        if s == "oS": return "o2" if t == "o2" else "o3"''', '''        if s == "oS": return "o3"''')
s = s.replace("st = rasp.SequenceMap(f3, st2b, T2xo)", "st = rasp.SequenceMap(f3, st2b, T2x)")
open('/work/prog_v6.py','w').write(s)

t = open('/work/gotmpl.py').read()
t = t.replace('''  "A": {"o1s": "o1s", "o1b": "o1b", "o2": "o2", "x1s": "x1s"},''', '''  "A": {"o1s": "o1s", "o1b": "o1b", "x1s": "x1s"},''')
t = t.replace('''GNAMES = {"A": ["o1s", "o1b", "o2", "x1s", "r"],''', '''GNAMES = {"A": ["o1s", "o1b", "x1s", "r"],''')
t = t.replace('''    elif c["o2"] >= 1: s += 3.0 + 1.0 * (c["o2"] - 1)\n''', '')
t = t.replace('''"C": {"e": "e", "o1s": "o", "o1b": "o", "o2": "o", "o3": "o",''', '''"C": {"e": "e", "o1s": "o", "o1b": "o", "o3": "o",''')
open('/work/gotmpl6.py','w').write(t)
s = s.replace("from gotmpl import *", "from gotmpl6 import *")
open('/work/prog_v6.py','w').write(s)
import sys; sys.path.insert(0,'/work')
import importlib, gotmpl6; importlib.reload(gotmpl6)
print({h: len(gotmpl6.CFG[h]) for h in "ABC"}, gotmpl6.GNAMES["A"], gotmpl6.GROUPS["C"])
res = compile_program('/work/prog_v6.py')
print({k: v for k, v in res.items() if k != 'residual_labels'})
```