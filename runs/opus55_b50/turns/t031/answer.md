Time is dominated by something in the run-id computation, not the propagation. Let me isolate: keep the run-id heads in the graph but propagate with fixed selectors, and vice versa.

```python
s = open('/work/gonet.py').read()
s = s.replace("    if stop == 'prop': return flags[0]\n",
"""    if stop == 'prop': return flags[0]
    if stop == 'prop+h':
        hx = rasp.numerical(rasp.Map(lambda v: 1 if v == 3 else 0, hrun))
        return lsm(flags[0], hx, 'dbg')
""")
# lsm is defined later; move a copy of lsm def up
s = s.replace("    # ---- propagation\n", "    def lsm(a, b, name): return rasp.numerical(rasp.LinearSequenceMap(a, b, 1, 1)).named(name)\n    # ---- propagation\n", 1)
open('/work/gonet.py','w').write(s)
variants = [(dict(FIXSEL=True, N_PROP=2), 'prop+h'), (dict(FIXSEL=True, N_PROP=2), 'prop'), (dict(N_PROP=2), 'prop'), (dict(N_PROP=0), 'prop+h')]
for v, stop in variants:
    hdr = '\n'.join(f'gonet.{k} = {val}' for k, val in v.items())
    open('/work/program.py','w').write(f'''
import sys
sys.path.insert(0, '/work')
import importlib, gonet
importlib.reload(gonet)
{hdr}
MLP_EXACTNESS = 1000
def program():
    return gonet.build(stop={stop!r})
''')
    print(v, stop); r = compile_program()
```