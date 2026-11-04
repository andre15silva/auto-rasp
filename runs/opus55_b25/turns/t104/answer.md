```python
src = open('/work/program.py').read()
add = r'''
    # ---- eye making / eye stealing ----
    def pred_aeye(col):
        def p(k, q):
            if k == 0:
                if q == col or q == 'P': return 0.1 + 3.2 * 0.5
                if q == 'E': return 0.1 - 3.2 * 0.5
                return 0.1 - 3.2 * 0.5 - 8.0
            if k == 1: return 0.6
            return None
        return p
    aeX = cat(rasp.Aggregate(mksel(idx, KH, pred_aeye('X')), ynmap)).named('aeX')
    aeO = cat(rasp.Aggregate(mksel(idx, KH, pred_aeye('O')), ynmap)).named('aeO')
    aeXk = cat(rasp.SequenceMap(lambda kd, y: 'AE' if (kd == 'E' and y == 'yes') else 'n', kind, aeX)).named('aeXk')
    aeOk = cat(rasp.SequenceMap(lambda kd, y: 'AO' if (kd == 'E' and y == 'yes') else 'n', kind, aeO)).named('aeOk')
    HE = cat(rasp.Aggregate(sel_hist(), aeXk)).named('HE')
    HO = cat(rasp.Aggregate(sel_hist(), aeOk)).named('HO')
    def pred_any(target):
        def p(k, q):
            if k == 0: return (0.1 + 3.2) if q == target else 0.1
            if k == 1: return 0.6
            return None
        return p
    mkE = cat(rasp.Aggregate(mksel(idx, HE, pred_any('AE')), ynmap)).named('mkE')
    stE = cat(rasp.Aggregate(mksel(idx, HO, pred_any('AO')), ynmap)).named('stE')
    eyeT = cat(rasp.SequenceMap(lambda a, b: (a == 'yes', b == 'yes'), mkE, stE)).named('eyeT')
    def feye(e, z):
        mk, st = e
        v = 0.0
        if mk and z in ('neu', 'opp'): v += MKEYE
        if st and z == 'neu': v += STEAL
        return v
    eyeV = cat(rasp.SequenceMap(feye, eyeT, zoneP)).named('eyeV')
    eyeR = num(rasp.Map(lambda v: float(v), eyeV)).named('eyeR')
'''
src = src.replace("    def fown(z, t):", add + "    def fown(z, t):") if "    def fown(z, t):" in src else src.replace("    passv = num(", add + "    passv = num(")
src = src.replace("    d1 = num(rasp.LinearSequenceMap(a2, a3, 1.0, 1.0)).named('d1')",
                  "    d0 = num(rasp.LinearSequenceMap(a2, a3, 1.0, 1.0)).named('d0')\n    d1 = num(rasp.LinearSequenceMap(d0, eyeR, 1.0, 1.0)).named('d1')")
src = src.replace("TAC_KO = -15", "TAC_KO = -15\nMKEYE = 4.0\nSTEAL = 3.0")
open('/work/program.py','w').write(src)
print('eyeR' in src, src.count('MKEYE'))
import sys; sys.path.insert(0,'/work')
import importlib, program, helper2
importlib.reload(program)
res = compile_program()
```