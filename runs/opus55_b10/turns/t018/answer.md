```python
est_src = r'''
import collections
def estimate(prog):
    order=[]; seen=set()
    def topo(e):
        if id(e) in seen: return
        seen.add(id(e))
        for c in e.children: topo(c)
        order.append(e)
    topo(prog)
    down = collections.defaultdict(int); down[id(prog)] = 1
    for e in reversed(order):
        for c in e.children: down[id(c)] += down[id(e)]
    parents = collections.defaultdict(list)
    for e in order:
        for c in e.children: parents[id(c)].append(e)
    leaves = [e for e in order if not e.children]
    tot = 0
    for L in leaves:
        cnt = collections.defaultdict(int); cnt[id(L)] = 1
        for e in order:
            if cnt[id(e)]:
                for p in parents[id(e)]: cnt[id(p)] += cnt[id(e)]
        tot += down[id(L)] * sum(cnt.values())
    return tot, len(order)
'''
open('/work/estimate.py','w').write(est_src)
import sys; sys.path.insert(0,'/work')
import importlib, go, estimate
importlib.reload(go)
import sys
sys.setrecursionlimit(10000)
print(estimate.estimate(go.program()))
```