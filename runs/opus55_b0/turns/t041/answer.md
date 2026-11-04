```python
s = open('/work/prog_v6.py').read()
s = s.replace('''    Ie = rasp.SequenceMap(f0, ise, idx)''', '''    rsx = rasp.SequenceMap(lambda t, l: 1 if (t == "x" and l != "x") else 0, tok, Lft)
    ise_late = rasp.SequenceMap(lambda a, b: a, ise, rsx)
    Ie = rasp.SequenceMap(f0, ise_late, idx)''')
s = s.replace('''    rsx = rasp.SequenceMap(lambda t, l: 1 if (t == "x" and l != "x") else 0, tok, Lft)
    rso =''', '''    rso =''')
s = s.replace('''    Ko = rasp.SequenceMap(fk, Lo, clso)''', '''    zz = rasp.Map(lambda l: 0, Lx)
    clso_late = rasp.SequenceMap(lambda c, z: c, clso, zz)
    Ko = rasp.SequenceMap(fk, Lo, clso_late)''')
open('/work/prog_v7.py','w').write(s)
res = compile_program('/work/prog_v7.py')
print({k: v for k, v in res.items() if k != 'residual_labels'})
```