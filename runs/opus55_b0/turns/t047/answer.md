```python
s = open('/work/prog_v7.py').read()
names = ['Lft','Upt','Lx0','Lo0','Ie','RSx','RSo','E','Kx','Ko','GLx','GLo','AtX0','AtO0','SZx','SZo','BIGx','BIGo','M1x','M1xc','I1x','Ie2x','E2x','GL2x','T2x','st1','st2','BIGxo','st2b','st','hist','histw','TW','Lo_late']
lines = s.split('\n')
out = []
for ln in lines:
    out.append(ln)
    st = ln.strip()
    for nm in names:
        if st.startswith(nm + ' = rasp.'):
            ind = ln[:len(ln) - len(ln.lstrip())]
            out.append(f'{ind}{nm} = {nm}.named("{nm}")')
s2 = '\n'.join(out)
open('/work/prog_v7n.py','w').write(s2)
import sys; sys.path.insert(0,'/work')
import report, importlib; importlib.reload(report)
r = report.layer_report('prog_v7n')
```