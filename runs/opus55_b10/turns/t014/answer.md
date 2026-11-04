```python
import sys, time
sys.path.insert(0,'/work')
import importlib, go
from tracr.rasp import rasp
prog = go.program()
memo = {}
def npaths(e):
    k = id(e)
    if k in memo: return memo[k]
    ch = e.children
    if not ch:
        v = 1
    else:
        v = sum(npaths(c) for c in ch)
    memo[k] = v
    return v
allnodes = {}
def collect(e):
    if id(e) in allnodes: return
    allnodes[id(e)] = e
    for c in e.children: collect(c)
collect(prog)
print('nodes', len(allnodes))
tot = sum(npaths(e) for e in allnodes.values())
print('paths to sink', npaths(prog), 'total dfs calls approx', tot)
# biggest
big = sorted(((npaths(e), e.label) for e in allnodes.values()), reverse=True)[:10]
print(big)
import tracr.compiler.rasp_to_graph as rg, inspect
print(inspect.getsource(rg.extract_rasp_graph)[:2500])
```