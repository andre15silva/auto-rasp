`rasp.Map` fuses consecutive Maps by default, merging my threshold into the extraction. Need `simplify=False`.

```python
s = open('/work/gonet.py').read()
s = s.replace("flags.append(rasp.numerical(rasp.Map(gthr, xh)).named(f'f{h}'))", "flags.append(rasp.numerical(rasp.Map(gthr, xh, simplify=False)).named(f'f{h}'))")
open('/work/gonet.py','w').write(s)
import time; t0 = time.time()
r = compile_program(); print('wall', round(time.time()-t0))
```