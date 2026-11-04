Interesting: size alone doesn't explain the 296 s (an 812M-param toy ran in 15 s). Something numerical in my v1 (denormals?) may be the culprit. Let me rebuild v1 with the cheaper threshold trick (returning None outside two kept values shrinks each threshold MLP to ~2 neurons), initial flags via MLPs instead of heads, and measure again.

```python
import re
s = open('/work/gonet.py').read()
# 1) cheap thresholds
s = s.replace('''def thr(agg, name, cat=False):
    f = (lambda x: bool(x > 0.001)) if cat else (lambda x: 1 if x > 0.001 else 0)''',
'''THR_LOW = 1.0/9
def thr(agg, name, cat=False):
    def f(x, cat=cat):
        if abs(x) < 1e-12: return False if cat else 0
        if abs(x - THR_LOW) < 1e-12: return True if cat else 1
        return None''')
# 2) initial flags via MLP from shifted colours instead of attention heads
old_init = s[s.index('    # ---- initial flags'):s.index('    # ---- runs')]
new_init = '''    # ---- initial flags via MLPs (no heads)
    eNS = rasp.categorical(rasp.SequenceMap(lambda a, b: (a == 'E', b == 'E'), nc['N'], nc['S'])).named('eNS')
    eWE = rasp.categorical(rasp.SequenceMap(lambda a, b: (a == 'E', b == 'E'), nc['W'], nc['E'])).named('eWE')
    xNS = rasp.categorical(rasp.SequenceMap(lambda a, b: (a == 'X' or b == 'X', a == 'O' or b == 'O'), nc['N'], nc['S'])).named('xNS')
    xWE = rasp.categorical(rasp.SequenceMap(lambda a, b: (a == 'X' or b == 'X', a == 'O' or b == 'O'), nc['W'], nc['E'])).named('xWE')
    rowc = rasp.categorical(rasp.SequenceMap(lambda c, i: (i // 9) if (c in ('X', 'O') and i < 81) else -1, color, idx)).named('rowc')
    colc = rasp.categorical(rasp.SequenceMap(lambda c, i: (i % 9) if (c in ('X', 'O') and i < 81) else -1, color, idx)).named('colc')
    ecol = rasp.categorical(rasp.Map(lambda c: c == 'E', color)).named('ecol')
    # pattern for rows: (row, N empty, S empty, W or E empty)
    patR = rasp.categorical(rasp.SequenceMap(lambda ns, we: (ns[0], ns[1], we[0] or we[1]), eNS, eWE)).named('patR')
    patC = rasp.categorical(rasp.SequenceMap(lambda ns, we: (we[0], we[1], ns[0] or ns[1]), eNS, eWE)).named('patC')
    patRr = rasp.categorical(rasp.SequenceMap(lambda p, r: (r,) + p, patR, rowc)).named('patRr')
    patCc = rasp.categorical(rasp.SequenceMap(lambda p, c: (c,) + p, patC, colc)).named('patCc')
    patT = rasp.categorical(rasp.SequenceMap(lambda a, b: (a[0] or b[0], a[1] or b[1]), xNS, xWE)).named('patT')
    patTe = rasp.categorical(rasp.SequenceMap(lambda p, e: p if e else (False, False), patT, ecol)).named('patTe')
    flags = []
    for r in range(9):
        def fr(p, r=r):
            rr, n, s_, we = p
            if rr < 0: return 0
            return 1 if ((n and r == rr - 1) or (s_ and r == rr + 1) or (we and r == rr)) else 0
        flags.append(rasp.numerical(rasp.Map(fr, patRr)).named(f'R{r}_0'))
    for c in range(9):
        def fc(p, c=c):
            cc, w, e, ns = p
            if cc < 0: return 0
            return 1 if ((w and c == cc - 1) or (e and c == cc + 1) or (ns and c == cc)) else 0
        flags.append(rasp.numerical(rasp.Map(fc, patCc)).named(f'C{c}_0'))
    flags.append(rasp.numerical(rasp.Map(lambda p: 1 if p[0] else 0, patTe)).named('TX_0'))
    flags.append(rasp.numerical(rasp.Map(lambda p: 1 if p[1] else 0, patTe)).named('TO_0'))

'''
s = s.replace(old_init, new_init)
# 3) remove stoneidx/emptyidx lines
s = re.sub(r"    stoneidx = .*\n", "", s); s = re.sub(r"    emptyidx = .*\n", "", s)
# 4) diagonal shifts from a later copy of color
s = s.replace("    dc = {d: shift(color, v, 'dc' + d) for d, v in DIAG.items()}\n", "")
s = s.replace("    hrun = rasp.categorical(", "    color4 = rasp.categorical(rasp.SequenceMap(lambda b, c: c, hsb, color)).named('color4')\n    dc = {d: shift(color4, v, 'dc' + d) for d, v in DIAG.items()}\n    hrun = rasp.categorical(", 1)
open('/work/gonet.py','w').write(s)
open('/work/program.py','w').write('''
import sys
sys.path.insert(0, '/work')
import importlib, gonet
importlib.reload(gonet)
MLP_EXACTNESS = 1000
def program():
    return gonet.build()
''')
r = compile_program()
```