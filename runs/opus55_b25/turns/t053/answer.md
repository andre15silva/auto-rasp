```python
src = open('/work/program.py').read()
old_zone_pred = src[src.index("ZTH, ZC = 0.12, 10.0"):src.index("def LV(i):")]
new_zone_pred = '''ZCENT = [-0.3, -0.13, 0.0, 0.13, 0.3]
ZNAMES = ['pS', 'pW', 'neu', 'oW', 'oS']
ZZ = 50.0
def pred_zone(k, q):
    if k >= len(ZCENT): return None
    f = {'X': 1.0, 'O': -1.0}.get(q, 0.0)
    c = ZCENT[k]
    return 0.6 + ZZ * (2 * c * f - c * c)

'''
src = src.replace(old_zone_pred, new_zone_pred)
src = src.replace("zmap = cat(rasp.Map(lambda k: ['own', 'opp', 'neu'][k] if k < 3 else 'neu', idx)).named('zmap')",
                  "zmap = cat(rasp.Map(lambda k: ZNAMES[k] if k < len(ZNAMES) else 'neu', idx)).named('zmap')")
src = src.replace("{'neu': 1.0, 'opp': 0.5, 'own': 0.35}", "GAINF")
src = src.replace("zpen = num(rasp.Map(lambda z: {'own': 2.0}.get(z, 0.0), zoneP)).named('zpen')",
                  "zpen = num(rasp.Map(lambda z: {'oS': 2.0, 'oW': 0.5}.get(z, 0.0), zoneP)).named('zpen')")
src = src.replace("'thr' if (s == TAC_SA and z == 'opp') else 'no'", "'thr' if (s == TAC_SA and z in ('pS', 'pW')) else 'no'")
src = src.replace("SA_OPP_BONUS = 16.0", "SA_OPP_BONUS = 16.0\nGAINF = {'neu': 1.0, 'pW': 0.7, 'pS': 0.25, 'oW': 0.6, 'oS': 0.1}")
open('/work/program.py','w').write(src)
print('GAINF' in src, src.count("'own'"), src.count("'opp'"))
import sys; sys.path.insert(0,'/work')
import importlib, program
importlib.reload(program)
res = compile_program()
```