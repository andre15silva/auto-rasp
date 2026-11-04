Compile time is manageable but grows with block count × D. Let me compile the full v4 to check time and speed.

```python
import time
t0 = time.time()
r = compile_program(); print('wall', round(time.time()-t0))
```