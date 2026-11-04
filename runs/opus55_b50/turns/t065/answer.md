6.9 s per 1000 positions — a 10× speedup. Now let me add the region flags (free in the bundle) back into the scoring, then verify all features with a positions pass.

```python
s = open('/work/gonet.py').read()
s = s.replace('''def score23(e, line):
    if e == 'side': return PASS_LOGIT
    if e == 'eye': return -12.0
    return round(PRIOR[line] if line < 9 else 0.0, 2)''', '''REG = {'own': -1.5, 'opp': -1.0, 'both': 0.0, 'none': 0.0}
def score23(aux, line):
    e, rg = aux
    if e == 'side': return PASS_LOGIT
    if e == 'eye': return -12.0
    return round(REG[rg] + (PRIOR[line] if line < 9 else 0.0), 2)''')
s = s.replace("    t23c = rasp.categorical(rasp.SequenceMap(score23, eye, linec)).named('t23c')",
"""    fXc = rasp.categorical(rasp.Map(lambda v: v > 0.5, flags[NBUCK])).named('fXc')
    fOc = rasp.categorical(rasp.Map(lambda v: v > 0.5, flags[NBUCK + 1])).named('fOc')
    region = rasp.categorical(rasp.SequenceMap(lambda a, b: ('own' if a and not b else 'opp' if b and not a else 'both' if a else 'none'), fXc, fOc)).named('region')
    aux = rasp.categorical(rasp.SequenceMap(lambda e, r: (e, r), eye, region)).named('aux')
    t23c = rasp.categorical(rasp.SequenceMap(score23, aux, linec)).named('t23c')""")
open('/work/gonet.py','w').write(s)
r = compile_program()
```