```python
import shutil
shutil.copy('/work/program.py', '/work/prog_v1.py')
shutil.copy('/work/prog_v3.py', '/work/program.py')
res = compile_program()
print({k: v for k, v in res.items() if k in ('layers','residual_dims','dense_params','seconds_per_1000_positions','compile_seconds')})
```