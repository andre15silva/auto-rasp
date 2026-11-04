Diagnosis: the slow model has tiny-but-nonzero residual values (from softmax weights like e^-60 on near-miss keys) that get multiplied together in later q·k products, causing float32 underflow/denormal slowdowns. Fix: make every attention either sharply exact (logit gaps ≥ ~110 so the losing weights underflow to exactly 0) or aggregate only values that are exactly zero where weights are tiny.

```python
s = open('/work/gonet.py').read()
s = s.replace("SEL, UNSEL = 5.0, -5.0\nGTOP, GSTEP = 6.9, 0.7", "SEL, UNSEL = 10.6, -10.0\nGTOP, GSTEP = 10.6 + 10.2 * 8, 10.2")
open('/work/gonet.py','w').write(s)
for stop in ['prop', None]:
    open('/work/program.py','w').write(f'''
import sys
sys.path.insert(0, '/work')
import importlib, gonet
importlib.reload(gonet)
MLP_EXACTNESS = 1000
def program():
    return gonet.build(stop={stop!r})
''')
    print(stop); r = compile_program()
```