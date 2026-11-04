```python
import sys, inspect; sys.path.insert(0,'/work')
import importlib, go; importlib.reload(go)
print(inspect.getsource(go.pos_score))
print(go.pos_score(1,0,1,0,2), go.pos_score(0,0,0,0,4), go.pos_score(0,0,0,0,0))
```