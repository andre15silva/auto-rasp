```python
s = open('/work/prog_v4.py').read()
s = s.replace('''def program():''', '''def P_up(k, q):
    if q == PASSI or q < 9: return 2.0 if k == PASSI else -2.0
    return 2.0 if k == q - 9 else -2.0

def P_vrun(k, q):
    if q == PASSI: return 2.0 if k == PASSI else -10.0
    if k == PASSI: return -10.0
    if k % 9 == q % 9 and k <= q: return 2.0 + 3.0 * (k // 9)
    return -10.0

N_ALT = 3

def program():''')
s = s.replace('''    Lft = rasp.Aggregate(rasp.Select(idx, idx, P_left), tok)''', '''    Lft = rasp.Aggregate(rasp.Select(idx, idx, P_left), tok)
    Upt = rasp.Aggregate(rasp.Select(idx, idx, P_up), tok)''')
s = s.replace('''    RSo = rasp.SequenceMap(f0, rso, idx)''', '''    RSo = rasp.SequenceMap(f0, rso, idx)
    vsx = rasp.SequenceMap(lambda t, u: 1 if (t == "x" and u != "x") else 0, tok, Upt)
    vso = rasp.SequenceMap(lambda t, u: 1 if (t == "o" and u != "o") else 0, tok, Upt)
    VSx = rasp.SequenceMap(f0, vsx, idx)
    VSo = rasp.SequenceMap(f0, vso, idx)''')
old_loop = s[s.index('    Lx = rasp.Aggregate(rasp.Select(RSx, Lx0, P_run), RSx)'):s.index('    fk = lambda l, c:')]
new_loop = '''    fk = lambda l, c: (l if (c == "s" and l != 81) else ("P" if c == "P" else "n"))
    Hrx = rasp.Aggregate(rasp.Select(RSx, Lx0, P_run), RSx)
    Hro = rasp.Aggregate(rasp.Select(RSo, Lo0, P_run), RSo)
    Vrx = rasp.Aggregate(rasp.Select(VSx, Lx0, P_vrun), VSx)
    Vro = rasp.Aggregate(rasp.Select(VSo, Lo0, P_vrun), VSo)
    KHx = rasp.SequenceMap(fk, Hrx, clsx)
    KHo = rasp.SequenceMap(fk, Hro, clso)
    KVx = rasp.SequenceMap(fk, Vrx, clsx)
    KVo = rasp.SequenceMap(fk, Vro, clso)
    Lx, Lo = Hrx, Hro
    for k in range(N_ALT):
        if k % 2 == 0:
            Hx = rasp.Aggregate(rasp.Select(KVx, Vrx, P_group2), Lx)
            Ho = rasp.Aggregate(rasp.Select(KVo, Vro, P_group2), Lo)
        else:
            Hx = rasp.Aggregate(rasp.Select(KHx, Hrx, P_group2), Lx)
            Ho = rasp.Aggregate(rasp.Select(KHo, Hro, P_group2), Lo)
        Lx = rasp.Aggregate(rasp.Select(idx, Hx, P_argmin), Lx)
        Lo = rasp.Aggregate(rasp.Select(idx, Ho, P_argmin), Lo)

'''
s = s.replace(old_loop, new_loop)
s = s.replace('''    fk = lambda l, c: (l if (c == "s" and l != 81) else ("P" if c == "P" else "n"))
    Kx = rasp.SequenceMap(fk, Lx, clsx)''', '''    Kx = rasp.SequenceMap(fk, Lx, clsx)''')
open('/work/prog_v5.py','w').write(s)
print(s[s.index('    Lft ='):s.index('    GLx =')])
```