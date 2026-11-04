Still slow (182 s) despite being smaller than a fast toy, so something numerical (likely denormals) is happening. Let me bisect by compiling truncated versions of the program.

```python
s = open('/work/gonet.py').read()
s = s.replace('def build():', 'def build(stop=None):')
s = s.replace("    # ---- runs\n", "    if stop == 'init': return flags[0]\n    # ---- runs\n")
s = s.replace("    # ---- propagation\n", "    if stop == 'runs':\n        return rasp.numerical(rasp.Map(lambda v: 0.0 if v == 'no' else 1.0, rasp.categorical(rasp.SequenceMap(lambda a, b: a, hkey, hrun))))\n    # ---- propagation\n")
s = s.replace("    R, C, TXc, TOc = flags[:9], flags[9:18], flags[18], flags[19]\n", "    R, C, TXc, TOc = flags[:9], flags[9:18], flags[18], flags[19]\n    if stop == 'prop': return flags[0]\n")
s = s.replace("    nbs = {d: shift(nbinfo", "    if stop == 'nbinfo': return rasp.numerical(rasp.Map(lambda v: 1.0 if v == 'E' else 0.0, nbinfo))\n    nbs = {d: shift(nbinfo")
open('/work/gonet.py','w').write(s)
for stop in ['init', 'runs', 'prop']:
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