```python
import sys, time, signal, collections
sys.path.insert(0,'/work')
import go
from tracr.rasp import rasp
from tracr.compiler import rasp_to_graph, craft_graph_to_model
prog = go.program()
# count tip->node paths (extract visits) and source occurrences
memo_down = {}
order = []
seen = set()
def topo(e):
    if id(e) in seen: return
    seen.add(id(e))
    for c in e.children: topo(c)
    order.append(e)
topo(prog)
down = collections.defaultdict(int); down[id(prog)] = 1
for e in reversed(order):
    for c in e.children: down[id(c)] += down[id(e)]
leaves = [e for e in order if not e.children]
print('extract visits', sum(down.values()), 'leaf visits', {e.label: down[id(e)] for e in leaves}, flush=True)
# paths from each leaf to all nodes
parents = collections.defaultdict(list)
for e in order:
    for c in e.children: parents[id(c)].append(e)
def up_total(src):
    cnt = collections.defaultdict(int); cnt[id(src)] = 1
    for e in order:  # topological (children before parents)
        if cnt[id(e)]:
            for p in parents[id(e)]: cnt[id(p)] += cnt[id(e)]
    return sum(cnt.values())
for L in leaves:
    print(L.label, 'paths from leaf to all nodes', up_total(L), flush=True)
est = sum(down[id(L)] * up_total(L) for L in leaves)
print('estimated dfs calls if sources duplicated:', est)
print('estimated dfs calls if deduped:', sum(up_total(L) for L in leaves))
signal.alarm(120)
t0 = time.time()
ex = rasp_to_graph.extract_rasp_graph(prog)
print('extract time', time.time()-t0, 'sources', len(ex.sources), flush=True)
```