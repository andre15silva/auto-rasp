```python
src = open('/work/program.py').read()
# remove zsa machinery
src = src.replace("""    zsa = cat(rasp.SequenceMap(lambda s, z: 'thr' if (s == TAC_SA and z == 'opp') else 'no', tab2, zoneP)).named('zsa')
    zsaR = num(rasp.Map(lambda v: SA_OPP_BONUS if v == 'thr' else 0.0, zsa)).named('zsaR')
""", "")
src = src.replace("""    b00 = num(rasp.LinearSequenceMap(a1, bigR2, 1.0, 1.0)).named('b00')
    b0 = num(rasp.LinearSequenceMap(b00, zsaR, 1.0, 1.0)).named('b0')""", """    b0 = num(rasp.LinearSequenceMap(a1, bigR2, 1.0, 1.0)).named('b0')""")
# coarse triple readout on U
src = src.replace("ZTH, ZC = 0.12, 10.0", '''TRIPLES8 = list(itertools.combinations(range(8), 3))
def pred_utriple(k, q):
    if k < len(TRIPLES8):
        if q == 'n' or q[0] == 'O': return 1.0
        return 1.0 if (q[1] % 8) in TRIPLES8[k] else -BIG
    if k == len(TRIPLES8): return 0.7
    return None

ZTH, ZC = 0.12, 10.0''')
src = src.replace("    rvu = cat(", "    rvu3 = cat(rasp.Map(lambda k: 'lo' if k < len(TRIPLES8) else 'hi', idx)).named('rvu3')\n    rvu = cat(")
src = src.replace("    RU = cat(rasp.Aggregate(mksel(idx, U, pred_upair), rvu)).named('RU')",
"""    RU2_ = cat(rasp.Aggregate(mksel(idx, U, pred_upair), rvu)).named('RU2')
    RU3_ = cat(rasp.Aggregate(mksel(idx, U, pred_utriple), rvu3)).named('RU3')
    RU = cat(rasp.SequenceMap(lambda a, b: 'lo' if a == 'lo' else ('hi' if b == 'hi' else 'mid'), RU2_, RU3_)).named('RU')""")
# labelA nEc up to 3
src = src.replace("    return (min(nO1, 2), int(nX >= 1), int(nX >= 1 and nX + nP == 4), min(nE, 2))",
                  "    return (min(nO1, 2), int(nX >= 1), int(nX >= 1 and nX + nP == 4), min(nE, 3))")
src = src.replace("""        if xn: la = 1 if ru == 'lo' else 2
        else: la = max(1, min(nEc, 2))
        return (la, int(nEc >= 2), xn)""", """        if xn: la = {'lo': 1, 'mid': 2, 'hi': 3}[ru]
        else: la = max(1, min(nEc, 3))
        return (la, int(nEc >= 2), xn)""")
src = src.replace("""        if xn and x3: la = max(la, 2)
        if la <= 1: return TAC_SA
        return TAC_ESC * esc + TAC_ATK * o2 + TAC_DEF * int(x2 and ne2 and not esc)""",
"""        if xn and x3: la = max(la, 2)
        if la <= 1: return TAC_SA
        escv = TAC_ESC if la >= 3 else TAC_ESC_LADDER
        return escv * esc + TAC_ATK * o2 + TAC_DEF * int(x2 and la >= 3 and not esc)""")
src = src.replace("""        if la <= 1: return 0
        return BIG_ESC * escB + BIG_DEF * int(defB and ne2 and not escB) + BIG_ATK * atkB""",
"""        if la <= 1: return 0
        return BIG_ESC * escB * int(la >= 3) + BIG_DEF * int(defB and la >= 3 and not escB) + BIG_ATK * atkB""")
src = src.replace("BIG_CAP, BIG_ESC, BIG_DEF, BIG_ATK = 6, 8, 4, 3", "BIG_CAP, BIG_ESC, BIG_DEF, BIG_ATK = 6, 8, 4, 3\nTAC_ESC_LADDER = 3")
src = src.replace("DANGW = 20.0", "DANGW = 30.0")
src = src.replace("labmap = cat(rasp.Map(lambda k: labelA(PROTOS[k]) if k < len(PROTOS) else (0, 0, 0, 2), idx)).named('labmap')",
                  "labmap = cat(rasp.Map(lambda k: labelA(PROTOS[k]) if k < len(PROTOS) else (0, 0, 0, 3), idx)).named('labmap')")
open('/work/program.py','w').write(src)
import sys; sys.path.insert(0,'/work')
import importlib, program, helper2
importlib.reload(program)
helper2.layer_report(program.program)
res = compile_program()
```