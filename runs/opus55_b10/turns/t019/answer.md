```python
import sys; sys.path.insert(0,'/work')
open('/work/program.py','w').write("import sys\nsys.path.insert(0, '/work')\nfrom go import program\nMLP_EXACTNESS = 10000000\n")
r = compile_program()
print({k:v for k,v in r.items() if k!='residual_labels'})
import collections
labs = r['residual_labels']
c = collections.Counter(l.split(':')[0] for l in labs)
print(len(c), sorted(c.items(), key=lambda x:-x[1])[:30])
```