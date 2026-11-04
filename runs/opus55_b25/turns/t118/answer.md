```python
import shutil
shutil.copy('/work/program_final_candidate.py', '/work/program.py')
src = open('/work/program.py').read()
print([l for l in src.split('\n') if l.startswith('BIG_CAP') or l.startswith('TAC_CAP1')])
src = src.replace("BIG_CAP, BIG_ESC, BIG_DEF, BIG_ATK = 6, 8, 4, 3", "BIG_CAP, BIG_ESC, BIG_DEF, BIG_ATK = 6, 8, 8, 5")
src = src.replace("TAC_CAP1, TAC_CAP2, TAC_EYE, TAC_SA, TAC_ESC, TAC_ATK, TAC_DEF = 20, 26, -25, -20, 14, 2, 3",
                  "TAC_CAP1, TAC_CAP2, TAC_EYE, TAC_SA, TAC_ESC, TAC_ATK, TAC_DEF = 20, 26, -25, -20, 14, 2, 4")
open('/work/program.py','w').write(src)
print([l for l in src.split('\n') if l.startswith('BIG_CAP') or l.startswith('TAC_CAP1')])
import sys; sys.path.insert(0,'/work')
import importlib, program
importlib.reload(program)
res = compile_program()
```