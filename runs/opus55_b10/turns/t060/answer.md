```python
s = open('/work/go.py').read()
import re
for m in re.finditer(r'^(def |[A-Z_]+ =)', s, flags=re.M):
    print(m.start(), s[m.start():m.start()+40].split('\n')[0])
```