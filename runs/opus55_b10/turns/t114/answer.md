Max 2 heads per layer now. Compile:

```python
import sys; sys.path.insert(0,'/work')
r = compile_program()
print({k:v for k,v in r.items() if k not in ('residual_labels',)})
```