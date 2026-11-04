```python
src = open('/work/program.py').read()
start = src.index("    RS1 = cat(rasp.Aggregate(mksel(idx, W, pred_single), rv1)).named('RS1')")
end = src.index("    tacP = num(")
new_mid = r'''    RS1 = cat(rasp.Aggregate(mksel(idx, W, pred_single), rv1)).named('RS1')
    RS2 = cat(rasp.Aggregate(mksel(idx, W, pred_pair), rv2)).named('RS2')
    U = cat(rasp.Aggregate(sel_open(), W)).named('U')
    RU = cat(rasp.Aggregate(mksel(idx, U, pred_upair), rvu)).named('RU')

    # ---- far-liberty flags: a stone seeing >=2 (>=3) classes flags its chain ----
    def fflag(kd, r):
        if kd in ('X', 'O') and r == 'c0': return (kd, 'F')
        return 'n'
    G2 = cat(rasp.SequenceMap(fflag, kind, RS1)).named('G2_0')
    G3 = cat(rasp.SequenceMap(fflag, kind, RS2)).named('G3_0')
    def fgm(kd, v):
        if v != 'n' and v[0] == kd: return v
        return 'n'
    for t in range(1, F_HOPS + 1):
        A2 = cat(rasp.Aggregate(sel_closed(), G2)).named(f'FA2_{t}')
        A3 = cat(rasp.Aggregate(sel_closed(), G3)).named(f'FA3_{t}')
        G2 = cat(rasp.SequenceMap(fgm, kind, A2)).named(f'G2_{t}')
        G3 = cat(rasp.SequenceMap(fgm, kind, A3)).named(f'G3_{t}')
    def pred_flag(k, q):
        if k == 0: return (-0.4 + FGAIN) if q != 'n' else -0.4
        if k == 1: return 0.6
        return None
    FR2 = cat(rasp.Aggregate(mksel(idx, G2, pred_flag), ynmap)).named('FR2')
    FR3 = cat(rasp.Aggregate(mksel(idx, G3, pred_flag), ynmap)).named('FR3')

    def fstA(kd, r):
        if kd == 'X': return 'Xm' if r == 'yes' else 'X1'
        if kd == 'O': return 'Om' if r == 'yes' else 'O1'
        return kd
    def fstB(kd, r):
        if kd == 'X': return 'X3' if r == 'yes' else 'X2'
        if kd == 'O': return 'O3' if r == 'yes' else 'O2'
        return kd
    stA = cat(rasp.SequenceMap(fstA, kind, FR2)).named('stA')
    stB = cat(rasp.SequenceMap(fstB, kind, FR3)).named('stB')
    HA = cat(rasp.Aggregate(sel_hist(), stA)).named('HA')
    HB = cat(rasp.Aggregate(sel_hist(), stB)).named('HB')
    labA = cat(rasp.Aggregate(mksel(idx, HA, pred_proto), labmap)).named('labA')
    escO = cat(rasp.Aggregate(mksel(idx, HA, pred_yes('X1')), ynmap)).named('escO')
    ox2 = cat(rasp.Aggregate(mksel(idx, HB, pred_protoB), labBmap)).named('ox2')

    def ftab1(lab, ru):
        capc, xn, eye, nEc = lab
        if capc >= 1: return ('cap', capc)
        if eye: return ('eye',)
        if xn: la = 1 if ru == 'lo' else 2
        else: la = max(1, min(nEc, 2))
        return (la, int(nEc >= 2), xn)
    tab1 = cat(rasp.SequenceMap(ftab1, labA, RU)).named('tab1')
    EO = cat(rasp.SequenceMap(lambda a, b: (int(a == 'yes'),) + tuple(b), escO, ox2)).named('EO')
    def ftab2(s, eo):
        esc, o2, x2, x3 = eo
        if s[0] == 'cap': return TAC_CAP2 if s[1] >= 2 else TAC_CAP1
        if s[0] == 'eye': return TAC_EYE
        la, ne2, xn = s
        if xn and x3: la = max(la, 2)
        if la <= 1: return TAC_SA
        return TAC_ESC * esc + TAC_ATK * o2 + TAC_DEF * int(x2 and ne2 and not esc)
    tab2 = cat(rasp.SequenceMap(ftab2, tab1, EO)).named('tab2')
'''
src = src[:start] + new_mid + src[end:]
# B prototypes with 4 categories
src = src.replace("""PROTOS_B = [t for t in itertools.product(range(5), repeat=3) if sum(t) == 4]
def catB(v): return 'O2' if v == 'O2' else ('X2' if v == 'X2' else 'R')
CATSB = ['O2', 'X2', 'R']""", """PROTOS_B = [t for t in itertools.product(range(5), repeat=4) if sum(t) == 4]
def catB(v): return v if v in ('O2', 'X2', 'X3') else 'R'
CATSB = ['O2', 'X2', 'X3', 'R']""")
src = src.replace("    t = PROTOS_B[k] if k < len(PROTOS_B) else (0, 0, 4)\n    m = [x / 4 for x in t]",
                  "    t = PROTOS_B[k] if k < len(PROTOS_B) else (0, 0, 0, 4)\n    m = [x / 4 for x in t]")
src = src.replace("""    t = PROTOS_B[k] if k < len(PROTOS_B) else (0, 0, 4)
    return (int(t[0] >= 1), int(t[1] >= 1))""", """    t = PROTOS_B[k] if k < len(PROTOS_B) else (0, 0, 0, 4)
    return (int(t[0] >= 1), int(t[1] >= 1), int(t[2] >= 1))""")
src = src.replace("labelB(k) if k <= len(PROTOS_B) else (0, 0)", "labelB(k) if k <= len(PROTOS_B) else (0, 0, 0)")
src = src.replace("T_HOPS = 6", "T_HOPS = 6\nF_HOPS = 4\nFGAIN = 2000.0")
open('/work/program.py','w').write(src)
import sys; sys.path.insert(0,'/work')
import importlib, program, helper2
importlib.reload(program)
helper2.layer_report(program.program)
res = compile_program()
```