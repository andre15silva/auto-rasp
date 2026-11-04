```python
from tracr.compiler import assemble, craft_model_to_transformer, craft_graph_to_model
from tracr.craft.chamber import categorical_attn, selector_width
import inspect, re
def src(obj, maxlen=None):
    s = inspect.getsource(obj)
    s = re.sub(r'\n\s*"""[\s\S]*?"""', '', s, count=1)
    s = '\n'.join(l for l in s.split('\n') if not l.strip().startswith('#'))
    print(s[:maxlen] if maxlen else s)
src(categorical_attn.categorical_attn)
src(assemble._make_transformer_parameters if hasattr(assemble,'_make_transformer_parameters') else assemble)
```