```python
src = open('/work/program.py').read()
old_loop = src[src.index("    for t in range(1, F_HOPS + 1):"):src.index("    FR3 = cat(")]
new_loop = """    G2_4 = None
    for t in range(1, F2_HOPS + 1):
        A2 = cat(rasp.Aggregate(sel_closed(), G2)).named(f'FA2_{t}')
        G2 = cat(rasp.SequenceMap(fgm, kind, A2)).named(f'G2_{t}')
        if t == F_HOPS: G2_4 = G2
        if t <= F_HOPS:
            A3 = cat(rasp.Aggregate(sel_closed(), G3)).named(f'FA3_{t}')
            G3 = cat(rasp.SequenceMap(fgm, kind, A3)).named(f'G3_{t}')
    def pred_flag(k, q):
        if k == 0: return (-0.4 + FGAIN) if q != 'n' else -0.4
        if k == 1: return 0.6
        return None
    FR2 = cat(rasp.Aggregate(mksel(idx, G2_4, pred_flag), ynmap)).named('FR2')
    FR2b = cat(rasp.Aggregate(mksel(idx, G2, pred_flag), ynmap)).named('FR2b')
"""
src = src.replace(old_loop, new_loop)
assert "FR2 = cat(rasp.Aggregate(mksel(idx, G2, pred_flag), ynmap)).named('FR2')" not in src or True
src = src.replace("    FR2 = cat(rasp.Aggregate(mksel(idx, G2, pred_flag), ynmap)).named('FR2')\n", "", 1) if src.count("named('FR2')") > 1 else src
# confirmed-atari opp neighbor
src = src.replace("    HA = cat(rasp.Aggregate(sel_hist(), stA)).named('HA')",
"""    stC = cat(rasp.SequenceMap(lambda kd, r: 'Oc' if (kd == 'O' and r == 'no') else 'n', kind, FR2b)).named('stC')
    HC = cat(rasp.Aggregate(sel_hist(), stC)).named('HC')
    def pred_anyc(k, q):
        if k == 0: return (0.1 + 3.2) if q == 'Oc' else 0.1
        if k == 1: return 0.6
        return None
    confO = cat(rasp.Aggregate(mksel(idx, HC, pred_anyc), ynmap)).named('confO')
    HA = cat(rasp.Aggregate(sel_hist(), stA)).named('HA')""")
src = src.replace("        if capc >= 1: return ('cap', capc, int(nEc == 0 and not xn))\n",
                  "        if capc >= 1:\n            sa = (ru == 'lo') if xn else (nEc <= 1)\n            return ('cap', capc, int(nEc == 0 and not xn), int(sa))\n")
src = src.replace("    a1 = num(rasp.LinearSequenceMap(tacP, tacN, 1.0, -1.0)).named('a1')",
"""    fcap = cat(rasp.SequenceMap(lambda s, c: 'fc' if (s[0] == 'cap' and s[3] and c == 'no') else 'n', tab1, confO)).named('fcap')
    fcapR = num(rasp.Map(lambda v: FCAP_PEN if v == 'fc' else 0.0, fcap)).named('fcapR')
    a1 = num(rasp.LinearSequenceMap(tacP, tacN, 1.0, -1.0)).named('a1')""")
src = src.replace("    e1 = num(rasp.LinearSequenceMap(a1, c1, 1.0, 1.0)).named('e1')",
                  "    e0 = num(rasp.LinearSequenceMap(a1, c1, 1.0, 1.0)).named('e0')\n    e1 = num(rasp.LinearSequenceMap(e0, fcapR, 1.0, -1.0)).named('e1')")
src = src.replace("F_HOPS = 4\nFGAIN = 1e6", "F_HOPS = 4\nF2_HOPS = 8\nFGAIN = 1e9\nFCAP_PEN = 52.0")
open('/work/program.py','w').write(src)
print(src.count("named('FR2')"), 'F2_HOPS' in src, 'fcapR' in src)
import sys; sys.path.insert(0,'/work')
import importlib, program, helper2
importlib.reload(program)
helper2.layer_report(program.program)
res = compile_program()
```