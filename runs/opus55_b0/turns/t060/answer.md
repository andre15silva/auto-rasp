```python
import sys; sys.path.insert(0,'/work')
import importlib, gotmpl10, gowin; importlib.reload(gotmpl10); importlib.reload(gowin)
g = gotmpl10
for h in "ABC":
    f = g.make_tlevel(h)
    lv = sorted(set(f(t) for t in range(82)))
    print(h, len(g.CFG[h]), lv)
# spot check: template slot for a config and its predicate maximality for exact hist
def best_slot(h, counts):
    P = g.make_tpred(h)
    # build hist masses over states consistent with counts (state -> count)
    best = None
    for k in range(82):
        sc = sum(c/4.0 * P(k, s) for s, c in counts.items())
        if best is None or sc > best[0]: best = (sc, k)
    return best[1], g.CFG[h][best[1]] if best[1] < len(g.CFG[h]) else None
print(best_slot("A", {"o1s":1, "e":2, "xn":1}))
print(best_slot("B", {"x1b":1, "e":3}))
print(best_slot("C", {"e":0, "xn":3, "edge":1}))
print(best_slot("C", {"edge":4}))
```