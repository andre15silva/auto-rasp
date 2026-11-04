The `sources` list contains thousands of duplicate `tokens`/`indices` entries — Tracr's graph extraction appends a source each time a leaf is reached, so the depth DFS runs (#sink→leaf paths) × (#leaf→sink paths) times. Let me read `extract_rasp_graph` to see exactly how sources are collected.

```python
import os, tracr
base = os.path.dirname(tracr.__file__)
s = open(base+'/compiler/rasp_to_graph.py').read()
i = s.find('def extract_rasp_graph'); print(s[i:i+2500])
```