```python
src = open('/work/program.py').read()
src = src.replace("    return (min(nO1, 2), int(nX >= 1), int(nX >= 1 and nX + nP == 4), min(nE, 3))",
                  "    return (min(nO1, 2), int(nX >= 1), int(nX >= 1 and nX + nP == 4), min(nE, 3), int(nO1 + nOm >= 1))")
src = src.replace("else (0, 0, 0, 3), idx)).named('labmap')", "else (0, 0, 0, 3, 0), idx)).named('labmap')")
src = src.replace("""    def ftab1(lab, ru):
        capc, xn, eye, nEc = lab""", """    def ftab1(lab, ru):
        capc, xn, eye, nEc, on = lab""")
src = src.replace("    tab1 = cat(rasp.SequenceMap(ftab1, labA, RU)).named('tab1')",
"""    tab1 = cat(rasp.SequenceMap(ftab1, labA, RU)).named('tab1')
    def fcontact(lab, ru):
        capc, xn, eye, nEc, on = lab
        if capc or eye or not on: return 0
        if xn: la = {'lo': 1, 'mid': 2, 'hi': 3}[ru]
        else: la = min(nEc, 3)
        return CONTACT if la >= 3 else 0
    contact = cat(rasp.SequenceMap(fcontact, labA, RU)).named('contact')
    contR = num(rasp.Map(lambda v: float(v), contact)).named('contR')""")
src = src.replace("    b0 = num(rasp.LinearSequenceMap(a1, bigR2, 1.0, 1.0)).named('b0')",
                  "    b00 = num(rasp.LinearSequenceMap(a1, bigR2, 1.0, 1.0)).named('b00')\n    b0 = num(rasp.LinearSequenceMap(b00, contR, 1.0, 1.0)).named('b0')")
src = src.replace("DANGW = 30.0", "DANGW = 20.0\nCONTACT = 3")
open('/work/program.py','w').write(src)
import sys; sys.path.insert(0,'/work')
import importlib, program
importlib.reload(program)
res = compile_program()
```