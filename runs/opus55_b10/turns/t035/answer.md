```python
import json
d = json.load(open('/work/pass2_positions.json'))
print(json.dumps({"positions": d['positions'], "activations": True, "rasp": False}, separators=(',',':')))
```