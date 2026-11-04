28 layers, ≤3 heads, MLP 457. Compile and measure:

```python
import sys; sys.path.insert(0,'/work')
r = compile_program()
print({k:v for k,v in r.items() if k not in ('residual_labels',)})
```