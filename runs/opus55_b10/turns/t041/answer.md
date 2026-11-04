```python
import sys; sys.path.insert(0,'/work')
r = compile_program()
print({k:v for k,v in r.items() if k!='residual_labels'})
```