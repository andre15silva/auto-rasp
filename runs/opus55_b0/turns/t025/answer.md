```python
s = open('/work/prog_v3.py').read()
s = s.replace('''    AtX = rasp.Aggregate(rasp.Select(idx, GLx, P_atari), atval)''',
'''    szvx = rasp.Map(lambda t: "c" if t == "x" else "d", tok)
    szvo = rasp.Map(lambda t: "c" if t == "o" else "d", tok)
    SZx = rasp.Aggregate(rasp.Select(Kx, Lx, P_sz), szvx)
    SZo = rasp.Aggregate(rasp.Select(Ko, Lo, P_sz), szvo)
    bigv = rasp.Map(lambda i: "big" if i == 0 else "small", idx)
    BIGx = rasp.Aggregate(rasp.Select(idx, SZx, P_big), bigv)
    BIGo = rasp.Aggregate(rasp.Select(idx, SZo, P_big), bigv)
    AtX = rasp.Aggregate(rasp.Select(idx, GLx, P_atari), atval)''')
s = s.replace('''    st1 = rasp.SequenceMap(f1, tok, AtX)
    st2 = rasp.SequenceMap(lambda s, a: ("o1" if a == "A" else "oS") if s == "o" else s, st1, AtO)''',
'''    st1 = rasp.SequenceMap(f1, tok, AtX)
    st1b = rasp.SequenceMap(lambda s, b: (("x1b" if b == "big" else "x1s") if s == "x1" else s), st1, BIGx)
    st2 = rasp.SequenceMap(lambda s, a: ("o1" if a == "A" else "oS") if s == "o" else s, st1b, AtO)
    st2b = rasp.SequenceMap(lambda s, b: (("o1b" if b == "big" else "o1s") if s == "o1" else s), st2, BIGo)''')
s = s.replace("st = rasp.SequenceMap(f3, st2, T2xo)", "st = rasp.SequenceMap(f3, st2b, T2xo)")
s = s.replace("def program():", '''def P_sz(k, q):
    if q == PASSI: return 2.0 if k == "P" else -2.0
    if k == q or k == "P": return 2.0
    return -2.0

def P_big(k, q):
    if k == 0: return 100.0 if q == "c" else 0.0
    if k == 1: return 250.0 if q == "d" else 0.0
    return -10.0

def program():''')
open('/work/prog_v4.py','w').write(s)
res = compile_program('/work/prog_v4.py')
print({k: v for k, v in res.items() if k != 'residual_labels'})
```