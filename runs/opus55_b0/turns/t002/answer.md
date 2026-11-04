```python
import re
root = os.path.dirname(tracr.__file__)
src = open(root + '/rasp/rasp.py').read()
# print selected parts
i = src.find('class Comparison')
print(src[i:i+2500])
i = src.find('class Select(')
print(src[i:i+1500])
i = src.find('class Aggregate')
print(src[i:i+2500])
```