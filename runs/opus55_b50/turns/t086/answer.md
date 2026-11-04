Let me instrument a copy of Tracr's DFS to count actual visits.

```python
import sys, importlib, time, collections
sys.path.insert(0, '/work')
import gonet4; importlib.reload(gonet4)
from tracr.compiler import rasp_to_graph, nodes
from tracr.rasp import rasp
import networkx as nx
sys.setrecursionlimit(100000)
for stop in ['nbinfo', 'feat']:
    prog = gonet4.build(stop=stop)
    ext = rasp_to_graph.extract_rasp_graph(prog)
    graph = ext.graph
    cnt = collections.Counter()
    def dfs(node_id, depth):
        cnt[node_id] += 1
        for s in graph.successors(node_id):
            dfs(s, depth + (1 if isinstance(graph.nodes[s][nodes.EXPR], rasp.SOp) else 0))
    t0 = time.time()
    for s in ext.sources: dfs(s[nodes.ID], 0)
    print(stop, 'sources', [s[nodes.ID] for s in ext.sources], 'visits', sum(cnt.values()), round(time.time()-t0, 1))
    print(cnt.most_common(4))
```