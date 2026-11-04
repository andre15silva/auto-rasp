```python
src = open('/work/program.py').read()
# ownership / ahead estimate
src = src.replace("    passv = num(", """    def fown(z, t):
        if t in ('B', 'W'): return t
        if z in ('SX', 'own'): return '+'
        if z in ('SO', 'opp'): return '-'
        return '0'
    ownv = cat(rasp.SequenceMap(fown, zoneP, tok)).named('ownv')
    glob = cat(rasp.Aggregate(mksel(idx, idx, lambda k, q: True), ownv)).named('glob')
    def pred_ahead(k, q):
        if k == 0:
            return 0.6 + CA * {'+': 82.0, '-': -82.0, 'B': -KOMI * 82.0, 'W': KOMI * 82.0}.get(q, 0.0)
        if k == 1: return 0.6
        return None
    aheadO = cat(rasp.Aggregate(mksel(idx, glob, pred_ahead), ynmap)).named('aheadO')
    passv = num(""")
src = src.replace("    tacP = num(rasp.Map(lambda s: float(max(s, 0)), tab2)).named('tacP')",
"""    kot = cat(rasp.SequenceMap(lambda s, a: 'kb' if (s == TAC_KO and a == 'no') else 'n', tab2, aheadO)).named('kot')
    kotR = num(rasp.Map(lambda v: KO_BEHIND if v == 'kb' else 0.0, kot)).named('kotR')
    tacP = num(rasp.Map(lambda s: float(max(s, 0)), tab2)).named('tacP')""")
src = src.replace("    b0 = num(rasp.LinearSequenceMap(b00, contR, 1.0, 1.0)).named('b0')",
                  "    b01 = num(rasp.LinearSequenceMap(b00, contR, 1.0, 1.0)).named('b01')\n    b0 = num(rasp.LinearSequenceMap(b01, kotR, 1.0, 1.0)).named('b0')")
src = src.replace("TAC_KO = -15", "TAC_KO = -15\nKO_BEHIND = 22.0\nCA = 0.3\nKOMI = 7.5")
open('/work/program.py','w').write(src)
import sys; sys.path.insert(0,'/work')
import importlib, program, helper2
importlib.reload(program)
res = compile_program()
```