```python
res = compile_program('/work/prog_v4.py')
print({k: v for k, v in res.items() if k in ('layers','heads','residual_dims','dense_params','seconds_per_1000_positions','compile_seconds')})
```