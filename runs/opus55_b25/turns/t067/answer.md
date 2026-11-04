```python
src = open('/work/program.py').read()
# revert to 3-bin zone
old = src[src.index("ZCENT = ["):src.index("def LV(i):")]
src = src.replace(old, '''ZTH, ZC = 0.12, 10.0
def pred_zone(k, q):
    fx = {'X': 1.0, 'O': -2.0}.get(q, 0.0)
    fo = {'O': 1.0, 'X': -2.0}.get(q, 0.0)
    if k == 0: return 0.6 + ZC * (fx - ZTH)
    if k == 1: return 0.6 + ZC * (fo - ZTH)
    if k == 2: return 0.6
    return None

''')
src = src.replace("zmap = cat(rasp.Map(lambda k: ZNAMES[k] if k < len(ZNAMES) else 'neu', idx)).named('zmap')",
                  "zmap = cat(rasp.Map(lambda k: ['own', 'opp', 'neu'][k] if k < 3 else 'neu', idx)).named('zmap')")
src = src.replace("zpen = num(rasp.Map(lambda z: {'oS': 2.0, 'oW': 0.5}.get(z, 0.0), zoneP)).named('zpen')",
                  "zpen = num(rasp.Map(lambda z: {'own': 2.0}.get(z, 0.0), zoneP)).named('zpen')")
src = src.replace("GAINF = {'neu': 1.0, 'pW': 0.7, 'pS': 0.25, 'oW': 0.6, 'oS': 0.1}", "GAINF = {'neu': 1.0, 'opp': 0.5, 'own': 0.35}")
# remove throw-in bonus
src = src.replace("SA_OPP_BONUS = 16.0", "SA_OPP_BONUS = 0.0")
src = src.replace("'thr' if (s == TAC_SA and z in ('pS', 'pW')) else 'no'", "'thr' if (s == TAC_SA and z == 'opp') else 'no'")
# tactics: restore base, big as additive
src = src.replace("TAC_CAP1, TAC_CAP2, TAC_EYE, TAC_SA, TAC_ESC, TAC_ATK, TAC_DEF = 14, 18, -25, -20, 6, 1, 2\nBIG_CAP, BIG_ESC, BIG_DEF, BIG_ATK = 10, 14, 6, 4",
                  "TAC_CAP1, TAC_CAP2, TAC_EYE, TAC_SA, TAC_ESC, TAC_ATK, TAC_DEF = 20, 26, -25, -20, 14, 2, 3\nBIG_CAP, BIG_ESC, BIG_DEF, BIG_ATK = 6, 8, 4, 3")
open('/work/program.py','w').write(src)
import sys; sys.path.insert(0,'/work')
import importlib, program
importlib.reload(program)
print([l for l in src.split('\n') if 'zsa' in l][:3])
res = compile_program()
```