```python
src = open('/work/program.py').read()
src = src.replace("TAC_CAP1, TAC_CAP2, TAC_EYE, TAC_SA, TAC_ESC, TAC_ATK, TAC_DEF = 20, 26, -25, -20, 14, 5, 6",
                  "TAC_CAP1, TAC_CAP2, TAC_EYE, TAC_SA, TAC_ESC, TAC_ATK, TAC_DEF = 20, 26, -25, -20, 14, 2, 3")
src = src.replace("SCALE = 2.0", "SCALE = 3.0")
src = src.replace("{'neu': 1.0, 'opp': 0.5, 'own': 0.15}", "{'neu': 1.0, 'opp': 0.5, 'own': 0.35}")
open('/work/program.py','w').write(src)
import sys; sys.path.insert(0,'/work')
import importlib, program
importlib.reload(program)
res = compile_program()
```