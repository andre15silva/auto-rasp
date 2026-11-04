Path cost 2.6e7 (v3 was 1.7e7). Compile and measure:

```python
import time
t0 = time.time()
r = compile_program(); print('wall', round(time.time()-t0))
```