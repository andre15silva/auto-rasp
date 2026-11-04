27 layers, MLP width 416, ≤4 heads. Compile:

```python
import sys; sys.path.insert(0,'/work')
r = compile_program()
print({k:v for k,v in r.items() if k not in ('residual_labels',)})
```