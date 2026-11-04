```python
import os, tracr, inspect
base = os.path.dirname(tracr.__file__)
print(inspect.getsource(compile_program) if 'compile_program' in globals() else 'no')
```