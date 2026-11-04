```python
import shutil
s = open('/work/prog_v8.py').read()
open('/work/prog_v9.py','w').write(s)
res = compile_program('/work/prog_v9.py')
print({k: v for k, v in res.items() if k != 'residual_labels'})
```