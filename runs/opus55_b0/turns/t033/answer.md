```python
res = compile_program('/work/prog_v5.py')
print({k: v for k, v in res.items() if k != 'residual_labels'})
```