```python
src = open('/work/program.py').read()
block = """    zsa = cat(rasp.SequenceMap(lambda s, z: 'thr' if (s == TAC_SA and z == 'opp') else 'no', tab2, zoneP)).named('zsa')
    zsaR = num(rasp.Map(lambda v: SA_OPP_BONUS if v == 'thr' else 0.0, zsa)).named('zsaR')
"""
src = src.replace(block, "")
src = src.replace("    a1 = num(rasp.LinearSequenceMap(tacP, tacN, 1.0, -1.0)).named('a1')", block + "    a1 = num(rasp.LinearSequenceMap(tacP, tacN, 1.0, -1.0)).named('a1')")
open('/work/program.py','w').write(src)
import sys; sys.path.insert(0,'/work')
import importlib, program
importlib.reload(program)
res = compile_program()
```