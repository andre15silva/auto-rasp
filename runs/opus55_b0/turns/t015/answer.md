```python
code = r'''
import math
from tracr.rasp import rasp

KS = 84
LSC = 100.0 / math.sqrt(KS)
N = 81
PASSI = 81

def nbrs(s):
    if s >= N: return []
    r, c = divmod(s, 9); out = []
    if r > 0: out.append(s - 9)
    if r < 8: out.append(s + 9)
    if c > 0: out.append(s - 1)
    if c < 8: out.append(s + 1)
    return out
NB = [set(nbrs(s)) for s in range(82)]

def P_selfw(k, q):
    if q == PASSI: return 2.0 if k == PASSI else -2.0
    if k == q: return 2.0 + math.log(20.0) / LSC
    if k in NB[q]: return 2.0
    return -2.0

def P_open_proxy(k, q):
    if q == PASSI: return 2.0 if k == PASSI else -2.0
    if k in NB[q]: return 2.0
    if k == PASSI:
        d = len(NB[q])
        return 2.0 + math.log(4 - d) / LSC if d < 4 else -2.0
    return -2.0

def P_argmin(k, q):
    t, v = k, q
    if v == PASSI: return 75.0 if t == PASSI else -5.0
    if t == PASSI: return -75.0
    if t == v: return 70.0
    if t > v: return -3000.0
    return 0.0

def P_group(k, q):
    if q == PASSI: return 2.0 if k == PASSI else -2.0
    return 2.0 if k == q else -2.0

def P_atari(k, q):
    t, v = k, q
    if t == PASSI: return 2.0
    if v == PASSI: return 0.0
    if v == t: return 1000.0
    return -8000.0
'''
open('/work/gocore.py','w').write(code)
print(open('/work/gocore.py').read()[:120])
```