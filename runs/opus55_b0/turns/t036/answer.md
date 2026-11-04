```python
res = compile_program('/work/prog_v1.py')
print({k: v for k, v in res.items() if k in ('dense_params','nonzero_params','compile_seconds','seconds_per_1000_positions')})
```