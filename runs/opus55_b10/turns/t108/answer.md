88.5M params (residual 1630) — a bit heavier than I'd like given the noisy speed measurements. The widest MLP (457) is the tactical table: 55 triple-classes × 8. Let me check how much simplifying the score function (dropping the tiny 0.5 "reduce 3-liberty group" term) shrinks the class count.

```python
import sys, itertools, importlib
sys.path.insert(0,'/work')
import go; importlib.reload(go)
CATS = go.CATS
def msum(a,b): return tuple(sorted(a+b))
triples = sorted({tuple(sorted(t)) for t in itertools.product(CATS, repeat=3)})
def count(fn):
    sig = {}
    for t in triples:
        sig.setdefault(tuple(fn(msum(t,(e,))) for e in CATS), []).append(t)
    return len(sig)
print('current', count(go.tactic_score))
src = open('/work/go.py').read()
import types
ns = {}
code = src[src.index('def tactic_score'):src.index('def pos_score')] if 'def pos_score' in src[src.index('def tactic_score'):] else None
code = src[src.index('def tactic_score'):src.index('LINE_OPEN')]
exec(code.replace("    if aO3 and safe: s += 0.5\n", ""), ns)
print('no red', count(ns['tactic_score']))
ns2 = {}
exec(code.replace("    if aO3 and safe: s += 0.5\n", "").replace("    if aX2 and lo >= 3: s += 2.5\n", "    if aX2 and lo >= 3: s += 2.5\n"), ns2)
print(code[:200])
```