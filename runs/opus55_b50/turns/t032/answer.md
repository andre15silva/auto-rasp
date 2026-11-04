Measurements are noisy, but one remaining tiny-value source is clear: at the BOS row, garbage query components times large negative UNSEL scores give weights like e^-33. Since every real query in my heads always selects at least one key, I can set UNSEL = 0. Let me check the full model.

```python
open('/work/program.py','w').write('''
import sys
sys.path.insert(0, '/work')
import importlib, gonet
importlib.reload(gonet)
gonet.UNSEL = 0.0
MLP_EXACTNESS = 1000
def program():
    return gonet.build()
''')
r = compile_program()
```