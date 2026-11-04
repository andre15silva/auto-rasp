```python
s = open('/work/prog_v4.py').read()
s = s.replace('''    st1b = rasp.SequenceMap(lambda s, b: (("x1b" if b == "big" else "x1s") if s == "x1" else s), st1, BIGx)
    st2 = rasp.SequenceMap(lambda s, a: ("o1" if a == "A" else "oS") if s == "o" else s, st1b, AtO)
    st2b = rasp.SequenceMap(lambda s, b: (("o1b" if b == "big" else "o1s") if s == "o1" else s), st2, BIGo)''',
'''    st2 = rasp.SequenceMap(lambda s, a: ("o1" if a == "A" else "oS") if s == "o" else s, st1, AtO)
    BIGxo = rasp.SequenceMap(lambda a, b: "xb" if a == "big" else ("ob" if b == "big" else "n"), BIGx, BIGo)
    def fb(s, b):
        if s == "x1": return "x1b" if b == "xb" else "x1s"
        if s == "o1": return "o1b" if b == "ob" else "o1s"
        return s
    st2b = rasp.SequenceMap(fb, st2, BIGxo)''')
open('/work/prog_v4.py','w').write(s)
res = compile_program('/work/prog_v4.py')
print({k: v for k, v in res.items() if k != 'residual_labels'})
```