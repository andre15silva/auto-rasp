```python
import shutil, filecmp
shutil.copy('/work/program_final.py', '/work/program.py')
print(filecmp.cmp('/work/program_final.py', '/work/program.py'))
src = open('/work/program.py').read()
for k in ['CONTACT = 4\n', 'ZC = 0.12, 10.0', 'SCALE = 3.0', 'BIG = 1e8', 'FGAIN = 1e6', 'TAC_KO = -15', 'T_HOPS = 6', 'F_HOPS = 4']:
    print(k.strip(), k in src)
import sys; sys.path.insert(0,'/work')
import importlib, program
importlib.reload(program)
res = compile_program()
```