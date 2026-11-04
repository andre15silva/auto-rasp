```python
src = open('/work/program.py').read()
# LV offset: board +7, pass 0
src = src.replace("""def LV(i):
    if i >= 81: return 3.0
    r, c = divmod(i, 9)
    e = min(r, c, 8 - r, 8 - c)
    return 3.0 + [-2.0, -0.5, 0.5, 0.7, 1.0][e]""",
"""def LV(i):
    if i >= 81: return 0.0
    r, c = divmod(i, 9)
    e = min(r, c, 8 - r, 8 - c)
    return 10.0 + [-2.0, -0.5, 0.5, 0.7, 1.0][e]""")
# prototypes over HB: (O2, X2, other) counts
src = src.replace("ZTH, ZC = 0.12, 10.0", """PROTOS_B = [t for t in itertools.product(range(5), repeat=3) if sum(t) == 4]
def catB(v): return 'O2' if v == 'O2' else ('X2' if v == 'X2' else 'R')
CATSB = ['O2', 'X2', 'R']
def pred_protoB(k, q):
    if k > len(PROTOS_B): return None
    t = PROTOS_B[k] if k < len(PROTOS_B) else (0, 0, 4)
    m = [x / 4 for x in t]
    sq = sum(x * x for x in m)
    return C1 * (2 * m[CATSB.index(catB(q))] - sq) + 0.5
def labelB(k):
    t = PROTOS_B[k] if k < len(PROTOS_B) else (0, 0, 4)
    return (int(t[0] >= 1), int(t[1] >= 1))

ZTH, ZC = 0.12, 10.0""")
src = src.replace("    ynmap = cat(", "    labBmap = cat(rasp.Map(lambda k: labelB(k) if k <= len(PROTOS_B) else (0, 0), idx)).named('labBmap')\n    ynmap = cat(")
src = src.replace("    o2O = cat(rasp.Aggregate(mksel(idx, HB, pred_yes('O2')), ynmap)).named('o2O')",
                  "    ox2 = cat(rasp.Aggregate(mksel(idx, HB, pred_protoB), labBmap)).named('ox2')")
src = src.replace("""        else: la = max(1, min(nEc, 2))
        return (capc, eye, la)""", """        else: la = max(1, min(nEc, 2))
        return (capc, eye, la, int(nEc >= 2))""")
src = src.replace("EO = cat(rasp.SequenceMap(lambda a, b: (a == 'yes', b == 'yes'), escO, o2O)).named('EO')",
                  "EO = cat(rasp.SequenceMap(lambda a, b: (int(a == 'yes'), b[0], b[1]), escO, ox2)).named('EO')")
src = src.replace("""        capc, eye, la = s
        esc, o2 = eo
        if capc >= 1: return TAC_CAP2 if capc >= 2 else TAC_CAP1
        if eye: return TAC_EYE
        if la <= 1: return TAC_SA
        return TAC_ESC * int(esc) + TAC_ATK * int(o2)""",
"""        capc, eye, la, ne2 = s
        esc, o2, x2 = eo
        if capc >= 1: return TAC_CAP2 if capc >= 2 else TAC_CAP1
        if eye: return TAC_EYE
        if la <= 1: return TAC_SA
        return TAC_ESC * esc + TAC_ATK * o2 + TAC_DEF * int(x2 and ne2 and not esc)""")
src = src.replace("TAC_CAP1, TAC_CAP2, TAC_EYE, TAC_SA, TAC_ESC, TAC_ATK = 20, 26, -25, -20, 14, 5",
                  "TAC_CAP1, TAC_CAP2, TAC_EYE, TAC_SA, TAC_ESC, TAC_ATK, TAC_DEF = 20, 26, -25, -20, 14, 5, 6")
# zone penalty and danger term
src = src.replace("zpen = num(rasp.Map(lambda z: {'own': 5.0, 'opp': 2.0}.get(z, 0.0), zoneP)).named('zpen')",
"""zpen = num(rasp.Map(lambda z: {'own': 2.0}.get(z, 0.0), zoneP)).named('zpen')
    DTH = 0.05
    dang = num(rasp.Map(lambda v: {'O': 1.0 - DTH, 'X': -1.0 - DTH}.get(v, -DTH), InfM)).named('dang')""")
src = src.replace("a3 = num(rasp.LinearSequenceMap(linev, passv, 1.0, 1.0)).named('a3')",
                  "a3 = num(rasp.LinearSequenceMap(linev, dang, 1.0, -DANGW)).named('a3')")
src = src.replace("GAINW = 8.0", "GAINW = 8.0\nDANGW = 20.0")
open('/work/program.py','w').write(src)
import sys; sys.path.insert(0,'/work')
import importlib, program
importlib.reload(program)
res = compile_program()
```