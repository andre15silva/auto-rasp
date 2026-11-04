That speed reading (295 s/1000) is alarming. Let me re-run the compile to see whether it's measurement noise or something structural (e.g., denormals).

```python
import sys; sys.path.insert(0,'/work')
r = compile_program()
print({k:v for k,v in r.items() if k not in ('residual_labels',)})
```