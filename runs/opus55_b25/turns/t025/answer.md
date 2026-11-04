```python
import inspect, re
from tracr.transformer import attention, model
s = inspect.getsource(attention)
i = s.find('def __call__')
print(s[i:i+3000])
```