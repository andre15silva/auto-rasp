Close losses dominate (~50 per 128 games lost by <10 points). Tweaks are within noise, but passes are plentiful (38) while runs are scarce (10), so I'll evaluate candidate configs with several passes each. Candidate C_new = the pass-9 configuration (best so far) + stronger contact/blocking shape bonuses + 8 propagation steps for more accurate liberties of big groups.

```python
s = open('/work/gonet4.py').read()
# back to pass-9 settings
s = s.replace("PRIOR = {0: [-4.5, -2.2, 1.2, 2.4, 3.0],", "PRIOR = {0: [-3.0, -1.5, 0.8, 1.6, 2.0],")
s = s.replace("'atari': 2.5, 'def2': 3.0}", "'atari': 2.0, 'def2': 2.5}")
s = s.replace("""    if win and nc == 0: return -7.0
    if win and nc == 1: return -7.5
    return -9.0""", """    if win and nc == 0: return -1.0
    if win and nc == 1: return -2.5 if big else -4.0
    return -8.0""")
# new: contact shape boost, 8 propagation steps
s = s.replace("SHAPE = {(1, 0): -0.2, (2, 0): -0.8, (3, 0): -1.5, (0, 1): 0.2, (0, 2): 0.3, (1, 1): 0.5, (2, 1): 0.3, (1, 2): 0.6}",
              "SHAPE = {(1, 0): -0.2, (2, 0): -0.8, (3, 0): -1.5, (0, 1): 0.3, (0, 2): 0.4, (1, 1): 1.2, (2, 1): 0.8, (1, 2): 1.0}")
s = s.replace("N_PROP = 6\n", "N_PROP = 8\n")
s = s.replace("TINY = 1e-5\n", "TINY = 2e-6\n")
open('/work/gonet4.py','w').write(s)
open('/work/program.py','w').write('''
import sys
sys.path.insert(0, '/work')
import importlib, gonet4
importlib.reload(gonet4)
MLP_EXACTNESS = 2000000
def program():
    return gonet4.build()
''')
r = compile_program()
```