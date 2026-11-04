The compile timed out — Tracr's compile time grows steeply with residual width, and the 172-category bundle (×7 copies) pushed D past ~2500. I'll hash stone membership into 8 buckets per colour (26-category bundle) and compact the tactical tail.

```python
src = open('/work/gonet4.py').read()
# 1) hashed membership entries
src = src.replace("""        if t == 'x': return ('X', i // 9, i % 9)
        if t == 'o': return ('O', i // 9, i % 9)""", """        if t == 'x': return ('X', bucket(i))
        if t == 'o': return ('O', bucket(i))""")
# 2) extraction directly from bundle
old = src[src.index("    # ---- extraction"):src.index("    cnt3 = cat(")]
new = """    # ---- extraction
    def extract(src_, pred, name):
        def fx(v, pred=pred):
            if v == 'D': return TINY
            return 1 if pred(v) else 0
        return thr(num(M(fx, src_), 'x' + name), 'f' + name)
    fb = [extract(bund, (lambda v, h=h: v == h), f'b{h}') for h in range(NBUCK)]
    fXm = [extract(bund, (lambda v, h=h: v == ('X', h)), f'Xm{h}') for h in range(NBUCK)]
    fOm = [extract(bund, (lambda v, h=h: v == ('O', h)), f'Om{h}') for h in range(NBUCK)]
    fanyX = extract(bund, (lambda v: isinstance(v, tuple) and v[0] == 'X'), 'anyX')
    fanyO = extract(bund, (lambda v: isinstance(v, tuple) and v[0] == 'O'), 'anyO')
    libn = tree(fb, 'sl', 0.01)
    SX = tree(fXm, 'sX', 0.01)
    SO = tree(fOm, 'sO', 0.01)
"""
src = src.replace(old, new)
src = src.replace("""def szcls(v):
    n = int(round(v * 100))
    return 't' if n == 0 else 's' if n <= 4 else 'm' if n <= 7 else 'l'""", """def szcls(v):
    n = int(round(v * 100))
    return 't' if n <= 1 else 's' if n <= 3 else 'm' if n <= 6 else 'l'""")
# 3) compact libs-after / tactical
old = src[src.index("    # libs after the move"):src.index("    def atk(o2, l):")]
new = """    # libs after the move (approx): empties + other liberties of joined own groups + captures
    la1 = cat(SM(lambda e, x3: (e, x3), nE, x3a), 'la1')
    la2 = cat(SM(lambda x2, cp: (x2 > 0, cp > 0), x2m, capm), 'la2')
    def laf(a, b):
        e, x3 = a; x2, cp = b
        l = e + (1 if x2 else 0) + (2 if x3 else 0) + (2 if cp else 0)
        return (min(l, 3), e == 0)
    la = cat(SM(laf, la1, la2), 'la')
    A = cat(SM(lambda l, cp: (l, cp), la, capm), 'tA')
    escg = cat(SM(lambda e, c: e if c == 'E' else -1, escm, color), 'escg')
    Bp = cat(SM(lambda e, x2: (e, x2), escg, x2m), 'tB')
    T = TACT
    def tact(a, b):
        (la_, e0), cp = a
        esc, x2 = b
        if esc == -1: return 0.0
        v = 0.0
        if cp:
            v += T['cap'][cp] + (T['capsave'] if esc else 0.0)
        elif esc:
            if la_ >= 3: v += T['esc3'][esc]
            elif la_ == 2: v += T['esc2'][esc]
            else: v += T['escf']
        else:
            if la_ == 0: v += T['sui']
            elif la_ == 1: v += T['sa'][max(x2, 1)]
            elif la_ == 2 and x2: v += T['fill2']
        if e0 and not cp and not esc: v += T['noE']
        if la_ >= 3 and x2: v += T['def2'][x2]
        return round(v, 2)
    t1c = cat(SM(tact, A, Bp), 't1c')
    t1 = num(M(lambda v: v, t1c), 't1')
"""
src = src.replace(old, new)
src = src.replace("""    def atk(o2, l):
        la_ = l[0]""", """    def atk(o2, l):
        la_ = l[0]""")
open('/work/gonet4.py','w').write(src)
import time, sys, importlib
sys.path.insert(0, '/work')
import gonet4; importlib.reload(gonet4)
from tracr.compiler import compiling
for stop in ['nbinfo', 'feat']:
    t0 = time.time()
    m = compiling.compile_rasp_to_model(gonet4.build(stop=stop), vocab={".", "x", "o", "B", "W"}, max_seq_len=82, compiler_bos="BOS", mlp_exactness=500000)
    print(stop, 'compile', round(time.time()-t0), 'D', len(m.residual_labels), 'layers', m.model_config.num_layers)
```