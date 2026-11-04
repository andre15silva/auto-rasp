Huge logits don't affect timing. Let me isolate further within `prop`: replace the pattern-based initial flags with trivial token maps (keeping run ids + EQ propagation).

```python
s = open('/work/gonet.py').read()
s = s.replace("    if stop == 'init': return flags[0]\n", "    if stop == 'init': return flags[0]\n    if TRIVIAL_FLAGS:\n        flags = [rasp.numerical(rasp.Map(lambda t, j=j: 1 if (t == '.' and j % 2 == 0) else 0, tok)).named(f'tf{j}') for j in range(20)]\n")
s = s.replace("FIXSEL = False\n", "FIXSEL = False\nTRIVIAL_FLAGS = False\n")
open('/work/gonet.py','w').write(s)
variants = [dict(TRIVIAL_FLAGS=True), dict(), dict(TRIVIAL_FLAGS=True), dict()]
for v in variants:
    hdr = '\n'.join(f'gonet.{k} = {val}' for k, val in v.items())
    open('/work/program.py','w').write(f'''
import sys
sys.path.insert(0, '/work')
import importlib, gonet
importlib.reload(gonet)
gonet.UNSEL = 0.0
{hdr}
MLP_EXACTNESS = 1000
def program():
    return gonet.build(stop='prop')
''')
    print(v, end=' '); r = compile_program()
```