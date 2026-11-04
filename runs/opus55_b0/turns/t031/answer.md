```python
import shutil
shutil.copy('/work/prog_v4.py', '/work/program.py')
print(open('/work/program.py').read()[:60])
```