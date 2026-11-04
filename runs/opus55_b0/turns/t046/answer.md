```python
s = open('/work/prog_v7.py').read()
s = s.replace('''    zz = rasp.Map(lambda l: 0, Lx)
    clso_late = rasp.SequenceMap(lambda c, z: c, clso, zz)
    Ko = rasp.SequenceMap(fk, Lo, clso_late)''', '''    Lo_late = rasp.Map(lambda l: l, Lo)
    Ko = rasp.SequenceMap(fk, Lo_late, clso)''')
open('/work/prog_v7.py','w').write(s)
import sys; sys.path.insert(0,'/work')
import report, importlib; importlib.reload(report)
r = report.layer_report('prog_v7')
```