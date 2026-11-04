```python
src = open('/work/program.py').read()
start = src.index("    a1 = num(rasp.LinearSequenceMap(tacP, tacN, 1.0, -1.0)).named('a1')")
end = src.index("    return out", start)
new = """    a1 = num(rasp.LinearSequenceMap(tacP, tacN, 1.0, -1.0)).named('a1')
    c1 = num(rasp.LinearSequenceMap(bigR2, contR, 1.0, 1.0)).named('c1')
    a2 = num(rasp.LinearSequenceMap(gainR, zpen, GAINW, -1.0)).named('a2')
    a3 = num(rasp.LinearSequenceMap(linev, dang, 1.0, -DANGW)).named('a3')
    d1 = num(rasp.LinearSequenceMap(a2, a3, 1.0, 1.0)).named('d1')
    e1 = num(rasp.LinearSequenceMap(a1, c1, 1.0, 1.0)).named('e1')
    e2 = num(rasp.LinearSequenceMap(kotR, d1, 1.0, 1.0)).named('e2')
    out = num(rasp.LinearSequenceMap(e1, e2, SCALE, SCALE)).named('logit')
"""
src = src[:start] + new + src[end:]
open('/work/program.py','w').write(src)
import sys; sys.path.insert(0,'/work')
import importlib, program
importlib.reload(program)
res = compile_program()
```