```python
import inspect
from tracr.craft.chamber import numerical_mlp, categorical_mlp, categorical_attn
def src(obj):
    s = inspect.getsource(obj)
    import re
    s = re.sub(r'\n\s*"""[\s\S]*?"""', '', s, count=1)
    s = '\n'.join(l for l in s.split('\n') if not l.strip().startswith('#'))
    print(s)
src(numerical_mlp._get_discretising_layer)
src(numerical_mlp.map_numerical_mlp)
src(numerical_mlp.map_numerical_to_categorical_mlp)
src(categorical_mlp)
```