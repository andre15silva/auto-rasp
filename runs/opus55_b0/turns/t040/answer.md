```python
res = compile_program('/work/prog_v6.py')
print({k: v for k, v in res.items() if k in ('dense_params','compile_seconds','seconds_per_1000_positions')})
import collections
cnt = collections.Counter(l.split(':')[0] for l in res['residual_labels'])
print(sorted(cnt.items(), key=lambda kv: -kv[1])[:45])
```