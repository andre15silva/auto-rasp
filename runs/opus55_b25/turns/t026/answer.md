```python
src = open('/work/program.py').read()
# 1. global scale + selector helper
src = src.replace("def cat(x): return rasp.categorical(x)",
"""FSC = math.sqrt(84.0)
def mksel(keys, queries, design):
    def p(k, q):
        v = design(k, q)
        if v is None or v is False: return -FSC
        if v is True: return FSC
        return FSC * float(v)
    return rasp.Select(keys, queries, p)
def cat(x): return rasp.categorical(x)""")
src = src.replace("""def sel_open():
    return rasp.Select(rasp.indices, rasp.indices, lambda k, q: (k == 81) if q >= 81 else (k in NB[q]))
def sel_closed():
    return rasp.Select(rasp.indices, rasp.indices, lambda k, q: (k == 81) if q >= 81 else (k == q or k in NB[q]))
def sel_hist():
    def p(k, q):
        if q >= 81: return 0.0
        if k in NB[q]: return 1.0
        if k == 81 and len(NB[q]) < 4: return 1.0 + math.log(4 - len(NB[q])) / 100
        return 0.0
    return rasp.Select(rasp.indices, rasp.indices, p)""",
"""def sel_open():
    return mksel(rasp.indices, rasp.indices, lambda k, q: (k == 81) if q >= 81 else (k in NB[q]))
def sel_closed():
    return mksel(rasp.indices, rasp.indices, lambda k, q: (k == 81) if q >= 81 else (k == q or k in NB[q]))
def sel_hist():
    def p(k, q):
        if q >= 81: return 1.0 if k == 81 else None
        if k in NB[q]: return 1.0
        if k == 81 and len(NB[q]) < 4: return 1.0 + math.log(4 - len(NB[q])) / 100
        return None
    return mksel(rasp.indices, rasp.indices, p)""")
src = src.replace("""    def p(k, q):
        if q >= 81: return 0.0
        if k >= 81:
            return (1.0 + math.log(S - Wq[q]) / 100) if pad else 0.0
        w = kern(q, k, s)
        if w < cutoff: return 0.0
        return 1.0 + math.log(w) / 100
    return rasp.Select(rasp.indices, rasp.indices, p)""",
"""    def p(k, q):
        if q >= 81: return 1.0 if k == 81 else None
        if k >= 81:
            return (1.0 + math.log(S - Wq[q]) / 100) if pad else None
        w = kern(q, k, s)
        if w < cutoff: return None
        return 1.0 + math.log(w) / 100
    return mksel(rasp.indices, rasp.indices, p)""")
# readout / classifier predicates: non-selected -> None
for old in ["    if k == NCLS: return 0.7\n    return 0.0", "    if k == NPAIR: return 0.7\n    return 0.0"]:
    src = src.replace(old, old.replace("return 0.0", "return None"))
src = src.replace("""    if k >= len(PROTOS): return 0.0
    t = PROTOS[k]""", """    if k > len(PROTOS): return None
    if k == len(PROTOS): t = (0, 4, 0, 0, 0)
    else: t = PROTOS[k]""")
src = src.replace("""        if k == 1: return 0.6
        return 0.0""", """        if k == 1: return 0.6
        return None""")
src = src.replace("""    if k == 2: return 0.6
    return 0.0""", """    if k == 2: return 0.6
    return None""")
# replace rasp.Select( usages for readouts/classifiers with mksel
src = src.replace("rasp.Aggregate(rasp.Select(", "rasp.Aggregate(mksel(")
# label for all-P prototype (index len(PROTOS)) -> neutral
src = src.replace("labmap = cat(rasp.Map(lambda k: labelA(PROTOS[k]) if k < len(PROTOS) else labelA(PROTOS[0]), idx)).named('labmap')",
                  "labmap = cat(rasp.Map(lambda k: labelA(PROTOS[k]) if k < len(PROTOS) else (0, 0, 0, 2), idx)).named('labmap')")
open('/work/program.py','w').write(src)
print(src.count('rasp.Select('), src.count('mksel('))
import sys; sys.path.insert(0,'/work')
import importlib, program
importlib.reload(program)
res = compile_program()
```