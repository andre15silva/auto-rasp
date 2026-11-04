```python
src = open('/work/program.py').read()
src = src.replace("""def sel_open():
    return rasp.Select(rasp.indices, rasp.indices, lambda k, q: q < 81 and k in NB[q])
def sel_closed():
    return rasp.Select(rasp.indices, rasp.indices, lambda k, q: q < 81 and (k == q or k in NB[q]))""",
"""def sel_open():
    return rasp.Select(rasp.indices, rasp.indices, lambda k, q: (k == 81) if q >= 81 else (k in NB[q]))
def sel_closed():
    return rasp.Select(rasp.indices, rasp.indices, lambda k, q: (k == 81) if q >= 81 else (k == q or k in NB[q]))""")
src = src.replace("""def sel_kernel(s, cutoff=0.02):
    def p(k, q):
        if q >= 81 or k >= 81: return 0.0
        w = kern(q, k, s)
        if w < cutoff: return 0.0
        return 1.0 + math.log(w) / 100
    return rasp.Select(rasp.indices, rasp.indices, p)""",
"""def sel_kernel(s, cutoff=0.02, pad=False):
    Wq = [sum(kern(q, k, s) for k in range(81) if kern(q, k, s) >= cutoff) for q in range(81)]
    S = max(Wq) + 0.05
    def p(k, q):
        if q >= 81: return 0.0
        if k >= 81:
            return (1.0 + math.log(S - Wq[q]) / 100) if pad else 0.0
        w = kern(q, k, s)
        if w < cutoff: return 0.0
        return 1.0 + math.log(w) / 100
    return rasp.Select(rasp.indices, rasp.indices, p)""")
src = src.replace("T_HOPS = 5", "T_HOPS = 6")
src = src.replace("return 3.0 + [-2.0, -0.5, 0.5, 0.5, 0.5][e]", "return 3.0 + [-2.0, -0.5, 0.5, 0.7, 1.0][e]")
src = src.replace("GainM = cat(rasp.Aggregate(sel_kernel(1.5), zoneP))", "GainM = cat(rasp.Aggregate(sel_kernel(1.5, pad=True), zoneP))")
open('/work/program.py','w').write(src)
import sys; sys.path.insert(0,'/work')
import importlib, helper2, program
importlib.reload(program)
res = compile_program()
```