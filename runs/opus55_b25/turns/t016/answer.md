```python
import inspect, re
from tracr.craft.chamber import selector_width
s = inspect.getsource(selector_width)
s = '\n'.join(l for l in s.split('\n') if not l.strip().startswith('#'))
print(s[s.find('def selector_width'):])
```