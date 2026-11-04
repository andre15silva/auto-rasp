```python
src = open('/work/program.py').read()
blk = """    kot = cat(rasp.SequenceMap(lambda s, a: 'kb' if (s == TAC_KO and a == 'no') else 'n', tab2, aheadO)).named('kot')
    kotR = num(rasp.Map(lambda v: KO_BEHIND if v == 'kb' else 0.0, kot)).named('kotR')
"""
src = src.replace(blk, "")
src = src.replace("    a1 = num(rasp.LinearSequenceMap(tacP, tacN, 1.0, -1.0)).named('a1')", blk + "    a1 = num(rasp.LinearSequenceMap(tacP, tacN, 1.0, -1.0)).named('a1')")
open('/work/program.py','w').write(src)
import sys; sys.path.insert(0,'/work')
import importlib, program, helper2
importlib.reload(program)
helper2.layer_report(program.program)
res = compile_program()
```