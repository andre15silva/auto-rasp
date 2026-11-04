```python
from tracr.compiler import craft_graph_to_model
import inspect, re
def src(obj, maxlen=None):
    s = inspect.getsource(obj)
    s = re.sub(r'\n\s*"""[\s\S]*?"""', '', s, count=1)
    s = '\n'.join(l for l in s.split('\n') if not l.strip().startswith('#'))
    print(s[:maxlen] if maxlen else s)
src(craft_graph_to_model)
```