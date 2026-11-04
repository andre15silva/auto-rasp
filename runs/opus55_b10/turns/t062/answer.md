Fixed the duplicated definitions. Let me compile and check the size before the next games pass.

```python
import sys; sys.path.insert(0,'/work'); sys.setrecursionlimit(10000)
import importlib, go, estimate
importlib.reload(go)
print(estimate.estimate(go.program()))
r = compile_program()
print({k:v for k,v in r.items() if k!='residual_labels'})
```