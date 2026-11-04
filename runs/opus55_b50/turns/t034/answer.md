Same model: 10.4 / 11.5 / 8.4 s, versus 4.6 s earlier — the machine is noisy, but this 16M-param model is still much slower than numerically "clean" toys. My leading hypothesis: their NumPy forward pass runs in float64, where my gaps of ~110 logits leave weights like e^-110…e^-660 that are tiny but non-zero and later underflow when multiplied. Let me compare variants interleaved (A/B/C/A).

```python
variants = [
 ('A_current', dict(SEL=10.6, UNSEL=0.0, GTOP=92.2, GSTEP=10.2)),
 ('B_moderate', dict(SEL=5.0, UNSEL=0.0, GTOP=6.9, GSTEP=0.7)),
 ('C_huge', dict(SEL=70.0, UNSEL=0.0, GTOP=70.0+72*8, GSTEP=72.0)),
 ('A_current', dict(SEL=10.6, UNSEL=0.0, GTOP=92.2, GSTEP=10.2)),
 ('C_huge', dict(SEL=70.0, UNSEL=0.0, GTOP=70.0+72*8, GSTEP=72.0)),
]
for nm, v in variants:
    hdr = '\n'.join(f'gonet.{k} = {val}' for k, val in v.items())
    open('/work/program.py','w').write(f'''
import sys
sys.path.insert(0, '/work')
import importlib, gonet
importlib.reload(gonet)
{hdr}
MLP_EXACTNESS = 1000
def program():
    return gonet.build(stop='prop')
''')
    print(nm, end=' '); r = compile_program()
```