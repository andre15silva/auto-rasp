The depth (≈36 SOp levels) is set by long MLP-only chains (decode, post-fetch combination). The quickest big win is layer 1's two 410-wide SequenceMaps (rowE/colE over the 82-valued index), which set the padded MLP width for every layer. Let me derive them from 10-valued row/col SOps instead.

```python
s = open('/work/go.py').read()
s = s.replace("""    def rowEf(i, t):
        if i >= 81: return 'Z' if t == '.' else 'D'
        return i // 9 if t == '.' else None
    def colEf(i, t):
        if i >= 81: return 'Z' if t == '.' else 'D'
        return i % 9 if t == '.' else None
    rowE = smap(rowEf, idx, tok)
    colE = smap(colEf, idx, tok)""", """    rowv = cmap(lambda i: 'P' if i >= 81 else i // 9, idx)
    colv = cmap(lambda i: 'P' if i >= 81 else i % 9, idx)
    def rcEf(v, t):
        if v == 'P': return 'Z' if t == '.' else 'D'
        return v if t == '.' else None
    rowE = smap(rcEf, rowv, tok)
    colE = smap(rcEf, colv, tok)""")
open('/work/go.py','w').write(s)
import sys; sys.path.insert(0,'/work'); sys.setrecursionlimit(10000)
import importlib, go, estimate
importlib.reload(go)
print(estimate.estimate(go.program()))
r = compile_program()
print({k:v for k,v in r.items() if k!='residual_labels'})
```