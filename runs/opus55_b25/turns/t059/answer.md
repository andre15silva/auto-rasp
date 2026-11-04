```python
src = open('/work/program.py').read()
# --- size pipeline + new st categories ---
old_st = src[src.index("    def fstA(kd, r):"):src.index("    def ftab1(lab, ru):")]
new_st = r'''    # ---- chain size >= 3 detection (local, 2-hop) ----
    KH = cat(rasp.Aggregate(sel_hist(), kind)).named('KH')
    same = cat(rasp.SequenceMap(lambda kd, v: 'S' if (kd in ('X', 'O') and v == kd) else 'D', kind, KH)).named('same')
    def pred_deg2(k, q):
        if k == 0: return (0.1 + 3.2 * 0.75) if q == 'S' else (0.1 - 3.2 * 0.25)
        if k == 1: return 0.6
        return None
    d2 = cat(rasp.Aggregate(mksel(idx, same, pred_deg2), ynmap)).named('d2')
    flagD = cat(rasp.SequenceMap(lambda kd, y: (kd, 'D') if (kd in ('X', 'O') and y == 'yes') else 'n', kind, d2)).named('flagD')
    FD = cat(rasp.Aggregate(sel_closed(), flagD)).named('FD')
    FDm = cat(rasp.SequenceMap(lambda kd, v: 'F' if (v != 'n' and v[0] == kd) else 'n', kind, FD)).named('FDm')
    def pred_big(k, q):
        if k == 0: return (0.1 + 2.0) if q == 'F' else 0.1
        if k == 1: return 0.6
        return None
    bigR = cat(rasp.Aggregate(mksel(idx, FDm, pred_big), ynmap)).named('bigR')
    def fkb(kd, y):
        if kd in ('X', 'O'): return kd + ('b' if y == 'yes' else 's')
        return kd
    kbig = cat(rasp.SequenceMap(fkb, kind, bigR)).named('kbig')

    def fstA(kb, r):
        if kb[0] == 'X' and len(kb) == 2: return 'Xm' if r == 'yes' else 'X1' + kb[1]
        if kb[0] == 'O' and len(kb) == 2: return 'Om' if r == 'yes' else 'O1' + kb[1]
        return kb
    def fstB(kb, r):
        if kb[0] == 'X' and len(kb) == 2: return 'X3' if r == 'yes' else 'X2' + kb[1]
        if kb[0] == 'O' and len(kb) == 2: return 'O3' if r == 'yes' else 'O2' + kb[1]
        return kb
    stA = cat(rasp.SequenceMap(fstA, kbig, FR2)).named('stA')
    stB = cat(rasp.SequenceMap(fstB, kbig, FR3)).named('stB')
    HA = cat(rasp.Aggregate(sel_hist(), stA)).named('HA')
    HB = cat(rasp.Aggregate(sel_hist(), stB)).named('HB')
    labA = cat(rasp.Aggregate(mksel(idx, HA, pred_proto), labmap)).named('labA')
    labAb = cat(rasp.Aggregate(mksel(idx, HA, pred_protoAb), labAbmap)).named('labAb')
    ox2 = cat(rasp.Aggregate(mksel(idx, HB, pred_protoB), labBmap)).named('ox2')
    labBb = cat(rasp.Aggregate(mksel(idx, HB, pred_protoBb), labBbmap)).named('labBb')

'''
src = src.replace(old_st, new_st)
# catof for 8-category HA; catB for HB
src = src.replace("def catof(v): return 'X' if v in ('X1', 'Xm') else v",
                  "def catof(v):\n    if v in ('X1s', 'X1b', 'Xm'): return 'X'\n    if v in ('O1s', 'O1b'): return 'O1'\n    return v")
src = src.replace("def catB(v): return v if v in ('O2', 'X2', 'X3') else 'R'",
                  "def catB(v):\n    if v in ('O2s', 'O2b'): return 'O2'\n    if v in ('X2s', 'X2b'): return 'X2'\n    return v if v == 'X3' else 'R'")
# new prototype heads
src = src.replace("ZCENT = [", '''def mkproto(cats, catfn, labfn, default):
    protos = [t for t in itertools.product(range(5), repeat=len(cats)) if sum(t) == 4]
    def pred(k, q):
        if k > len(protos): return None
        t = protos[k] if k < len(protos) else default
        m = [x / 4 for x in t]
        sq = sum(x * x for x in m)
        return C1 * (2 * m[cats.index(catfn(q))] - sq) + 0.5
    def lab(k):
        t = protos[k] if k < len(protos) else default
        return labfn(t)
    return pred, lab, len(protos)
def _catAb(v):
    return v if v in ('X1s', 'X1b', 'O1b') else 'R'
pred_protoAb, labelAb, NPAb = mkproto(['X1s', 'X1b', 'O1b', 'R'], _catAb, lambda t: (int(t[0] + t[1] >= 1), int(t[1] >= 1), int(t[2] >= 1)), (0, 0, 0, 4))
def _catBb(v):
    return v if v in ('X2b', 'O2b') else 'R'
pred_protoBb, labelBb, NPBb = mkproto(['X2b', 'O2b', 'R'], _catBb, lambda t: (int(t[0] >= 1), int(t[1] >= 1)), (0, 0, 4))

ZCENT = [''', 1)
src = src.replace("    ynmap = cat(", "    labAbmap = cat(rasp.Map(lambda k: labelAb(k) if k <= NPAb else (0, 0, 0), idx)).named('labAbmap')\n    labBbmap = cat(rasp.Map(lambda k: labelBb(k) if k <= NPBb else (0, 0), idx)).named('labBbmap')\n    ynmap = cat(", 1)
# EO now from labAb (esc any) and ox2
src = src.replace("EO = cat(rasp.SequenceMap(lambda a, b: (int(a == 'yes'),) + tuple(b), escO, ox2)).named('EO')",
                  "EO = cat(rasp.SequenceMap(lambda a, b: (a[0],) + tuple(b), labAb, ox2)).named('EO')\n    bigbits = cat(rasp.SequenceMap(lambda a, b: (a[1], a[2], b[0], b[1]), labAb, labBb)).named('bigbits')")
src = src.replace("""    tab2 = cat(rasp.SequenceMap(ftab2, tab1, EO)).named('tab2')""",
"""    tab2 = cat(rasp.SequenceMap(ftab2, tab1, EO)).named('tab2')
    def fbig(s, bb):
        escB, capB, defB, atkB = bb
        if s[0] == 'cap': return BIG_CAP * capB
        if s[0] == 'eye': return 0
        la, ne2, xn = s
        if la <= 1: return 0
        return BIG_ESC * escB + BIG_DEF * int(defB and ne2 and not escB) + BIG_ATK * atkB
    bigt = cat(rasp.SequenceMap(fbig, tab1, bigbits)).named('bigt')
    bigR2 = num(rasp.Map(lambda v: float(v), bigt)).named('bigR2')""")
# NOTE: tab1 x3 rule lives in ftab2; for bigt use same la (without x3 upgrade) - acceptable
src = src.replace("b0 = num(rasp.LinearSequenceMap(a1, zsaR, 1.0, 1.0)).named('b0')",
                  "b00 = num(rasp.LinearSequenceMap(a1, bigR2, 1.0, 1.0)).named('b00')\n    b0 = num(rasp.LinearSequenceMap(b00, zsaR, 1.0, 1.0)).named('b0')")
src = src.replace("TAC_CAP1, TAC_CAP2, TAC_EYE, TAC_SA, TAC_ESC, TAC_ATK, TAC_DEF = 20, 26, -25, -20, 14, 2, 3",
                  "TAC_CAP1, TAC_CAP2, TAC_EYE, TAC_SA, TAC_ESC, TAC_ATK, TAC_DEF = 14, 18, -25, -20, 6, 1, 2\nBIG_CAP, BIG_ESC, BIG_DEF, BIG_ATK = 10, 14, 6, 4")
open('/work/program.py','w').write(src)
import sys; sys.path.insert(0,'/work')
import importlib, program, helper2
importlib.reload(program)
helper2.layer_report(program.program)
res = compile_program()
```