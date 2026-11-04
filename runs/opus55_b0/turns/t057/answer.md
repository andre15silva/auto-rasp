```python
import shutil
shutil.copy('/work/prog_v10.py', '/work/program.py')
res = compile_program()
print({k: v for k, v in res.items() if k in ('layers','dense_params','seconds_per_1000_positions','output_label')})
```